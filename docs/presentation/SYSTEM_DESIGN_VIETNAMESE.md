# V. Thiết Kế và Triển Khai Hệ Thống

## 1. Tích Hợp Mô Hình AI

### 1.1 Kiến Trúc Đa Mô Hình

RetinaAI tích hợp nhiều kiến trúc học sâu hiện đại để phân đoạn các tổn thương võng mạc trong ảnh OCT:

**Các Mô Hình Khả Dụng:**

- **ResNet U-Net**: Encoder-decoder với kết nối residual cho phân đoạn chính xác
- **U-Net++**: Dense skip connections cho fusion đặc trưng đa tỷ lệ
- **EfficientNet-B3 U-Net**: Backbone nhẹ cho môi trường có tài nguyên hạn chế
- **Vanilla U-Net**: Kiến trúc baseline để so sánh hiệu năng

**Mẫu Đăng Ký Mô Hình:**
```
Lựa Chọn Mô Hình → Tải Động → Khởi Tạo Trọng Số → Sẵn Sàng Suy Diễn
```

Mỗi mô hình được đăng ký với:
- Đường dẫn module để import động
- Định nghĩa lớp kiến trúc
- Vị trí trọng số được huấn luyện trước
- Các siêu tham số cấu hình (dropout, channels, classes)

### 1.2 Giao Diện Tích Hợp Hệ Thống

**Tương Tác Giữa Các Thành Phần:**
```
Frontend (Next.js)
    ↓ (HTTP/REST với CORS)
API Layer (FastAPI Endpoints)
    ↓ (xác thực Pydantic)
Service Layer (Tiền xử lý, Suy diễn, Xử lý sau)
    ↓ (thực thi mô hình PyTorch)
PyTorch GPU/CPU Runtime
    ↓ (đầu ra được mã hóa Base64)
Response: Phân loại + Mặt Nạ Phân Đoạn
```

**Các Điểm Tích Hợp Chính:**

1. **Tầng Yêu Cầu**: Tải ảnh OCT (PNG, JPG, JPEG, TIFF) qua multipart/form-data
2. **Tầng Xử Lý**: Lựa chọn thiết bị tự động (GPU/CPU), tải mô hình
3. **Tầng Đầu Ra**: Mặt nạ phân đoạn được mã hóa Base64 + điểm tin cậy
4. **Tầng Cơ Sở Dữ Liệu**: SQLAlchemy ORM để lưu trữ bản ghi bệnh nhân/quét

### 1.3 Cơ Chế Trao Đổi Dữ Liệu

**Lược Đồ Yêu Cầu:**
```json
{
  "file": "dữ liệu ảnh nhị phân (< 50MB)"
}
```

**Lược Đồ Phản Hồi:**
```json
{
  "label": "Normal|AMD|DME",
  "confidence": 0.85,
  "mask_base64": "iVBORw0KGgo...",
  "processing_time_ms": 245
}
```

**Đường Ống Xử Lý Đồng Bộ:**
- Xác thực đầu vào → Tiền xử lý ảnh → Suy diễn mô hình → Tạo mặt nạ → Phản hồi JSON

---

## 2. Luồng Dữ Liệu và Xử Lý

### 2.1 Kiến Trúc Luồng Dữ Liệu Hoàn Chỉnh

```
GIAI ĐOẠN NHẬP
├── Tải Lên Ảnh (quét OCT)
├── Xác thực tệp (loại, kích thước)
└── Chuyển đổi nhị phân thành mảng NumPy

GIAI ĐOẠN TIỀN XỬ LÝ
├── Chuẩn hóa thang xám
├── Thay đổi kích thước thành 512×512
├── Chuẩn hóa cường độ [0, 1]
├── Tiêu chuẩn hóa (mean/std)
└── Thêm chiều batch

GIAI ĐOẠN SUY DIỄN
├── Lựa chọn thiết bị (GPU/CPU)
├── Forward pass mô hình
├── Đầu ra: Logits phân loại + Mặt nạ phân đoạn
└── Tính toán điểm tin cậy

GIAI ĐOẠN XỬ LÝ SAU
├── Argmax để dự đoán lớp
├── Ngưỡng hóa mặt nạ
├── Các phép toán hình thái (tùy chọn)
└── Mã hóa PNG Base64

GIAI ĐOẠN ĐẦU RA
├── Xây dựng phản hồi JSON
├── Tạo bản ghi cơ sở dữ liệu
└── Phân phối phản hồi HTTP
```

