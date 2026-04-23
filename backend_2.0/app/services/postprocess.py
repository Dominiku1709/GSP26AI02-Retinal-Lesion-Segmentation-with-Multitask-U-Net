# backend_2.0/app/services/postprocess.py
import cv2
import base64
import numpy as np
import os

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


def save_mask_to_disk(mask_data, image_filename: str, storage_dir: str = "storage") -> str:
    # 1. Chuyển đổi về numpy array nếu đang là list
    mask_array = np.array(mask_data, dtype=np.float32)
    
    # 2. Kiểm tra nếu mask bị trống
    if mask_array.size == 0:
        mask_array = np.zeros((224, 224), dtype=np.float32)

    # 3. Scale về 0-255
    mask_visual = (np.clip(mask_array, 0, 1) * 255).astype(np.uint8)
    
    # 4. Resize mask về kích thước hiển thị chuẩn (ví dụ 224x224) 
    # vì mask từ inference trả về đang bị downsample 8x
    mask_visual = cv2.resize(mask_visual, (224, 224), interpolation=cv2.INTER_LINEAR)
    
    # 5. Xử lý đường dẫn
    os.makedirs(storage_dir, exist_ok=True)
    image_name_without_ext = os.path.splitext(image_filename)[0]
    mask_filename = f"mask+{image_name_without_ext}.png" # Ép đuôi png cho mask
    mask_path = os.path.join(storage_dir, mask_filename)
    
    # 6. Lưu file
    cv2.imwrite(mask_path, mask_visual)
    
    return mask_filename