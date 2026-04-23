# backend_2.0/app/core/gpu_config.py
"""
GPU and CUDA configuration management for ONNX Runtime.

Handles detection and initialization of GPU providers with proper fallback to CPU.
"""

import os
import logging
from typing import List, Tuple
import onnxruntime as ort

logger = logging.getLogger(__name__)


class GPUConfig:
    """Manages GPU/CUDA availability and ONNX Runtime provider selection."""
    
    def __init__(self):
        self.cuda_available = False
        self.gpu_enabled = os.getenv("ENABLE_GPU", "true").lower() == "true"
        self.providers: List[str] = []
        self.fallback_to_cpu = os.getenv("FALLBACK_TO_CPU", "true").lower() == "true"
        
        self._detect_providers()
    
    def _detect_providers(self) -> None:
        """Detect available execution providers and set up the provider list."""
        available_providers = ort.get_available_providers()
        logger.info(f"Available ONNX Runtime providers: {available_providers}")
        
        self.providers = []
        
        # Check for CUDA
        if self.gpu_enabled:
            if "CUDAExecutionProvider" in available_providers:
                self.providers.append("CUDAExecutionProvider")
                self.cuda_available = True
                logger.info("✓ CUDA provider available - GPU acceleration enabled")
            else:
                logger.warning("✗ CUDA provider not available - GPU acceleration disabled")
                if "TensorrtExecutionProvider" in available_providers:
                    logger.info("  Alternative: TensorRT provider available")
        
        # Always add CPU as fallback
        if self.fallback_to_cpu:
            self.providers.append("CPUExecutionProvider")
            logger.info("✓ CPU provider added as fallback")
        elif not self.cuda_available:
            # If GPU is disabled and no fallback, still add CPU
            self.providers.append("CPUExecutionProvider")
            logger.warning("GPU disabled but CPU fallback enabled for safety")
        
        if not self.providers:
            raise RuntimeError(
                "No execution providers available! "
                "Please install onnxruntime or fix your CUDA installation."
            )
    
    def get_providers(self) -> List[str]:
        """Get the configured list of providers."""
        return self.providers
    
    def get_info(self) -> dict:
        """Get GPU configuration information."""
        return {
            "gpu_enabled": self.gpu_enabled,
            "cuda_available": self.cuda_available,
            "active_providers": self.providers,
            "fallback_to_cpu": self.fallback_to_cpu
        }
    
    @staticmethod
    def get_cuda_version_info() -> dict:
        """Get CUDA and cuDNN version information if available."""
        info = {
            "cuda_available": False,
            "cuda_version": None,
            "cudnn_version": None,
            "onnxruntime_version": ort.__version__
        }
        
        try:
            import torch
            if torch.cuda.is_available():
                info["cuda_available"] = True
                info["cuda_version"] = torch.version.cuda
                info["cudnn_version"] = torch.backends.cudnn.version()
        except ImportError:
            pass
        
        return info


# Global GPU configuration instance
gpu_config = GPUConfig()