### 2.2 Các Bước Xử Lý Chi Tiết

**Bước 1: Tiền Xử Lý Ảnh**
- Đầu vào: Ảnh OCT thô (độ phân giải thay đổi)
- Chuẩn hóa: Chuyển đổi sang phạm vi [0, 1]
- Tiêu chuẩn hóa: Áp dụng thống kê ImageNet
- Augmentation: Test-Time Augmentation (TTA) để tăng ổn định
- Đầu ra: Tensor batch (1, 1, 512, 512) sẵn sàng cho mô hình

**Bước 2: Suy Diễn Mô Hình AI**
- Lựa Chọn Mô Hình: Tải từ registry dựa trên cấu hình
- Tăng Tốc GPU: PyTorch hỗ trợ CUDA trên GPU khả dụng
- Xử Lý Batch: Sẵn sàng để xử lý đa ảnh trong tương lai
- Hình Dạng Đầu Ra:
  - Phân loại: (1, 3) logits → softmax → xác suất lớp
  - Phân đoạn: (1, 2, 512, 512) → argmax → mặt nạ nhị phân

**Bước 3: Xử Lý Kết Quả Sau**
- Ánh Xạ Lớp: Argmax thành ["Normal", "AMD", "DME"]
- Điểm Tin Cậy: Xác suất softmax tối đa
- Tạo Mặt Nạ: Phóng to lên độ phân giải gốc
- Hình Ảnh Hóa: Áp dụng bảng màu để hiển thị lâm sàng
- Mã Hóa: Nén PNG + Base64 để nhúng JSON

**Bước 4: Lưu Trữ Dữ Liệu**
- Bản Ghi Bệnh Nhân: Tạo nếu mới, liên kết nếu tồn tại
- Siêu Dữ Liệu Quét: Lưu trữ dấu thời gian, phiên bản mô hình, tin cậy
- Lưu Trữ Ảnh: Lưu gốc + mặt nạ vào hệ thống tệp
- Commit Cơ Sở Dữ Liệu: Giao dịch SQLAlchemy ORM

### 2.3 Biểu Đồ Luồng Dữ Liệu

```
┌─────────────────┐
│  Ảnh OCT        │
│  (PNG/JPG)      │
└────────┬────────┘
         │
         ▼
    ┌─────────────────────────┐
    │ Xác Thực                │
    │ - Kiểm tra loại tệp     │
    │ - Xác thực kích thước   │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Tiền Xử Lý              │
    │ - Thay đổi 512×512      │
    │ - Chuẩn hóa             │
    │ - Tiêu chuẩn hóa        │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Lựa Chọn Mô Hình AI     │
    │ - DeepLabV3+ (mặc định) │
    │ - Thực thi GPU/CPU      │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Suy Diễn                │
    │ - Phân loại             │
    │ - Phân đoạn             │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Xử Lý Sau               │
    │ - Tạo mặt nạ            │
    │ - Mã hóa Base64         │
    │ - Định dạng kết quả     │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Phản Hồi                │
    │ {label, confidence,     │
    │  mask_base64}           │
    └─────────────────────────┘
```

### 2.4 Lược Đồ Cơ Sở Dữ Liệu

