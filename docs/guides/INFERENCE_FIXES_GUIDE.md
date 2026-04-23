"""
KIỂM TRA VÀ SỬA CHỮA GUIDE: InferenceService cho OCT Grayscale

STATUS: File inference.py hiện tại cần sửa ở 4 điểm chính
"""

# ============================================================
# ĐIỂM 1: ARCH_REGISTRY - in_channels phải là 1 cho TẤT CẢ models
# ============================================================

# ✗ TRƯỚC (SAI):
effb3_unet: {
    "class": "AnyBackboneMultiTaskUNet",          # ← SAI class name!
    "num_seg_classes": 1,  # ← SAI! Phải là 2
}

# ✓ SAU (ĐÚNG):
effb3_unet: {
    "class": "ResNet50MultiTaskUNet",  # ← ĐÚNG
    "num_seg_classes": 2,              # ← ĐÚNG
}

# Thêm một entry mới cho effb3_architecture:
effb3_architecture: {
    "module": "model_architecture.effb3_architecture",
    "class": "AnyBackboneMultiTaskUNet",
    "weight_path": os.getenv("EFFB3_ARCH_WEIGHT_PATH", "weights/effb3_arch.pth"),
    "params": {
        "encoder_name": "efficientnet-b3",
        "in_channels": 1,
        "num_classes": 3,
        "num_seg_classes": 2,
        "dropout_rate": 0.3
    }
}


# ============================================================
# ĐIỂM 2: THÊM Grayscale Preprocessing Function
# ============================================================

# Thêm sau ARCH_REGISTRY:
def normalize_grayscale(img: np.ndarray, mean: float = 0.485, std: float = 0.229) -> torch.Tensor:
    """
    Chuẩn hóa ảnh grayscale sang tensor (B, 1, H, W).
    - Giữ nguyên 1 kênh (không stack RGB)
    - Normalize với mean=0.485, std=0.229
    """
    try:
        img = np.array(img, dtype=np.float32)
        
        # Xử lý dimension - Đưa về 2D (H, W)
        if img.ndim == 3:
            if img.shape[0] in [1, 3] and img.shape[0] < img.shape[1]:
                # Format (C, H, W)
                if img.shape[0] == 1:
                    img = img[0]
                else:
                    img = np.dot(img, [0.299, 0.587, 0.114])
            elif img.shape[2] in [1, 3]:
                # Format (H, W, C)
                if img.shape[2] == 1:
                    img = img[..., 0]
                else:
                    img = np.dot(img[..., :3], [0.299, 0.587, 0.114])
        
        # Normalize pixel values đến [0, 1]
        if img.max() > 1.1:
            img = img / 255.0
        else:
            img = np.clip(img, 0, 1)
        
        # Normalize với grayscale statistics
        img = (img - mean) / (std + 1e-8)
        
        # Convert to tensor (B, 1, H, W)
        tensor = torch.from_numpy(img).float()
        tensor = tensor.unsqueeze(0).unsqueeze(0)  # Add batch & channel dims
        
        return tensor
    except Exception as e:
        logger.error(f"Grayscale normalization error: {e}")
        raise


