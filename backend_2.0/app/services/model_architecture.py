import numpy as np
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score, classification_report, roc_auc_score
from scipy.ndimage import distance_transform_edt, binary_erosion
import warnings

warnings.filterwarnings('ignore', category=RuntimeWarning)


def compute_hd95_scipy(pred_mask, true_mask, spacing=(1.0, 1.0)):
    pred = np.asarray(pred_mask).astype(bool)
    true = np.asarray(true_mask).astype(bool)
    
    if np.sum(pred) == 0 and np.sum(true) == 0:
        return 0.0
    if np.sum(pred) == 0 or np.sum(true) == 0:
        return np.nan
        
    pred_border = pred ^ binary_erosion(pred)
    true_border = true ^ binary_erosion(true)
    
    dt_pred = distance_transform_edt(~pred_border, sampling=spacing)
    dt_true = distance_transform_edt(~true_border, sampling=spacing)
    
    dist_pred_to_true = dt_true[pred_border]
    dist_true_to_pred = dt_pred[true_border]
    
    all_distances = np.concatenate([dist_pred_to_true, dist_true_to_pred])
    if len(all_distances) == 0:
        return 0.0
        
    return np.percentile(all_distances, 95)


class AverageMeter:
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


class MultiTaskMetrics:
    def __init__(self,
                 num_classes: int = 3,
                 num_seg_classes: int = 1,
                 class_names=None,
                 seg_threshold: float = 0.35):
        self.num_classes     = num_classes
        self.num_seg_classes = num_seg_classes
        self.class_names     = class_names or [f'Class_{i}' for i in range(num_classes)]
        self.seg_threshold   = seg_threshold
        self.reset()

    def reset(self):
        self.seg_tp = 0
        self.seg_fp = 0
        self.seg_fn = 0
        self.hd95_list = []
        self.cls_preds   = []
        self.cls_targets = []
        self.cls_probs   = []

    def compute_dice(self, pred_logits, target, smooth=1e-5):
        pred   = torch.sigmoid(pred_logits).squeeze(1)
        target = target.float()
        
        if target.sum() == 0:
            return torch.tensor(0.0, device=pred_logits.device)
            
        intersection = (pred * target).sum()
        union = pred.sum() + target.sum()
        dice = (2 * intersection + smooth) / (union + smooth)
        
        return torch.clamp(dice, min=0.0, max=1.0)

    def update(self, seg_pred, seg_target, cls_pred, cls_target, has_mask=None):
        # --- Segmentation ---
        if has_mask is not None:
            mask_bool = has_mask.bool()
            if mask_bool.sum() > 0:
                valid_seg_pred = seg_pred[mask_bool]
                valid_target   = seg_target[mask_bool].float()

                if valid_seg_pred.dim() == 4:
                    if valid_seg_pred.shape[1] == 1:
                        valid_seg_pred = valid_seg_pred.squeeze(1)
                    elif valid_seg_pred.shape[1] > 1:
                        valid_seg_pred = valid_seg_pred[:, 1, :, :]

                pred_prob = torch.sigmoid(valid_seg_pred)
                pred_bin = (pred_prob > self.seg_threshold).float()

                self.seg_tp += (pred_bin * valid_target).sum().item()
                self.seg_fp += (pred_bin * (1 - valid_target)).sum().item()
                self.seg_fn += ((1 - pred_bin) * valid_target).sum().item()

                if not seg_pred.requires_grad:
                    for i in range(pred_bin.size(0)):
                        p_mask = pred_bin[i].cpu().numpy()
                        t_mask = valid_target[i].cpu().numpy()
                        hd = compute_hd95_scipy(p_mask, t_mask)
                        if not np.isnan(hd):
                            self.hd95_list.append(hd)

        # --- Classification ---
        if cls_pred is not None and cls_target is not None:
            valid_cls_mask = (cls_target != -1)
            if valid_cls_mask.sum() > 0:
                valid_pred   = cls_pred[valid_cls_mask]
                valid_target = cls_target[valid_cls_mask]
                pred_labels  = torch.argmax(valid_pred, dim=1)
                probs        = torch.softmax(valid_pred, dim=1)
                
                self.cls_preds.extend(pred_labels.cpu().numpy())
                self.cls_targets.extend(valid_target.cpu().numpy())
                self.cls_probs.extend(probs.detach().cpu().numpy().tolist())

    def compute(self):
        # --- Segmentation Compute ---
        denom_dice = 2 * self.seg_tp + self.seg_fp + self.seg_fn
        dice       = (2 * self.seg_tp) / denom_dice if denom_dice > 0 else 0.0
        iou        = dice / (2 - dice + 1e-7) if dice > 0 else 0.0
        precision  = self.seg_tp / (self.seg_tp + self.seg_fp + 1e-7)
        recall     = self.seg_tp / (self.seg_tp + self.seg_fn + 1e-7)
        mean_hd95  = np.mean(self.hd95_list) if len(self.hd95_list) > 0 else 0.0

        # --- Classification Compute ---
        if len(self.cls_targets) > 0:
            y_true  = np.array(self.cls_targets)
            y_pred  = np.array(self.cls_preds)
            y_probs = np.array(self.cls_probs)

            cm       = confusion_matrix(y_true, y_pred, labels=range(self.num_classes))
            f1       = f1_score(y_true, y_pred, average='macro', zero_division=0)
            accuracy = accuracy_score(y_true, y_pred)

            specificity_list = []
            for i in range(self.num_classes):
                tn = np.sum(cm) - (np.sum(cm[i, :]) + np.sum(cm[:, i]) - cm[i, i])
                fp = np.sum(cm[:, i]) - cm[i, i]
                spec = tn / (tn + fp + 1e-7)
                specificity_list.append(spec)
            mean_specificity = np.mean(specificity_list)

            try:
                y_probs    = np.nan_to_num(y_probs)
                auc_score  = roc_auc_score(
                    y_true, y_probs,
                    multi_class='ovr', average='macro',
                    labels=list(range(self.num_classes))
                )
            except Exception:
                auc_score = 0.0
        else:
            cm = np.zeros((self.num_classes, self.num_classes))
            f1 = accuracy = mean_specificity = auc_score = 0.0
            precision = recall = 0.0

        return {
            'segmentation': {
                'dice':      dice,
                'iou':       iou,
                'precision': precision,
                'recall':    recall,
                'hd95':      mean_hd95,
            },
            'classification': {
                'accuracy':         accuracy,
                'f1_macro':         f1,
                'mean_specificity': mean_specificity,
                'auc':              auc_score,
                'confusion_matrix': cm,
            }
        }

    def print_results(self):
        results = self.compute()
        
        print("\n--- Evaluation Results ---")
        print(f"Segmentation Threshold: {self.seg_threshold}")
        
        print("\nSegmentation Metrics:")
        print(f"  Dice Score      : {results['segmentation']['dice']:.4f}")
        print(f"  IoU             : {results['segmentation']['iou']:.4f}")
        print(f"  Precision       : {results['segmentation']['precision']:.4f}")
        print(f"  Recall          : {results['segmentation']['recall']:.4f}")
        if results['segmentation']['hd95'] > 0:
            print(f"  HD95            : {results['segmentation']['hd95']:.2f} px")

        print("\nClassification Metrics:")
        print(f"  Accuracy        : {results['classification']['accuracy']:.4f}")
        print(f"  F1-Macro        : {results['classification']['f1_macro']:.4f}")
        print(f"  Mean Specificity: {results['classification']['mean_specificity']:.4f}")
        if 'auc' in results['classification']:
            print(f"  Macro-AUC       : {results['classification']['auc']:.4f}")

        if len(self.cls_targets) > 0:
            print("\nClassification Report:")
            print(classification_report(
                self.cls_targets, self.cls_preds,
                target_names=self.class_names, zero_division=0
            ))
        print("--------------------------\n")


def plot_confusion_matrix(cm, class_names, save_path=None):
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def plot_metrics_history(history, save_path=None):
    epochs = range(len(history['train_loss']))
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    axes[0].plot(epochs, history['train_loss'], label='Train Loss')
    axes[0].plot(epochs, history['val_loss'], label='Val Loss')
    axes[0].set_title('Loss')
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(epochs, history['train_dice'], label='Train Dice')
    axes[1].plot(epochs, history['val_dice'], label='Val Dice')
    axes[1].set_title('Segmentation Dice')
    axes[1].legend()
    axes[1].grid(True)

    axes[2].plot(epochs, history['train_acc'], label='Train Acc')
    axes[2].plot(epochs, history['val_acc'], label='Val Acc')
    axes[2].set_title('Classification Accuracy')
    axes[2].legend()
    axes[2].grid(True)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()