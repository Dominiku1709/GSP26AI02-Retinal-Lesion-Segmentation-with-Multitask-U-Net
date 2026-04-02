"""
dummy_model.py
==============
A fake MultiTaskUNet that produces outputs with the EXACT same shapes
as the real model, but using only random numbers and simple convolutions.

Purpose: test the full webapp pipeline (upload → inference → display)
without needing the real .pth weights or segmentation_models_pytorch.

Contracts matched from model_architecture.py:
  Input:     (B, 1, H, W)  float32
  Output:    dict with keys:
    "cls_output"  → (B, num_classes)       raw logits
    "seg_output"  → (B, num_seg_classes, H, W) raw logits
  (deep_sup_outputs omitted — same as real model at inference time)

Usage:
  python dummy_model.py          # runs self-test, prints shapes
  python convert_model.py        # replace real model with this dummy
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict


class DummyMultiTaskUNet(nn.Module):
    """
    Matches the forward() signature and output shape of MultiTaskUNet exactly.
    Uses a tiny real conv so ONNX tracing produces a valid computation graph
    (pure torch.randn() cannot be traced — it produces a constant node).
    """

    def __init__(
        self,
        in_channels:    int = 1,
        num_classes:    int = 3,
        num_seg_classes: int = 2,
        # Accept (and silently ignore) every kwarg the real model takes
        **kwargs,
    ):
        super().__init__()
        self.num_classes     = num_classes
        self.num_seg_classes = num_seg_classes

        # A tiny learned conv — just enough to make ONNX tracing work.
        # The weights are random and meaningless; that's intentional.
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 16, kernel_size=3, padding=1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(16, 16, kernel_size=3, padding=1, bias=False),
            nn.ReLU(inplace=True),
        )

        # Classification head: global pool → linear → (B, num_classes)
        self.cls_head = nn.Linear(16, num_classes)

        # Segmentation head: conv → (B, num_seg_classes, H, W)
        self.seg_head = nn.Conv2d(16, num_seg_classes, kernel_size=1)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        # x shape: (B, 1, H, W)
        feat = self.stem(x)                        # (B, 16, H, W)

        # Classification branch
        pooled     = feat.mean(dim=[2, 3])         # (B, 16) — global average pool
        cls_output = self.cls_head(pooled)         # (B, num_classes)

        # Segmentation branch
        seg_output = self.seg_head(feat)           # (B, num_seg_classes, H, W)

        # Return the SAME dict structure as the real MultiTaskUNet
        return {
            "cls_output": cls_output,
            "seg_output": seg_output,
        }

    def get_num_params(self) -> Dict[str, int]:
        """Matches the real model's helper method."""
        total = sum(p.numel() for p in self.parameters())
        return {"total": total}


# ── Self-test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("Dummy MultiTaskUNet — shape contract test")
    print("=" * 50)

    model = DummyMultiTaskUNet(in_channels=1, num_classes=3, num_seg_classes=2)
    model.eval()

    # Test at two different input sizes
    for H, W in [(224, 224), (512, 512)]:
        x = torch.randn(1, 1, H, W)
        with torch.no_grad():
            out = model(x)

        cls_shape = tuple(out["cls_output"].shape)
        seg_shape = tuple(out["seg_output"].shape)

        cls_ok = cls_shape == (1, 3)
        seg_ok = seg_shape == (1, 2, H, W)

        print(f"\n  Input  {tuple(x.shape)}")
        print(f"  cls_output {cls_shape}  {'OK' if cls_ok else 'FAIL'}")
        print(f"  seg_output {seg_shape}  {'OK' if seg_ok else 'FAIL'}")

    params = model.get_num_params()
    print(f"\n  Parameters: {params['total']:,}  "
          f"(real model ~21M — dummy is intentionally tiny)")
    print("\n  All shapes match the real model contract.")
