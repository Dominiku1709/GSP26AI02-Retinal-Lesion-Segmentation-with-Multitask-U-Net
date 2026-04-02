"""
convert_model.py
================
Converts your MultiTaskUNet .pth → .onnx for FastAPI deployment.

Run this ONCE on your local machine (where PyTorch is installed):
    python convert_model.py

Requirements (local only, NOT on the server):
    pip install torch segmentation-models-pytorch onnx onnxruntime scipy

Two critical problems this script solves that a naive export would miss:

  PROBLEM 1: MultiTaskUNet.forward() returns a DICT.
    ONNX tracing requires the model to return a tuple of tensors, never a dict.
    We wrap the model in an ONNXExportWrapper that unwraps the dict into a tuple.

  PROBLEM 2: use_deep_supervision=True produces a LIST of tensors inside the dict.
    ONNX tracing cannot handle dynamic-length lists in the output graph.
    We force use_deep_supervision=False during export only.
    This does NOT affect weights — only which outputs get traced.
"""

import torch
import torch.nn as nn
import numpy as np
import os
import sys

# ─── CONFIG ────────────────────────────────────────────────────────────────────
PTH_PATH  = r"D:\KEEP\FPTUni\DH_FPT\FPTU\Syllabuses\Sem9\capstone\code\capstone_code\Multitask_test\backend_2.0\stage3_multitask_finetune_best_weights_only.pth"                       # ← path to your .pth file

ONNX_PATH = "\weights\oct_model.onnx"   # ← where the backend reads from

# Must match exactly what the model was trained with.
# Check your training script for these values.
MODEL_CONFIG = {
    "encoder_name"        : "resnet34",   # change if you trained with efficientnet-b3
    "encoder_weights"     : None,         # None = skip re-downloading imagenet weights
    "num_classes"         : 3,            # classification output size — check your training config
    "num_seg_classes"     : 2,            # segmentation channels (background + lesion)
    "in_channels"         : 1,            # grayscale OCT
    "use_attention"       : True,
    "use_scse"            : True,
    "use_deep_supervision": False,        # MUST be False for ONNX export (see note above)
    "dropout_rate"        : 0.3,
}

INPUT_SIZE = (224, 224)  # Must match PREPROCESS_CONFIG["target_size"] in backend config.py
# ───────────────────────────────────────────────────────────────────────────────


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend_2.0"))
from model_architecture import MultiTaskUNet


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — INSPECT CHECKPOINT
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("Step 1 — Inspecting checkpoint")
print("=" * 60)

raw = torch.load(PTH_PATH, map_location="cpu")
checkpoint = raw
if isinstance(raw, dict):
    for key in ["state_dict", "model_state_dict", "model", "weights", "net"]:
        if key in raw:
            print(f"  Unwrapped under key: '{key}'")
            checkpoint = raw[key]
            break

