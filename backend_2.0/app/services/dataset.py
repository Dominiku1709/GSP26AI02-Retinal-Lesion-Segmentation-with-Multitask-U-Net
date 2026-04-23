import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import albumentations as A
import cv2
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler


# --- Augmentation ---

def get_training_augmentation(image_size: int = 512) -> A.Compose:
    return A.Compose([
        A.HorizontalFlip(p=0.5),
        A.Affine(
            translate_percent={'x': (-0.06, 0.06), 'y': (-0.04, 0.04)},
            scale=(0.92, 1.08),
            rotate=(-12, 12),
            p=0.5,
        ),
        A.ElasticTransform(alpha=0.5, sigma=60, p=0.3),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
        A.RandomGamma(gamma_limit=(80, 120), p=0.3),
        A.RandomToneCurve(scale=0.12, p=0.25),
        A.OneOf([
            A.GaussNoise(std_range=(0.01, 0.05)),
            A.MultiplicativeNoise(multiplier=(0.85, 1.15), p=1.0),
        ], p=0.4),
        A.OneOf([
            A.GaussianBlur(blur_limit=(3, 5), p=1.0),
            A.MedianBlur(blur_limit=3, p=1.0),
        ], p=0.25),
        A.CLAHE(clip_limit=2.5, tile_grid_size=(8, 8), p=0.35),
        A.CoarseDropout(max_holes=8, max_height=12, max_width=12, fill_value=0, p=0.4),
    ])


def get_finetune_augmentation(image_size: int = 512) -> A.Compose:
    return A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(brightness_limit=0.1, contrast_limit=0.1, p=0.4),
        A.CLAHE(clip_limit=2.0, tile_grid_size=(8, 8), p=0.3),
    ])


def get_validation_augmentation() -> A.Compose:
    return A.Compose([])


def get_preprocessing(image_size: int = 512) -> A.Compose:
    return A.Compose([
        A.LongestMaxSize(max_size=image_size, interpolation=cv2.INTER_LINEAR),
        A.PadIfNeeded(
            min_height=image_size,
            min_width=image_size,
            border_mode=cv2.BORDER_CONSTANT,
            value=0.0,
        ),
        A.Normalize(
            mean=[0.5, 0.5, 0.5],
            std=[0.5, 0.5, 0.5],
            max_pixel_value=255.0, 
)
    ])


# --- Dataset ---

