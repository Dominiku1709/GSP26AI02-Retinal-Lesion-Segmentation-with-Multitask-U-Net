import onnxruntime as ort
import os
from dotenv import load_dotenv
load_dotenv()
path = r"backend_2.0\weights\deeplabv3_best_model.pth"

print(f"Available Providers: {ort.get_available_providers()}")

try:
    # Thử ép buộc chạy bằng CUDA
    session = ort.InferenceSession(path, providers=['CUDAExecutionProvider'])
    print("✅ Thành công! ONNX đã nhận CUDA 13.")
except Exception as e:
    print(f"❌ Thất bại: {e}")