**Bảng OCTScan:**
| Cột | Loại | Mục Đích |
|-----|------|---------|
| id | Khóa chính | Định danh duy nhất |
| patient_id | Khóa ngoại | Liên kết bệnh nhân |
| image_path | Chuỗi | Lưu trữ ảnh gốc |
| mask_path | Chuỗi | Lưu trữ mặt nạ được tạo |
| classification | Chuỗi | Loại tổn thương (Normal/AMD/DME) |
| confidence | Float | Tin cậy phân loại |
| model_version | Chuỗi | Kiến trúc mô hình được sử dụng |
| processing_time | Float | Thời gian suy diễn (ms) |
| created_at | DateTime | Dấu thời gian phân tích |

---

## 3. Chiến Lược Triển Khai

### 3.1 Kiến Trúc Triển Khai

**Mô Hình Triển Khai Đa Tầng:**

```
┌────────────────────────────────────────────────────────────┐
│           Môi Trường Sản Xuất                              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  Cân Bằng    │         │  Cân Bằng    │                 │
│  │  Tải         │         │  Tải         │  (Nginx)        │
│  └──────┬───────┘         └──────┬───────┘                 │
│         │                        │                         │
│  ┌──────▼────────┐       ┌──────▼────────┐                 │
│  │  Frontend     │       │  Frontend     │  (Next.js)      │
│  │  Container 1  │       │  Container 2  │                 │
│  └──────┬────────┘       └──────┬────────┘                 │
│         │                       │                          │
│         └───────────┬───────────┘                          │
│                     │ (HTTP/REST)                          │
│                     ▼                                      │
│         ┌────────────────────────┐                         │ 
│         │  API Gateway / LB      │                         │
│         │  (Reverse Proxy)       │                         │
│         └────────────┬───────────┘                         │
│                      │                                     │
│  ┌───────────────────┼───────────────────┐                 │
│  │                   │                   │                 │
│  ▼                   ▼                   ▼                 │
│  Backend       Backend            Backend                  │
│  Container 1   Container 2        Container N (GPU)        │
│  (FastAPI)     (FastAPI)          (FastAPI)                │
│  │              │                 │                        │
│  └──────────────┴─────────────────┘                        │
│                 │                                          │
│                 ▼                                          │
│         ┌──────────────────┐                               │
│         │  Lưu Trữ Chia Sẻ │                               │
│         │  (SQLite/PG)     │                               │
│         │  Lưu Trữ Ảnh     │                               │
│         └──────────────────┘                               │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 3.2 Môi Trường Triển Khai

**Phát Triển:**
- Docker Compose cục bộ (backend + frontend)
- Cơ sở dữ liệu SQLite
- Suy diễn dựa trên CPU
- Hot-reload được kích hoạt

**Staging:**
- Các container Docker trên máy chủ staging
- Cơ sở dữ liệu PostgreSQL
- Suy diễn tăng tốc GPU
- HTTPS được kích hoạt
- Stack giám sát (tùy chọn)

**Sản Xuất:**
- Điều phối Kubernetes (tùy chọn)
- Nhiều nút backend API với cân bằng tải
- PostgreSQL với sao chép
- Các nút GPU để mở rộng suy diễn
- CDN cho các tài sản tĩnh
- Giám sát, ghi nhật ký, cảnh báo

### 3.3 Quy Trình Triển Khai

#### A. Triển Khai Trên Máy Local (Khuyến Nghị)

**Bước 1: Chuẩn Bị Môi Trường**
```bash
# Clone project
git clone <repository-url>
cd capstone_code/Multitask_test

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

**Bước 2: Cài Đặt Backend**
```bash
# Cài đặt dependencies backend
cd backend_2.0
pip install -r requirements.txt

# Tạo file .env từ .env.example
cp .env.example .env

# Cấu hình DATABASE_URL (để trống cho SQLite)
# DATABASE_URL=sqlite:///./oct_app.db
```

**Bước 3: Khởi Động Backend**
```bash
# Chạy FastAPI server
cd backend_2.0
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend sẽ chạy tại http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

**Bước 4: Cài Đặt Frontend**
```bash
# Mở terminal mới
cd UX
npm install  # hoặc pnpm install

