import onnxruntime as ort
import numpy as np
import os
import random

class InferenceService:
    def __init__(self, model_path: str):
        self.model_path = model_path
        # 1. Check if the model file exists on the server
        if os.path.exists(self.model_path):
            # Load the model into the ONNX Runtime session
            self.session = ort.InferenceSession(self.model_path)
            self.is_mock = False
        else:
            # If the model is missing, we use 'Mock Mode' to unblock the Frontend
            print(f"WARNING: Model not found at {model_path}. Running in MOCK MODE.")
            self.is_mock = True

    def predict(self, input_data: np.ndarray):
        if self.is_mock:
            return self._mock_predict()

        # 2. Identify the input and output names required by the ONNX file
        input_name = self.session.get_inputs()[0].name
        
        # 3. Run the math! (This is the 'Inference' step)
        # result is usually a list of outputs: [classification_logits, segmentation_mask]
        outputs = self.session.run(None, {input_name: input_data})
        
        # 4. Simplify the outputs for the rest of the app
        # This part depends on your specific model's architecture
        label_index = np.argmax(outputs[0])
        labels = ["AMD", "DME", "Normal"]
        
        return {
            "label": labels[label_index],
            "confidence": float(np.max(outputs[0])),
            "mask": outputs[1][0][0] # Taking the first batch, first channel mask
        }

    def _mock_predict(self):
        # Returns fake but realistic data to keep the project moving
        return {
            "label": random.choice(["AMD", "DME", "Normal"]),
            "confidence": 0.98,
            "mask": np.random.randint(0, 2, (224, 224)) # A random binary mask
        }

# Initialize the service (Point to your weights folder)
model_runner = InferenceService("weights/oct_model.onnx")