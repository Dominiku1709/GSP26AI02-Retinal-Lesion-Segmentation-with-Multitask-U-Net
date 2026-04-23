import os
import sys
import logging
import importlib
import numpy as np
import cv2
import torch
import torch.nn.functional as F
import base64
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# --- CẤU HÌNH ĐƯỜNG DẪN TUYỆT ĐỐI ---
# File này tại: backend_2.0/app/services/inference.py
CURRENT_FILE = Path(__file__).resolve()
# Gốc dự án: backend_2.0/
ROOT_DIR = CURRENT_FILE.parent.parent.parent 
# Thư mục chứa model: backend_2.0/weights/
WEIGHTS_DIR = ROOT_DIR / "weights"

# Thêm dự án vào sys.path để import model_architecture
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Đảm bảo thư mục weights tồn tại
if not WEIGHTS_DIR.exists():
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    logger.warning(f"Thư mục weights không tồn tại, đã tạo mới tại: {WEIGHTS_DIR}")

# Cấu hình Model
LABELS = ["Normal", "AMD", "DME", "Lesion"]
IMAGE_SIZE = 512

ARCH_REGISTRY = {
    "vanilla": {
        "module": "model_architecture.model_architecture", 
        "class": "VanillaMultitaskUNet",
        "weight_path": "Vanilla.pth", # Chỉ cần tên file
        "params": {"in_channels": 1, "num_classes": 4, "num_seg_classes": 1, "dropout_rate": 0.3}
    },
    "resnet_unet": {
        "module": "model_architecture.model_architecture",
        "class": "ResNet50MultiTaskUNet",
        "weight_path": "Resnet50.pth",
        "params": {"in_channels": 1, "num_classes": 4, "num_seg_classes": 1, "dropout_rate": 0.3}
    },
    "effb3_unet": {
        "module": "model_architecture.model_architecture",
        "class": "ImprovedOctMultiTaskUNet",
        "weight_path": "effb3.pth",
        "params": {"in_channels": 1, "num_classes": 4, "num_seg_classes": 1, "dropout_rate": 0.3}
    },
    "unetplusplus": {
        "module": "model_architecture.model_architecture",
        "class": "UNetPlusPlusMultiTask",
        "weight_path": "Unet.pth",
        "params": {"in_channels": 1, "num_classes": 4, "num_seg_classes": 1, "dropout_rate": 0.3}
    }
}

# --- HELPER FUNCTIONS ---

def postprocess_pred_mask(pred_mask: np.ndarray, min_component_area: int = 80) -> np.ndarray:
    """Lọc nhiễu đốm nhỏ và làm sạch mask"""
    mask = pred_mask.astype(np.uint8).copy()
    if not mask.any(): return mask
    
    # Đóng các lỗ nhỏ
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Lọc theo diện tích
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    clean = np.zeros_like(mask)
    for lab in range(1, n_labels):
        if int(stats[lab, cv2.CC_STAT_AREA]) >= min_component_area:
            clean[labels == lab] = 1
    return clean

def preprocess_image(img):
    """Tiền xử lý: Resize giữ tỷ lệ + Padding"""
    img = np.array(img)
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    img = img.astype(np.float32)
    h, w = img.shape
    scale = IMAGE_SIZE / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    img_padded = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.float32)
    pad_y, pad_x = (IMAGE_SIZE - new_h) // 2, (IMAGE_SIZE - new_w) // 2
    img_padded[pad_y:pad_y+new_h, pad_x:pad_x+new_w] = img_resized
    
    if img_padded.max() > 1.0: img_padded /= 255.0
    tensor = torch.from_numpy(img_padded).unsqueeze(0).unsqueeze(0).float()
    return tensor, pad_x, pad_y, new_w, new_h