# Tạo file .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

**Bước 5: Khởi Động Frontend**
```bash
# Chạy Next.js development server
npm run dev  # hoặc pnpm dev

# Frontend sẽ chạy tại http://localhost:3000
```

**Bước 6: Kiểm Tra Hệ Thống**
```bash
# Kiểm tra backend health
curl http://localhost:8000/api/v1/health

# Kiểm tra kết nối frontend-backend
# Truy cập http://localhost:3000 trong trình duyệt
```

**Lợi Ích Triển Khai Local:**
- ✅ Dễ dàng debug và phát triển
- ✅ Không cần Docker, tiết kiệm tài nguyên
- ✅ Hot-reload tự động khi thay đổi code
- ✅ Thích hợp cho phát triển và staging
- ✅ Cài đặt GPU trực tiếp (CUDA/cuDNN)

---

#### B. Triển Khai Dựa Trên Docker (Nếu Cần)

**Bước 1: Xây Dựng Ảnh Container**
```bash
# Ảnh backend với hỗ trợ GPU
docker build -f Dockerfile -t oct-api:v1.0 .

# Ảnh frontend
docker build -f UX/Dockerfile -t oct-ui:v1.0 ./UX
```

**Bước 2: Đẩy Đến Registry (Tùy Chọn)**
```bash
docker push myregistry.azurecr.io/oct-api:v1.0
docker push myregistry.azurecr.io/oct-ui:v1.0
```

**Bước 3: Triển Khai Với Docker Compose**
```yaml
version: '3.8'
services:
  backend:
    image: oct-api:v1.0
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/oct_db
      - CUDA_VISIBLE_DEVICES=0,1
    volumes:
      - ./weights:/app/weights:ro
      - ./storage:/app/storage
    networks:
      - oct-network

  frontend:
    image: oct-ui:v1.0
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000/api/v1
    networks:
      - oct-network

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=oct_db
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - db_data:/var/lib/postgresql/data

networks:
  oct-network:
    driver: bridge

volumes:
  db_data:
```

**Bước 4: Khởi Động Docker Containers**
```bash
# Khởi động tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng services
docker-compose down
```

**Bước 5: Xác Minh Triển Khai**
```bash
# Kiểm tra sức khỏe
curl http://localhost:8000/api/v1/health

# Phân tích thử nghiệm
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@test_oct.png"
```

**Khi Nào Sử Dụng Docker:**
- 📦 Cần triển khai trên máy chủ khác
- 📦 Cần đảm bảo môi trường nhất quán
- 📦 Sử dụng Kubernetes orchestration
- 📦 Triển khai lên cloud (AWS, GCP, Azure)

### 3.4 Cấu Hình Môi Trường

**Các Biến Môi Trường Sản Xuất:**
```env
# Cơ Sở Dữ Liệu
DATABASE_URL=postgresql://user:password@prod-db.azure.com:5432/oct_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Cấu Hình API
API_TITLE=RetinaAI OCT Analysis
API_VERSION=1.0.0
LOG_LEVEL=INFO

# Cấu Hình Mô Hình
DEFAULT_MODEL=deeplabv3plus
DEEPLAB_WEIGHT_PATH=/app/weights/deeplabv3_best_model.pth
USE_GPU=True
CUDA_VISIBLE_DEVICES=0,1

# Tải Lên Tệp
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_EXTENSIONS=png,jpg,jpeg,tiff

# CORS
CORS_ORIGINS=https://retinaai.com,https://api.retinaai.com

# Bảo Mật
API_KEY_ENABLED=True
JWT_SECRET=your-secret-key-here
```

---

## 4. Khả Năng Mở Rộng và Bảo Trì

### 4.1 Thiết Kế Khả Năng Mở Rộng của Hệ Thống

**Mở Rộng Ngang:**