all_keys = list(checkpoint.keys())
print(f"  Total tensors: {len(all_keys)}")
print("  First 8 keys:")
for k in all_keys[:8]:
    print(f"    {k:60s}  {list(checkpoint[k].shape)}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — STRIP KEY PREFIX
# Your checkpoint stores everything under "seg_model.*"
# MultiTaskUNet expects bare keys: "encoder.*", "decoder_blocks.*" etc.
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Step 2 — Stripping key prefix")
print("=" * 60)

prefix = ""
first_key = all_keys[0]
for marker in ["encoder.", "decoder", "classifier", "seg_head", "attention"]:
    if marker in first_key:
        prefix = first_key[:first_key.index(marker)]
        break

if prefix:
    print(f"  Detected prefix: '{prefix}'")
    stripped = {}
    for k, v in checkpoint.items():
        new_k = k[len(prefix):] if k.startswith(prefix) else k
        stripped[new_k] = v
    checkpoint = stripped
    print(f"  Stripped. New first key: '{list(checkpoint.keys())[0]}'")
else:
    print("  No prefix detected — keys already bare")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — DETECT ENCODER TYPE
# conv3 present in layer1.0 → ResNet50/101 (bottleneck)
# conv3 absent              → ResNet34/18  (basic block)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Step 3 — Detecting encoder")
print("=" * 60)

has_conv3 = any("layer1.0.conv3" in k for k in checkpoint.keys())
has_aspp  = any("decoder.aspp"   in k for k in checkpoint.keys())

detected_encoder = "resnet50" if has_conv3 else "resnet34"
print(f"  Encoder: {detected_encoder}  (conv3={'yes' if has_conv3 else 'no'})")

if has_aspp:
    print(f"  WARNING: ASPP/DeepLab decoder keys found — these will be skipped")
    print(f"  Only encoder + classifier weights will transfer cleanly")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — BUILD MODEL
# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — BUILD MODEL (UPDATED)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Step 4 — Building model")
print("=" * 60)

# The error shows:
# checkpoint wants 256, model has 512
# checkpoint wants 128, model has 256
# We need to pass the correct hidden dimensions to your class.

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — BUILD MODEL (PATCHED)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Step 4 — Building model & Patching Classifier")
print("=" * 60)

# 1. Build the base model
model = MultiTaskUNet(**MODEL_CONFIG)

# 2. Patch the classifier to match the checkpoint's 256/128 architecture
# We must use the exact names and order used in your model_architecture.py
bottleneck_features = model.encoder_channels[-1] # This will be 2048 for ResNet50
dropout_rate = MODEL_CONFIG.get("dropout_rate", 0.3)

model.classifier = nn.Sequential(
    nn.Flatten(),
    nn.Linear(bottleneck_features, 256),  # Fixed to match checkpoint
    nn.BatchNorm1d(256),
    nn.ReLU(inplace=True),
    nn.Dropout(dropout_rate),
    nn.Linear(256, 128),                  # Fixed to match checkpoint
    nn.BatchNorm1d(128),
    nn.ReLU(inplace=True),
    nn.Dropout(dropout_rate),
    nn.Linear(128, 3)                     # 3 classes
)

model.eval()
print(f"  Built MultiTaskUNet and patched classifier to [256, 128]")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5 — LOAD WEIGHTS WITH strict=False
# strict=False: load every key that matches, silently skip any that don't.
# This handles the ASPP decoder keys (no match -> skipped) without crashing.
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Step 5 — Loading weights (strict=False)")
print("=" * 60)

result = model.load_state_dict(checkpoint, strict=False)

missing    = result.missing_keys
unexpected = result.unexpected_keys

def count_by(keys, prefix):
    return len([k for k in keys if k.startswith(prefix)])

total   = sum(p.numel() for p in model.parameters())
loaded  = sum(p.numel() for n, p in model.named_parameters() if n not in missing)
pct     = 100 * loaded // total

print(f"  Loaded: {loaded:,} / {total:,} parameters  ({pct}%)")
print(f"\n  Missing  ({len(missing):3d} keys):    "
      f"encoder={count_by(missing,'encoder')}  "
      f"decoder={count_by(missing,'decoder_blocks')}  "
      f"attention={count_by(missing,'attention')}  "
      f"classifier={count_by(missing,'classifier')}")
print(f"  Skipped  ({len(unexpected):3d} keys):    "
      f"(checkpoint keys that had no matching layer in the model)")

if count_by(missing, "encoder") > 0:
    print("\n  ACTION NEEDED: encoder keys are still missing after stripping.")
    print("  This means the encoder in the checkpoint is a different variant.")
    print("  Inspect the keys above and update 'detected_encoder' in MODEL_CONFIG.")
elif count_by(missing, "decoder_blocks") > 0 and count_by(missing, "encoder") == 0:
    print("\n  Encoder loaded correctly. Decoder missing — expected if checkpoint")
    print("  used a different decoder (ASPP vs UNet). Decoder will use random init.")
else:
    print("\n  Load looks good.")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6 — EXPORT TO ONNX
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Step 6 — Exporting to ONNX")
print("=" * 60)

class ONNXExportWrapper(nn.Module):
    """Converts dict output to tuple so ONNX can trace it."""
    def __init__(self, m):
        super().__init__()
        self.model = m
    def forward(self, x):
        out = self.model(x)
        return out["cls_output"], out["seg_output"]

os.makedirs(os.path.dirname(ONNX_PATH), exist_ok=True)
wrapped = ONNXExportWrapper(model)
wrapped.eval()
dummy = torch.randn(1, 1, *INPUT_SIZE)

torch.onnx.export(
    wrapped, dummy, ONNX_PATH,
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
print(f"  Exported: {ONNX_PATH}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 7 — VERIFY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("Step 7 — Verification")
print("=" * 60)

import onnx, onnxruntime as ort

onnx.checker.check_model(onnx.load(ONNX_PATH))
print("  ONNX graph: valid")

session = ort.InferenceSession(ONNX_PATH, providers=["CPUExecutionProvider"])
for i, o in enumerate(session.get_outputs()):
    print(f"  Output[{i}] '{o.name}'  shape={o.shape}")

dummy_np = np.random.randn(1, 1, *INPUT_SIZE).astype(np.float32)
results  = session.run(None, {"input": dummy_np})

def softmax(x):
    e = np.exp(x - x.max()); return e / e.sum()

probs = softmax(results[0][0])
print(f"\n  Classification probs: {probs.round(3)}  sum={probs.sum():.4f}")
print(f"  Segmentation shape: {results[1].shape}  "
      f"range=[{results[1].min():.3f}, {results[1].max():.3f}]")

print(f"\n{'='*60}")
print(f"  Done. Copy '{ONNX_PATH}' to backend_2.0/weights/")
print(f"{'='*60}")
