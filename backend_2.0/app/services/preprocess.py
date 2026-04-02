# app/services/preprocess.py
from monai.transforms import (
    Compose, 
    Resize, 
    ScaleIntensity, 
    NormalizeIntensity, 
    EnsureChannelFirst  # Use this instead of AddChannel
)
from ..core.config import PREPROCESS_CONFIG
import numpy as np

def get_independent_pipeline():
    transforms = [
        # Automatically handles (H, W) -> (1, H, W)
        EnsureChannelFirst(channel_dim='no_channel'), 
        
        Resize(
            spatial_size=PREPROCESS_CONFIG["target_size"],
            mode=PREPROCESS_CONFIG["interpolation"]
        ),
        
        NormalizeIntensity(
            subtrahend=PREPROCESS_CONFIG["norm_mean"],
            divisor=PREPROCESS_CONFIG["norm_std"]
        )
    ]
    return Compose(transforms)
def prepare_image(image_path: str):
    # Use standard OpenCV to load, then pass to the MONAI pipeline
    import cv2
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    pipeline = get_independent_pipeline()
    # Cast to float32 to ensure mathematical precision
    img_tensor = pipeline(img).astype(np.float32)
    
    # Add batch dimension: (1, 1, 224, 224)
    return np.expand_dims(img_tensor, axis=0)