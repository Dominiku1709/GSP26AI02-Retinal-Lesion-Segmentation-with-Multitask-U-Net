import cv2
import base64
import numpy as np

def mask_to_base64(mask_array: np.ndarray):
    # 1. Scale the mask from [0, 1] or [0, 255] to full uint8
    # If it's a binary mask (0 or 1), we multiply by 255 so it's visible (Black/White)
    mask_visual = (mask_array * 255).astype(np.uint8)

    # 2. Encode the image into PNG format in memory (not saved to disk)
    # .imencode returns (success_flag, buffer)
    _, buffer = cv2.imencode('.png', mask_visual)

    # 3. Convert the buffer to a Base64 string
    # This turns binary data into a text string
    mask_base64 = base64.b64encode(buffer).decode('utf-8')

    # 4. Return it as a data URI so the Frontend can put it in an <img> tag
    return f"data:image/png;base64,{mask_base64}"