class InferenceService:
    def __init__(self, arch_type: str = "unetplusplus",use_tta: bool = False):
        self.arch_type = arch_type
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.model_path = ""
        self.is_mock = True
        self.use_tta = use_tta
        # Tự động nạp model mặc định
        self.set_model_by_arch(arch_type)

    def _load_model(self, arch_info: dict, full_path: Path) -> Any:
        try:
            module = importlib.import_module(arch_info["module"])
            model_class = getattr(module, arch_info["class"])
            model = model_class(**arch_info["params"])
            checkpoint = torch.load(full_path, map_location=self.device)
            state_dict = checkpoint.get("model_state_dict", checkpoint.get("state_dict", checkpoint))
            model.load_state_dict(state_dict, strict=False)
            logger.info(f"Successfully loaded model: {full_path.name}")
            return model.to(self.device).eval()
        except Exception as e:
            logger.error(f"Error loading model {full_path}: {e}")
            return None

    def list_models(self) -> List[str]:
        """Trả về danh sách file model trong thư mục weights/"""
        if not WEIGHTS_DIR.exists(): return []
        return sorted([f for f in os.listdir(WEIGHTS_DIR) if f.endswith(('.pth', '.pt'))])

    def set_model(self, model_name: str):
        """Đổi model dựa trên tên file cụ thể"""
        target_path = WEIGHTS_DIR / model_name
        if not target_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file {model_name} tại {WEIGHTS_DIR}")
        
        # Tìm kiến trúc phù hợp dựa trên tên file trong Registry
        found_arch = "vanilla"
        for arch_key, info in ARCH_REGISTRY.items():
            if info["weight_path"] == model_name:
                found_arch = arch_key
                break
        
        self.arch_type = found_arch
        self.model_path = str(target_path)
        self.model = self._load_model(ARCH_REGISTRY[found_arch], target_path)
        self.is_mock = self.model is None

    def set_model_by_arch(self, arch_type: str):
        """Nạp model dựa trên key kiến trúc (vanilla, resnet_unet,...)"""
        info = ARCH_REGISTRY.get(arch_type, ARCH_REGISTRY["vanilla"])
        full_path = WEIGHTS_DIR / info["weight_path"]
        if full_path.exists():
            self.model = self._load_model(info, full_path)
            self.model_path = str(full_path)
            self.is_mock = False
        else:
            logger.warning(f"File mặc định {full_path} không tồn tại.")

    def get_gpu_status(self) -> dict:
        return {
            "device": self.device, 
            "model_loaded": self.model is not None, 
            "selected_model": os.path.basename(self.model_path) if self.model_path else "None"
        }

    @property
    def selected_model(self) -> str:
        return os.path.basename(self.model_path) if self.model_path else "None"

    def visualize_result(self, image: np.ndarray, mask: np.ndarray) -> str:
        """Vẽ overlay mask màu đỏ lên ảnh gốc và encode base64"""
        if image.ndim == 2:
            canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            canvas = image.copy()

        if mask.any():
            # Vẽ vùng phủ màu đỏ mờ
            overlay = canvas.copy()
            overlay[mask > 0] = (0, 0, 255)
            canvas = cv2.addWeighted(canvas, 0.75, overlay, 0.25, 0)
            # Vẽ viền đỏ đậm sắc nét
            edge = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
            canvas[edge > 0] = (0, 0, 255)

        _, buffer = cv2.imencode('.jpg', canvas)
        return base64.b64encode(buffer).decode('utf-8')

    @torch.no_grad()
    def predict(self, input_data: Any) -> dict:
        if self.is_mock or self.model is None:
            return self._mock_predict()

        try:
            # 1. Chuyển đổi đầu vào thành uint8
            img_uint8 = np.array(input_data[1] if isinstance(input_data, tuple) else input_data)
            if img_uint8.max() <= 1.1: img_uint8 = (img_uint8 * 255).astype(np.uint8)
            orig_h, orig_w = img_uint8.shape[:2]

            # 2. Tiền xử lý
            image_tensor, px, py, nw, nh = preprocess_image(img_uint8)
            image_tensor = image_tensor.to(self.device)

            # 3. Chạy model
            outputs = self.model(image_tensor)
            
            # 4. Xử lý Classification
            cls_probs = F.softmax(outputs['cls_output'], dim=1).cpu().numpy()[0]
            cls_idx = np.argmax(cls_probs)
            
            # 5. Xử lý Segmentation (Un-padding + Resize)
            seg_logits = outputs.get('seg_logits', outputs.get('seg_output'))
            seg_probs = torch.sigmoid(seg_logits).cpu().numpy()[0, 0]
            
            # Cắt phần hợp lệ và resize về gốc
            seg_valid = seg_probs[py:py+nh, px:px+nw]
            mask_resized = cv2.resize(seg_valid, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
            
            # Lọc nhiễu mask
            final_mask_bin = postprocess_pred_mask((mask_resized > 0.5).astype(np.uint8))
            # ─────────────── DEBUG LINE ───────────────
            # cv2.connectedComponents trả về (số lượng nhãn, bản đồ nhãn)
            # Chúng ta trừ 1 vì nhãn 0 luôn là nền (background)
            num_labels, _ = cv2.connectedComponents(final_mask_bin)
            detected_masks_count = max(0, num_labels - 1)
            print(f"--- [DEBUG INFERENCE] Model: {self.arch_type} | Số lượng mask (vùng tổn thương) tạo ra: {detected_masks_count} ---")
            # ──────────────────────────────────────────

            # 6. Tạo Visualization
            mask_viz_b64 = self.visualize_result(img_uint8, final_mask_bin)

            return {
                "label": LABELS[cls_idx],
                "confidence": round(float(cls_probs[cls_idx]), 4),
                "mask_viz": mask_viz_b64,
                "architecture": self.arch_type,
                "objects_found": int(cv2.connectedComponents(final_mask_bin)[0] - 1)
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._mock_predict(str(e))

    def _mock_predict(self, error_msg: str = "Model not loaded"):
        return {"status": "error", "error_msg": error_msg, "label": "Error", "confidence": 0.0, "mask_viz": "", "architecture": "none"}

# Khởi tạo instance cho toàn bộ ứng dụng
model_runner = InferenceService(use_tta=True)