# app/core/config.py

PREPROCESS_CONFIG = {
    "target_size": (224, 224),
    "interpolation": "bilinear", # Match standard PyTorch/OpenCV
    "norm_mean": 0.5,             # Placeholder: AI guys provide this
    "norm_std": 0.5,              # Placeholder: AI guys provide this
    "use_monai_advanced": False   # Toggle for medical-specific denoising
}