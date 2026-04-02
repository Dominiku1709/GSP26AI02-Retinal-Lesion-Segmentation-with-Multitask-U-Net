"""
convert_dummy.py
================
Exports the DummyMultiTaskUNet to ONNX so the FastAPI backend
can load it exactly as it would the real model.

Run this once on any machine:
    python convert_dummy.py

Requirements (much lighter than the real model):
    pip install torch onnx onnxruntime

No .pth file needed. No segmentation_models_pytorch needed.
"""

import torch
import torch.nn as nn
import numpy as np
import os
import sys

ONNX_PATH  = "backend_2.0/weights/oct_model.onnx"
INPUT_SIZE = (224, 224)

sys.path.insert(0, os.path.dirname(__file__))
from dummy_model import DummyMultiTaskUNet


# ── Build ──────────────────────────────────────────────────────────────────────
print("Building dummy model...")
model = DummyMultiTaskUNet(in_channels=1, num_classes=3, num_seg_classes=2)
model.eval()
print(f"  Parameters: {model.get_num_params()['total']:,}")


# ── Wrap: dict → tuple (required for ONNX tracing) ────────────────────────────
class ONNXWrapper(nn.Module):
    def __init__(self, m):
        super().__init__()
        self.model = m
    def forward(self, x):
        out = self.model(x)
        return out["cls_output"], out["seg_output"]

wrapped = ONNXWrapper(model)
wrapped.eval()


# ── Export ─────────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(ONNX_PATH), exist_ok=True)
dummy_input = torch.randn(1, 1, *INPUT_SIZE)

print(f"Exporting to {ONNX_PATH} ...")
torch.onnx.export(
    wrapped, dummy_input, ONNX_PATH,
    export_params=True,
    opset_version=17,
    do_constant_folding=True,
    input_names=["input"],
    output_names=["classification", "segmentation"],
    dynamic_axes={
        "input":          {0: "batch_size"},
        "classification": {0: "batch_size"},
        "segmentation":   {0: "batch_size"},
    },
    verbose=False,
)


# ── Verify ─────────────────────────────────────────────────────────────────────
import onnx, onnxruntime as ort

onnx.checker.check_model(onnx.load(ONNX_PATH))

session = ort.InferenceSession(ONNX_PATH, providers=["CPUExecutionProvider"])
dummy_np = np.random.randn(1, 1, *INPUT_SIZE).astype(np.float32)
results  = session.run(None, {"input": dummy_np})

print(f"\nVerification:")
print(f"  classification  shape={results[0].shape}   (expected: (1, 3))")
print(f"  segmentation    shape={results[1].shape}  (expected: (1, 2, 224, 224))")
print(f"\nDone. The backend will now run with the dummy model.")
print(f"Replace {ONNX_PATH} with the real model when it's ready.")