1. **Mở Rộng Backend**
   - Máy chủ API không trạng thái → Thêm/xóa instances qua cân bằng tải
   - Kết nối pooling → Mở rộng kết nối cơ sở dữ liệu
   - Hàng đợi yêu cầu → Xử lý tải cao
   - Chia sẻ tài nguyên GPU → Nhiều instances suy diễn mỗi GPU

2. **Mở Rộng Cơ Sở Dữ Liệu**
   - Replica đọc → Phân phối truy vấn có lượng đọc lớn
   - Primary ghi → Xử lý giao dịch tập trung
   - Kết nối pooling → Sử dụng tài nguyên hiệu quả
   - Phân vùng → Chia bảng lớn theo bệnh nhân/ngày

3. **Mở Rộng Lưu Trữ**
   - Lưu trữ đối tượng (S3/Azure Blob) → Lưu trữ ảnh không giới hạn
   - Phân phối CDN → Truy cập ảnh toàn cầu
   - Chiến lược lưu trữ → Di chuyển ảnh cũ đến lưu trữ lạnh
   - Chính sách lưu giữ → Dọn dẹp tự động các quét hết hạn

**Mở Rộng Dọc:**
- Nâng cấp GPU → GPU lớn hơn để suy diễn nhanh hơn
- Mở rộng bộ nhớ → Hỗ trợ kích thước batch lớn hơn
- Nâng cấp CPU → Tiền xử lý nhanh hơn
- Nâng cấp SSD → Thao tác I/O nhanh hơn

### 4.2 Quản Lý Phiên Bản

**Phiên Bản Mô Hình:**

```
Định Dạng Phiên Bản: major.minor.patch-identifier
Ví Dụ: 1.0.0-deeplabv3plus

Cấu Trúc:
weights/
├── v1.0.0/
│   ├── deeplabv3_best_model.pth
│   ├── checkpoint_epoch_99.pth
│   └── metadata.json
├── v1.1.0/
│   └── [trọng số cập nhật]
└── v2.0.0/
    └── [sẵn sàng sản xuất]
```

**Chiến Lược Chuyển Đổi Cơ Sở Dữ Liệu:**

- Kiểm soát phiên bản: Theo dõi thay đổi lược đồ trong git
- Sao lưu trước nâng cấp: Sao lưu cơ sở dữ liệu toàn bộ
- Kế hoạch khôi phục: Giữ định nghĩa lược đồ trước đó
- Kiểm tra: Xác thực chuyển đổi trên staging trước

**Phiên Bản API:**

```
/api/v1/analyze      # Phiên bản 1 (ổn định)
/api/v2/analyze      # Phiên bản 2 (tính năng mới)
/api/v3/analyze      # Phiên bản 3 (beta)
```

### 4.3 Quy Trình Bảo Trì

**Các Tác Vụ Bảo Trì Thường Xuyên:**

| Tác Vụ | Tần Suất | Thời Lượng |
|--------|---------|-----------|
| Sao lưu cơ sở dữ liệu | Hàng ngày | < 5 phút |
| Xoay nhật ký | Hàng tuần | N/A |
| Cập nhật phụ thuộc | Hàng tháng | 2-4 giờ |
| Vá bảo mật | Khi cần | 1-2 giờ |
| Huấn luyện lại mô hình | Hàng quý | 24-48 giờ |
| Tinh chỉnh hiệu năng | Hai tháng | 2-3 giờ |
| Lập kế hoạch dung lượng | Hàng tháng | 1 giờ |

**Chiến Lược Triển Khai Cập Nhật:**

1. **Phát Hành Bản Vá (1.0.0 → 1.0.1)**
   - Chỉ sửa lỗi
   - Không chuyển đổi cơ sở dữ liệu
   - Cập nhật liên tục (blue-green)
   - Chuyển đổi tự động

