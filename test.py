import torch

model_path = r"backend_2.0\stage3_multitask_finetune_best_weights_only.pth"
checkpoint = torch.load(model_path, map_location='cpu')

# Check if the checkpoint is the weights themselves or a dictionary
if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
    weights = checkpoint['model_state_dict']
    print("Detected nested dictionary structure.")
else:
    # If 'model_state_dict' isn't there, the checkpoint usually IS the weights
    weights = checkpoint
    print("Detected direct weights structure.")

# Now access the layers
keys = list(weights.keys())
first_key = keys[0]
last_key = keys[-1]

print(f"First Layer: {first_key} | Shape: {weights[first_key].shape}")
print(f"Total Layers: {len(keys)}")
print(f"Last Layer:  {last_key}  | Shape: {weights[last_key].shape}")