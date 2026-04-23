# backend_2.0/app/services/preprocess.py
import cv2
import torch
import numpy as np
from monai.transforms import (
    Compose, 
    Resize, 
    ScaleIntensity, 
    NormalizeIntensity, 
    EnsureChannelFirst,
    ToTensor
)
from ..core.config import PREPROCESS_CONFIG

def get_independent_pipeline():
    transforms = [
        # Đảm bảo ảnh từ (H, W) thành (1, H, W)
        EnsureChannelFirst(channel_dim='no_channel'), 
        
        # Scale về dải [0, 1] trước khi Normalize (Cực kỳ quan trọng để tránh nổ Logits)
        ScaleIntensity(), 
        
        Resize(
            spatial_size=PREPROCESS_CONFIG["target_size"],
            mode=PREPROCESS_CONFIG["interpolation"]
        ),
        
        # Chuẩn hóa theo Mean/Std (Dành cho 1 kênh)
        NormalizeIntensity(
            subtrahend=PREPROCESS_CONFIG["norm_mean"],
            divisor=PREPROCESS_CONFIG["norm_std"]
        ),
        
        # Chuyển trực tiếp sang Torch Tensor
        ToTensor()
    ]
    return Compose(transforms)

def prepare_image(image_path: str):
    # 1. Load ảnh grayscale gốc (Dùng IMREAD_GRAYSCALE để ép về 1 kênh ngay từ đầu)
    img_raw = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img_raw is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    # Resize ảnh gốc để làm nền (dùng uint8 để hiển thị/vẽ mask sau này)
    target_size = PREPROCESS_CONFIG["target_size"] # Thường là (224, 224)
    # Lưu ý: cv2.resize dùng (W, H), MONAI dùng (H, W)
    img_bg = cv2.resize(img_raw, (target_size[1], target_size[0]), interpolation=cv2.INTER_AREA)

    # 2. Chạy qua pipeline MONAI
    pipeline = get_independent_pipeline()
    img_tensor = pipeline(img_raw) # Output sẽ là torch.Tensor kích thước (1, H, W)
    
    # 3. Thêm Batch Dimension để thành (1, 1, H, W)
    final_tensor = img_tensor.unsqueeze(0) 
    
    # TRẢ VỀ: (Tensor chuẩn hóa 1 kênh, Ảnh uint8 làm nền)
    return final_tensor, img_bg