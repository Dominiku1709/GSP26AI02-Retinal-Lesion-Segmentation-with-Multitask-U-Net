# RetinaAI — Hướng Dẫn Chạy Hệ Thống (Dành cho Hội Đồng Chấm)

> **Dự án:** RetinaAI — OCT Retinal Lesion Segmentation & Classification  
> **Sinh viên:** [Điền tên]  
> **MSSV:** [Điền MSSV]  
> **Giảng viên hướng dẫn:** [Điền tên GV]  
> **Ngày nộp:** 2026-04-24

---

## 📋 Yêu Cầu Hệ Thống

| Thành phần | Phiên bản yêu cầu |
|-----------|-------------------|
| Python | >= 3.9 |
| Node.js | >= 18.0 |
| GPU (khuyến nghị) | NVIDIA CUDA-capable (RTX 3060+) |
| RAM | >= 8GB |
| Dung lượng | >= 2GB (không tính weights) |

---

## 🚀 Hướng Dẫn Chạy

### Bước 0: Giải nén

```bash
# Giải nén source code
# File: RetinaAI_SourceCode_Final.zip

# Giải nén model weights (nếu có riêng)
# File: Model_Weights.zip → Copy nội dung vào backend_2.0/weights/
```

### Bước 1: Khởi Động Backend (Port 8000)

```bash
# Di chuyển vào thư mục backend
cd backend_2.0

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# (Tùy chọn) Tạo database demo với dữ liệu mẫu
cd ..
python seed_data.py
cd backend_2.0

# Khởi động server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Kiểm tra:** Mở trình duyệt tại [http://localhost:8000/docs](http://localhost:8000/docs) — Sẽ hiển thị Swagger API Documentation.

### Bước 2: Khởi Động Frontend (Port 3000)

```bash
# Mở terminal mới, di chuyển vào thư mục UX
cd UX

# Cài đặt dependencies
npm install

# Khởi động development server
npm run dev
```

✅ **Kiểm tra:** Mở trình duyệt tại [http://localhost:3000](http://localhost:3000) — Sẽ hiển thị giao diện RetinaAI.

---

## 🧪 Kiểm Tra Nhanh

### API Health Check
```bash
curl http://localhost:8000/api/health
```
**Kết quả mong đợi:**
```json
{
  "status": "healthy",
  "app_name": "OCT Analysis Backend",
  "version": "2.0.0",
  "database": "connected",
  "model_available": true
}
```

### GPU Status
```bash
curl http://localhost:8000/api/system/gpu-status
```

### Danh Sách Models
```bash
curl http://localhost:8000/api/models
```

---

## 📂 Cấu Trúc Thư Mục Chính

```
Multitask_test/
├── backend_2.0/              # Backend (FastAPI + PyTorch)
│   ├── app/                  # Core application
│   │   ├── main.py           # Entry point
│   │   ├── services/
│   │   │   ├── preprocess.py # MONAI preprocessing
│   │   │   ├── inference.py  # PyTorch inference engine
│   │   │   └── postprocess.py# Mask visualization
│   │   └── api/
│   │       └── endpoints.py  # API routes
│   ├── model_architecture/   # AI model definitions
│   ├── weights/              # Pre-trained .pth models
│   └── requirements.txt
│
├── UX/                       # Frontend (Next.js + React)
│   ├── app/                  # Pages
│   ├── components/           # React components
│   └── lib/                  # API client + state
│
├── seed_data.py              # Script tạo database demo
├── REQUIREMENTS_CHECK.txt    # Danh sách thư viện
└── README_SUBMISSION.md      # File này
```

---

## 🔄 Luồng Xử Lý (Pipeline 5 Bước)

```
1. INPUT        → Upload ảnh OCT qua giao diện web
2. PREPROCESS   → MONAI: Grayscale → Resize → Normalize → Tensor
3. INFERENCE    → PyTorch: Forward pass trên GPU/CPU
4. POSTPROCESS  → OpenCV: Mask visualization + Heatmap JET
5. OUTPUT       → JSON Response + Base64 mask → Frontend hiển thị
```

---

## ⚠️ Lưu Ý Quan Trọng

1. **Model Weights:** Nếu thư mục `backend_2.0/weights/` trống, hệ thống sẽ chạy ở **chế độ Mock** (trả về dữ liệu giả lập). Hãy đảm bảo đã copy các file `.pth` từ `Model_Weights.zip`.

2. **GPU không bắt buộc:** Hệ thống tự động fallback sang CPU nếu không có NVIDIA GPU. Tuy nhiên, inference sẽ chậm hơn (~5-10x).

3. **CORS:** Backend đã cấu hình cho phép tất cả origins (`allow_origins=["*"]`) để tiện demo. Trong production cần giới hạn.

4. **Database:** Tự động tạo file `oct_app.db` khi khởi động lần đầu. Chạy `python seed_data.py` để có dữ liệu demo.

---

## 📊 Các Model AI Có Sẵn

| File | Kiến trúc | Kích thước |
|------|-----------|-----------|
| `Resnet50.pth` | ResNet50 Multi-Task UNet | ~385 MB |
| `Vanilla.pth` | Vanilla Multi-Task UNet | ~358 MB |
| `Unet.pth` | UNet++ Multi-Task | ~195 MB |
| `effb3.pth` | EfficientNet-B3 UNet | ~147 MB |

---

## 📞 Liên Hệ

Nếu có vấn đề khi chạy hệ thống, vui lòng liên hệ:
- **Email:** [Điền email]
- **SĐT:** [Điền SĐT]