2. **Phát Hành Phụ (1.0.0 → 1.1.0)**
   - Tính năng mới, tương thích ngược
   - Chuyển đổi cơ sở dữ liệu tùy chọn
   - Triển khai Canary (10% → 50% → 100%)
   - Kiểm tra A/B được kích hoạt

3. **Phát Hành Chính (1.0.0 → 2.0.0)**
   - Các thay đổi ngắt có thể xảy ra
   - Chuyển đổi cơ sở dữ liệu bắt buộc
   - Cửa sổ bảo trì được lên kế hoạch
   - Sao lưu dữ liệu bắt buộc

### 4.4 Giám Sát và Quan Sát

**Các Số Liệu Chính:**

```
Cơ Sở Hạ Tầng:
├── Sử dụng CPU (mục tiêu: < 70%)
├── Sử dụng bộ nhớ (mục tiêu: < 80%)
├── Sử dụng GPU (mục tiêu: > 80%)
├── Độ trễ I/O đĩa (mục tiêu: < 10ms)
└── Thông lượng mạng (mục tiêu: > 100Mbps)

Ứng Dụng:
├── Độ trễ yêu cầu (p95: < 500ms)
├── Tỷ lệ lỗi (mục tiêu: < 0.1%)
├── Thời gian suy diễn mô hình (mục tiêu: < 300ms)
├── Thời gian truy vấn cơ sở dữ liệu (mục tiêu: < 50ms)
└── Tính khả dụng API (mục tiêu: > 99.9%)

Mô Hình:
├── Độ chính xác phân loại
├── Điểm Dice phân đoạn
├── Thông lượng suy diễn (ảnh/giây)
└── Sử dụng bộ nhớ GPU
```

**Chiến Lược Ghi Nhật Ký:**

```json
{
  "timestamp": "2024-04-22T10:30:45.123Z",
  "level": "INFO",
  "service": "backend",
  "event": "inference_complete",
  "details": {
    "patient_id": "PAT123",
    "model": "deeplabv3plus",
    "confidence": 0.92,
    "inference_time_ms": 245,
    "gpu_memory_mb": 1024
  }
}
```

### 4.5 Khôi Phục Thảm Họa

**Chiến Lược Sao Lưu:**

- **Cơ Sở Dữ Liệu**: Tăng dần hàng ngày, sao lưu toàn bộ hàng tuần
- **Trọng Số Mô Hình**: Kiểm soát phiên bản + lưu trữ sao lưu
- **Dữ Liệu Bệnh Nhân**: Sao lưu được mã hóa đến vị trí thứ cấp
- **Mục Tiêu Thời Gian Khôi Phục (RTO)**: < 1 giờ
- **Mục Tiêu Điểm Khôi Phục (RPO)**: < 15 phút

**Cơ Chế Chuyển Đổi Dự Phòng:**

1. Kiểm tra sức khỏe thất bại → Chuyển đổi tự động đến dự phòng
2. Sao chép đa khu vực → Dự phòng địa lý
3. Độ trễ sao chép cơ sở dữ liệu < 5 giây
4. Chuyển đổi DNS < 30 giây
5. Tổng thời gian chết < 1 phút

---

## Tóm Tắt

RetinaAI thể hiện thiết kế hệ thống cấp doanh nghiệp với:
- **Tích hợp AI mô-đun**: Nhiều kiến trúc mô hình có lựa chọn động
- **Xử lý dữ liệu hiệu quả**: Đường ống được tối ưu hóa từ ảnh đến thông tin lâm sàng
- **Triển khai sản xuất sẵn sàng**: Containerized, có thể mở rộng, hỗ trợ đa môi trường
- **Kiến trúc dễ bảo trì**: Quản lý phiên bản, giám sát, khôi phục thảm họa
- **Thiết kế hướng tương lai**: Mở rộng ngang, cập nhật mô hình, tối ưu hóa hiệu năng

Nền tảng này đảm bảo khi áp dụng bác sĩ lâm sàng trong khi duy trì độ chính xác khoa học và xuất sắc hoạt động.
