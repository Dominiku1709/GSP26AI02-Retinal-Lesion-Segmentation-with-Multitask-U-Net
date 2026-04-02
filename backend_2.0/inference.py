"""
app/services/inference.py
=========================
Runs the exported MultiTaskUNet ONNX model.

Your model's exact I/O contract (from model_architecture.py):
  Input:   (1, 1, 224, 224)  float32   — batch, grayscale channel, H, W
  Output[0] "classification": (1, 3)   float32   — logits for 3 classes
  Output[1] "segmentation":  (1, 2, 224, 224) float32 — 2-channel mask

  NOTE: num_classes=3 in your architecture config.
  Update LABELS below to match your 3 actual training class names.
  The order must be identical to the label order used during training.
"""

import onnxruntime as ort
import numpy as np
import os
import random


# ── YOUR 3 CLASSIFICATION LABELS ──────────────────────────────────────────────
# num_classes=3 in your MultiTaskUNet, so exactly 3 labels here.
# Check your training code for the exact class order.
# Common OCT datasets use: Normal, Drusen, CNV  OR  Normal, DME, CNV
LABELS = ["Normal", "Drusen", "CNV"]   # ← verify this matches your training order


def _softmax(logits: np.ndarray) -> np.ndarray:
    """
    Converts raw classification logits → probabilities summing to 1.0.
    Numerical stability: subtract max before exp to avoid overflow.
    """
    shifted = logits - logits.max()
    e = np.exp(shifted)
    return e / e.sum()


def _sigmoid(x: np.ndarray) -> np.ndarray:
    """
    Per-pixel probability for the segmentation mask.
    Your seg head outputs raw logits (not probabilities) — sigmoid maps them to [0,1].
    """
    return 1.0 / (1.0 + np.exp(-x))


class InferenceService:

    def __init__(self, model_path: str):
        self.model_path = model_path

        if os.path.exists(self.model_path):
            print(f"[InferenceService] Loading: {model_path}")
            self.session = ort.InferenceSession(
                self.model_path,
                # Tries GPU (CUDA) first, falls back to CPU automatically
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
            )
            self.is_mock = False
            self._log_io_info()
        else:
            print(f"[InferenceService] WARNING: no model at '{model_path}'. MOCK MODE.")
            self.is_mock = True

    def _log_io_info(self):
        """Prints the model's I/O at startup — useful for debugging mismatches."""
        inp = self.session.get_inputs()[0]
        print(f"  Input  → '{inp.name}' shape={inp.shape}")
        for i, out in enumerate(self.session.get_outputs()):
            print(f"  Output[{i}] → '{out.name}' shape={out.shape}")

    def predict(self, input_data: np.ndarray) -> dict:
        """
        Runs inference on one preprocessed OCT image.

        Args:
            input_data: np.ndarray, shape (1, 1, 224, 224), dtype float32.
                        Produced by preprocess.prepare_image().

        Returns:
            {
                "label"      : str    — e.g. "Drusen"
                "confidence" : float  — 0.0 to 1.0, e.g. 0.94
                "mask"       : np.ndarray shape (224, 224), values 0.0–1.0
            }
        """
        if self.is_mock:
            return self._mock_predict()

        # ── Run the ONNX graph ───────────────────────────────────────────────
        # input_name should be "input" (set in convert_model.py export)
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: input_data})

        # ── Output[0]: Classification ────────────────────────────────────────
        # Shape: (1, 3) — one row per batch, one column per class
        # [0] removes the batch dimension → shape (3,)
        logits = outputs[0][0]             # shape: (3,)
        probs  = _softmax(logits)          # shape: (3,)  sums to 1.0

        label_index = int(np.argmax(probs))
        label       = LABELS[label_index]
        confidence  = float(probs[label_index])

        # ── Output[1]: Segmentation mask ────────────────────────────────────
        # Shape: (1, 2, 224, 224)
        #   [0]    → removes batch dim          → (2, 224, 224)
        #
        # Your model uses num_seg_classes=2:
        #   channel 0 = background probability
        #   channel 1 = lesion probability
        #
        # We take channel 1 (lesion) and apply sigmoid to get [0,1] probabilities.
        seg_logits = outputs[1][0]          # shape: (2, 224, 224)
        lesion_channel = seg_logits[1]      # shape: (224, 224) — lesion logits
        mask = _sigmoid(lesion_channel)     # shape: (224, 224) — values 0.0–1.0

        return {
            "label"      : label,
            "confidence" : confidence,
            "mask"       : mask,
        }

    def _mock_predict(self) -> dict:
        """
        Realistic fake data when no model file is available.
        Generates a smooth elliptical blob instead of random noise.
        """
        label = random.choice(LABELS)

        # Smooth lesion-shaped blob near the centre of the image
        mask = np.zeros((224, 224), dtype=np.float32)
        cy = 112 + random.randint(-20, 20)
        cx = 112 + random.randint(-30, 30)
        ry = 35 + random.randint(-10, 10)   # vertical radius
        rx = 50 + random.randint(-10, 10)   # horizontal radius
        for y in range(224):
            for x in range(224):
                val = ((y - cy) / ry) ** 2 + ((x - cx) / rx) ** 2
                mask[y, x] = max(0.0, 1.0 - val)

        return {
            "label"      : label,
            "confidence" : round(random.uniform(0.82, 0.98), 4),
            "mask"       : mask,
        }


# Singleton — loaded once when the module is first imported.
# endpoints.py imports this:  from ..services.inference import model_runner
model_runner = InferenceService("weights/oct_model.onnx")