def extract_segmentation_mask(seg_output: torch.Tensor, original_shape: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Xử lý flexible segmentation output:
    - 1 channel: Sigmoid
    - 2 channels: Softmax lấy channel 1 (lesion class)
    
    Returns:
        - mask_prob: Probability map (H, W) in [0, 1]
        - mask_clean: Binary mask after morphological filtering
    """
    try:
        # Remove batch dimension
        if seg_output.dim() == 4:
            seg_output = seg_output[0]
        
        # Extract based on channel count
        if seg_output.shape[0] == 1:
            # Single channel - use Sigmoid
            mask_prob = torch.sigmoid(seg_output[0]).cpu().detach().numpy()
        elif seg_output.shape[0] == 2:
            # Two channels - use Softmax, take lesion class (channel 1)
            seg_soft = F.softmax(seg_output, dim=0)
            mask_prob = seg_soft[1].cpu().detach().numpy()
        else:
            logger.warning(f"Unexpected seg channels: {seg_output.shape[0]}")
            mask_prob = torch.sigmoid(seg_output[0]).cpu().detach().numpy()
        
        # Convert to uint8
        mask_uint8 = (np.clip(mask_prob, 0, 1) * 255).astype(np.uint8)
        
        # Resize to original shape
        if mask_uint8.shape != original_shape:
            mask_uint8 = cv2.resize(mask_uint8, (original_shape[1], original_shape[0]), interpolation=cv2.INTER_LINEAR)
        
        # Thresholding
        _, mask_binary = cv2.threshold(mask_uint8, 1, 255, cv2.THRESH_BINARY)
        
        # Morphological filtering
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask_clean = cv2.morphologyEx(mask_binary, cv2.MORPH_OPEN, kernel)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel)
        
        return mask_prob, mask_clean
    except Exception as e:
        logger.error(f"Segmentation extraction error: {e}")
        raise


# ============================================================
# ĐIỂM 3: SỬA _predict_tta() để support single-channel
# ============================================================

# ✗ TRƯỚC (SAI):
def _predict_tta(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
    if x.ndim != 4:
        logger.warning(f"⚠️ TTA: Expected 4D tensor, got {x.ndim}D. Skipping TTA.")
        return self.model(x)
    
    try:
        out1 = self.model(x)  # ← Không có torch.no_grad()!
        x_flip = torch.flip(x, dims=[3])
        out2 = self.model(x_flip)  # ← Không có torch.no_grad()!
        # ...

# ✓ SAU (ĐÚNG):
def _predict_tta(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
    """Test-Time Augmentation: Average predictions from original + flipped"""
    if x.ndim != 4 or x.shape[1] != 1:  # ← Kiểm tra channel
        logger.warning(f"TTA: Expected (B, 1, H, W), got {x.shape}. Skipping TTA.")
        return self.model(x)
    
    try:
        with torch.no_grad():
            out1 = self.model(x)
            x_flip = torch.flip(x, dims=[3])
            out2 = self.model(x_flip)
        
        # Extract segmentation outputs
        s_out1 = out1.get("seg_output", out1.get("seg_logits"))
        s_out2 = out2.get("seg_output", out2.get("seg_logits"))
        
        if s_out1 is None or s_out2 is None:
            logger.warning("TTA: Segmentation output not found. Using original.")
            return out1
        
        # Flip back seg2
        s_out2_flipped = torch.flip(s_out2, dims=[3])
        
        return {
            "cls_output": (out1.get("cls_output", torch.zeros(1)) + out2.get("cls_output", torch.zeros(1))) / 2.0,
            "seg_output": (s_out1 + s_out2_flipped) / 2.0
        }
    except Exception as e:
        logger.warning(f"TTA failed: {e}. Using single prediction.")
        with torch.no_grad():
            return self.model(x)


# ============================================================
# ĐIỂM 4: SỬA predict() method
# ============================================================

# ✗ TRƯỚC (SAI):
def predict(self, input_data: Any) -> dict:
    # ...
    img_norm = (img_uint8.astype(np.float32) / 255.0 - 0.485) / 0.229
    tensor = torch.from_numpy(img_norm).unsqueeze(0).unsqueeze(0).float().to(self.device)
    # ← Manual normalization, không linh hoạt!
    
    # ...
    lesion_map = s_out[0, 1] if s_out.shape[1] > 1 else s_out[0, 0]
    mask_prob = torch.sigmoid(lesion_map).cpu().numpy()
    # ← Không xử lý Softmax case!

# ✓ SAU (ĐÚNG):
def predict(self, input_data: Any) -> dict:
    if self.is_mock or self.model is None: 
        return self._mock_predict()
    
    try:
        # 1. PREPROCESSING: Chuẩn hóa grayscale
        if isinstance(input_data, tuple) and len(input_data) == 2:
            tensor, img_raw = input_data
            if not torch.is_tensor(tensor):
                tensor = normalize_grayscale(tensor).to(self.device)
            else:
                tensor = tensor.to(self.device)
            img_uint8 = np.array(img_raw, dtype=np.uint8)
        else:
            img_raw = np.array(input_data, dtype=np.uint8)
            # Handle different input formats
            if img_raw.ndim == 3 and img_raw.shape[0] in [1, 3]:
                img_uint8 = img_raw[0] if img_raw.shape[0] == 1 else cv2.cvtColor(np.transpose(img_raw, (1,2,0)), cv2.COLOR_RGB2GRAY)
            elif img_raw.ndim == 3:
                img_uint8 = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
            else:
                img_uint8 = img_raw
            
            tensor = normalize_grayscale(img_uint8).to(self.device)
        
        original_shape = img_uint8.shape

        # 2. INFERENCE
        with torch.no_grad():
            outputs = self._predict_tta(tensor) if self.use_tta else self.model(tensor)
            
            # Classification
            c_out = outputs.get("cls_output")
            if c_out is None:
                raise ValueError("No classification output")
            probs = F.softmax(c_out, dim=1).cpu().numpy()[0]
            idx = np.argmax(probs)
            
            # Segmentation - use flexible handler
            s_out = outputs.get("seg_output", outputs.get("seg_logits"))
            if s_out is None:
                raise ValueError("No segmentation output")
            
            mask_prob, mask_clean = extract_segmentation_mask(s_out, original_shape)
            mask_prob = np.nan_to_num(mask_prob)

        # 3. VISUALIZATION: JET Heatmap + Contours
        mask_viz_b64 = ""
        try:
            bg_rgb = cv2.cvtColor(img_uint8, cv2.COLOR_GRAY2RGB)
            h, w = bg_rgb.shape[:2]
            mask_255 = (np.clip(mask_prob, 0, 1) * 255).astype(np.uint8)
            
            # Ensure size matches
            if mask_255.shape != (h, w):
                mask_255 = cv2.resize(mask_255, (w, h), interpolation=cv2.INTER_LINEAR)
            
            # Create JET heatmap
            heatmap = cv2.applyColorMap(mask_255, cv2.COLORMAP_JET)
            
            # Blend with original
            result = cv2.addWeighted(bg_rgb, 0.4, heatmap, 0.6, 0)
            
            # Draw contours
            contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(result, contours, -1, (0, 255, 0), 2)
            
            _, buffer = cv2.imencode('.jpg', result)
            mask_viz_b64 = base64.b64encode(buffer).decode('utf-8')
        except Exception as aze:
            logger.warning(f"Visualization error: {aze}")

        return {
            "status": "success",
            "label": str(LABELS[int(idx)]),
            "confidence": round(float(probs[idx]), 4),
            "all_probabilities": {LABELS[i]: round(float(p), 4) for i, p in enumerate(probs)},
            "mask": mask_prob[::8, ::8].tolist(),
            "mask_full_shape": list(mask_prob.shape),
            "mask_viz_b64": mask_viz_b64,
            "model_used": self.selected_model,
            "architecture": self.arch_type
        }

    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        return self._mock_predict(error_msg=str(e))

# ============================================================
# ĐIỂM 5: SỬA _mock_predict() return format
# ============================================================

# ✗ TRƯỚC (SAI):
def _mock_predict(self):
    return {
        "label": "Error(Mock)", 
        "confidence": 0.0, 
        "mask": [], 
        "mask_viz": ""
    }

# ✓ SAU (ĐÚNG):
def _mock_predict(self, error_msg: str = ""):
    return {
        "status": "error",
        "label": "Error",
        "confidence": 0.0,
        "all_probabilities": {l: 0.0 for l in LABELS},
        "mask": [],
        "mask_full_shape": [],
        "mask_viz_b64": "",
        "model_used": self.selected_model,
        "architecture": self.arch_type,
        "error": error_msg
    }


# ============================================================
# KIỂM TRA SAU KHI SỬA:
# ============================================================

print("""
1. Chạy test cơ bản:
   from app.services.inference import InferenceService
   service = InferenceService(arch_type="deeplabv3plus")
   print(service.get_gpu_status())

2. Kiểm tra import các model:
   from model_architecture.deeplabv3_architect import MultiTaskDeepLabV3Plus
   model = MultiTaskDeepLabV3Plus(in_channels=1, num_classes=3, num_seg_classes=2)

3. Test predict trên ảnh:
   import numpy as np
   test_img = np.random.randint(0, 256, (512, 512), dtype=np.uint8)
   result = service.predict(test_img)
   print(result.keys())  # Phải có: status, label, confidence, all_probabilities, mask, mask_viz_b64

4. Kiểm tra các architectures:
   for arch in ["deeplabv3plus", "resnet_unet", "unetplusplus", "effb3_unet", "effb3_architecture"]:
       print(f"Testing {arch}...")
       service = InferenceService(arch_type=arch)
       status = service.get_gpu_status()
       print(f"  Model loaded: {status['model_loaded']}")
""")