class OCTMultiTaskDataset(Dataset):
    VALID_LABELS = {0, 1, 2, 3}
    LABEL_NAMES  = {0: "NORMAL", 1: "AMD", 2: "DME", 3: "Lesion"}

    def __init__(
        self,
        metadata_path: str,
        augmentation: Optional[A.Compose] = None,
        preprocessing: Optional[A.Compose] = None,
        debug: bool = False,
        validate_files: bool = False,
        first_batch_debug: bool = False,
    ):
        with open(metadata_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self.augmentation      = augmentation
        self.preprocessing     = preprocessing
        self.debug             = debug
        self.first_batch_debug = first_batch_debug
        self._debug_done       = False

        self.samples = self._sanitize_samples(raw, metadata_path)

        if validate_files:
            self._validate_file_existence()

        self._print_stats(metadata_path)

    def _sanitize_samples(self, raw: List[Dict], path: str) -> List[Dict]:
        clean = []
        label_issues = []
        for i, s in enumerate(raw):
            lbl = s.get("class_label", -99)
            if lbl not in self.VALID_LABELS:
                label_issues.append((i, lbl))
                s = {**s, "class_label": 3}
            clean.append(s)

        if label_issues:
            print(f"Warning: Found {len(label_issues)} samples with invalid labels in {Path(path).name}. Remapped to 3 (Lesion).")
        return clean

    def _validate_file_existence(self):
        missing = []
        for s in self.samples:
            if not Path(s["image_path"]).exists():
                missing.append(s["image_path"])
            if s.get("has_mask") and s.get("mask_path"):
                if not Path(s["mask_path"]).exists():
                    missing.append(s["mask_path"])
        if missing:
            msg = f"Missing {len(missing)} files:\n" + "\n".join(missing[:10])
            raise FileNotFoundError(msg)
        print(f"File validation passed for {len(self.samples)} samples.")

    def _print_stats(self, path: str):
        print(f"Loaded {len(self.samples)} samples from {Path(path).name}")
        label_counts = Counter(s["class_label"] for s in self.samples)
        for lbl in sorted(label_counts):
            name = self.LABEL_NAMES.get(lbl, f"label={lbl}")
            pct  = label_counts[lbl] / len(self.samples) * 100
            print(f"  {name:<10}: {label_counts[lbl]:>5} ({pct:.1f}%)")
        
        n_mask = sum(1 for s in self.samples if s.get("has_mask"))
        print(f"  With mask : {n_mask:>5} ({n_mask/len(self.samples)*100:.1f}%)")

    def __len__(self) -> int:
        return len(self.samples)

    @staticmethod
    def _load_image(path: str) -> np.ndarray:
        p = Path(path)
        if p.suffix == ".npy":
            img = np.load(path, allow_pickle=False).astype(np.float32)
        else:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise IOError(f"Cannot read image: {path}")
            img = img.astype(np.float32)

        if img.ndim == 3:
            img = img[:, :, 0]

        if img.max() > 1.1:
            img = img / 255.0

        return np.clip(img, 0.0, 1.0)

    @staticmethod
    def _load_mask(path: str, image_shape: Tuple[int, int]) -> np.ndarray:
        p = Path(path)
        if p.suffix == ".npy":
            mask = np.load(path, allow_pickle=False).astype(np.float32)
        else:
            mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if mask is None:
                return np.zeros(image_shape, dtype=np.float32)
            mask = mask.astype(np.float32)

        if mask.ndim == 3:
            mask = mask[:, :, 0]
        if mask.max() > 1.1:
            mask = mask / 255.0
        return (mask > 0.5).astype(np.float32)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        s = self.samples[idx]

        image = self._load_image(s["image_path"])

        if s.get("has_mask") and s.get("mask_path") and Path(s["mask_path"]).exists():
            mask = self._load_mask(s["mask_path"], image.shape[:2])
        else:
            mask = np.zeros(image.shape[:2], dtype=np.float32)

        image_3ch = np.stack([image, image, image], axis=-1)

        if self.augmentation is not None:
            try:
                aug = self.augmentation(image=image_3ch, mask=mask)
                image_3ch = aug["image"]
                mask      = aug["mask"]
            except Exception as e:
                if self.debug:
                    print(f"Augmentation warning at idx={idx}: {e}")

        if self.preprocessing is not None:
            pre = self.preprocessing(image=image_3ch, mask=mask)
            image_3ch = pre["image"]
            mask      = pre["mask"]

        if self.first_batch_debug and not self._debug_done:
            ch0 = image_3ch[:, :, 0]
            print(f"Preprocessing check - First batch info:")
            print(f"  Channel-0: min={ch0.min():.4f}, max={ch0.max():.4f}, mean={ch0.mean():.4f}")
            if ch0.max() > 2.0 or ch0.min() < -2.0:
                print("  Warning: Pixel values are outside expected [-1, 1] range.")
            self._debug_done = True

        image_tensor = torch.from_numpy(image_3ch[:, :, 0].astype(np.float32)).unsqueeze(0)
        mask_tensor = torch.from_numpy((mask > 0.5).astype(np.float32))

        label     = int(s["class_label"])
        has_mask  = bool(s.get("has_mask", False))

        return {
            "image":    image_tensor,
            "mask":     mask_tensor,
            "label":    torch.tensor(label, dtype=torch.long),
            "has_mask": torch.tensor(has_mask, dtype=torch.bool),
            "dataset":  s.get("dataset", "unknown"),
        }


# --- Sampler & Mixup ---

def get_sample_weights(dataset: OCTMultiTaskDataset) -> torch.DoubleTensor:
    samples = dataset.samples
    total   = len(samples)
    label_counts = Counter(s["class_label"] for s in samples)

    freq_w = {lbl: min(total / cnt, 6.0) for lbl, cnt in label_counts.items()}

    weights = [
        freq_w.get(s["class_label"], 1.0) * (1.5 if s.get("has_mask") else 1.0)
        for s in samples
    ]
    wt = torch.DoubleTensor(weights)
    return wt

def mixup_batch(
    images:   torch.Tensor,
    masks:    torch.Tensor,
    labels:   torch.Tensor,
    has_mask: torch.Tensor,
    alpha:    float = 0.2,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, float, torch.Tensor]:
    lam   = float(np.random.beta(alpha, alpha))
    lam   = max(lam, 1.0 - lam)
    index = torch.randperm(images.size(0), device=images.device)
    
    return (
        lam * images + (1 - lam) * images[index],
        lam * masks  + (1 - lam) * masks[index],
        labels,
        labels[index],
        lam,
        has_mask | has_mask[index],
    )


# --- Factory ---

def create_dataloaders(
    train_metadata:      str,
    val_metadata:        str,
    batch_size:          int   = 4,
    num_workers:         int   = 4,
    image_size:          int   = 512,
    use_augmentation:    bool  = True,
    use_weighted_sampler: bool = True,
    seg_threshold:       float = 0.35,
    validate_files:      bool  = False,
    debug:               bool  = False,
) -> Tuple[DataLoader, DataLoader]:

    train_aug     = get_training_augmentation(image_size) if use_augmentation else None
    val_aug       = get_validation_augmentation()
    preprocessing = get_preprocessing(image_size)

    train_ds = OCTMultiTaskDataset(
        metadata_path    = train_metadata,
        augmentation     = train_aug,
        preprocessing    = preprocessing,
        debug            = debug,
        validate_files   = validate_files,
        first_batch_debug= True,
    )
    
    val_ds = OCTMultiTaskDataset(
        metadata_path    = val_metadata,
        augmentation     = val_aug,
        preprocessing    = preprocessing,
        debug            = debug,
        validate_files   = validate_files,
        first_batch_debug= True,
    )

    if use_weighted_sampler:
        train_weights = get_sample_weights(train_ds)
        sampler = WeightedRandomSampler(
            weights=train_weights,
            num_samples=len(train_ds),
            replacement=True,
        )
        train_loader = DataLoader(
            train_ds, batch_size=batch_size, sampler=sampler,
            num_workers=num_workers, pin_memory=True, drop_last=True,
        )
    else:
        train_loader = DataLoader(
            train_ds, batch_size=batch_size, shuffle=True,
            num_workers=num_workers, pin_memory=True, drop_last=True,
        )

    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True, drop_last=False,
    )

    return train_loader, val_loader