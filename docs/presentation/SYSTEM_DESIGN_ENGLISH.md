# V. System Design and Implementation

## 1. AI Model Integration

### 1.1 Multi-Model Architecture

RetinaAI integrates multiple state-of-the-art deep learning architectures for OCT lesion segmentation:

**Available Models:**
- **DeepLabV3+** (Primary): Atrous convolution with ResNet-50 encoder for receptive field expansion
- **ResNet U-Net**: Encoder-decoder with residual connections for precise segmentation
- **U-Net++**: Dense skip connections for multi-scale feature fusion
- **EfficientNet-B3 U-Net**: Lightweight backbone for resource-constrained environments
- **Vanilla U-Net**: Baseline architecture for performance comparison

**Model Registry Pattern:**
```
Model Selection → Dynamic Loading → Weight Initialization → Inference Ready
```

Each model is registered with:
- Module path for dynamic importing
- Architecture class definition
- Pre-trained weight location
- Configurable hyperparameters (dropout, channels, classes)

### 1.2 System Integration Interface

**Component Interaction:**
```
Frontend (Next.js)
    ↓ (HTTP/REST with CORS)
API Layer (FastAPI Endpoints)
    ↓ (Pydantic validation)
Service Layer (Preprocessing, Inference, Postprocessing)
    ↓ (PyTorch model execution)
PyTorch GPU/CPU Runtime
    ↓ (Base64 encoded output)
Response: Classification + Segmentation Mask
```

**Key Integration Points:**

1. **Request Layer**: Upload OCT image (PNG, JPG, JPEG, TIFF) via multipart/form-data
2. **Processing Layer**: Automatic device selection (GPU/CPU), model loading
3. **Output Layer**: Base64-encoded segmentation mask + confidence score
4. **Database Layer**: SQLAlchemy ORM for patient/scan record persistence

### 1.3 Data Exchange Mechanism

**Request Schema:**
```json
{
  "file": "binary image data (< 50MB)"
}
```

**Response Schema:**
```json
{
  "label": "Normal|AMD|DME",
  "confidence": 0.85,
  "mask_base64": "iVBORw0KGgo...",
  "processing_time_ms": 245
}
```

**Synchronous Processing Pipeline:**
- Input validation → Image preprocessing → Model inference → Mask generation → JSON response

---

## 2. Data Flow and Processing

### 2.1 Complete Data Flow Architecture

```
INPUT STAGE
├── Image Upload (OCT scan)
├── File validation (type, size)
└── Binary to NumPy array conversion

PREPROCESSING STAGE
├── Grayscale normalization
├── Resize to 512×512
├── Intensity normalization [0, 1]
├── Standardization (mean/std)
└── Batch dimension addition

INFERENCE STAGE
├── Device selection (GPU/CPU)
├── Model forward pass
├── Output: Classification logits + Segmentation mask
└── Confidence score computation

POSTPROCESSING STAGE
├── Argmax for class prediction
├── Mask thresholding
├── Morphological operations (optional)
└── Base64 PNG encoding

OUTPUT STAGE
├── JSON response construction
├── Database record creation
└── HTTP response delivery
```

### 2.2 Detailed Processing Steps

**Step 1: Image Preprocessing**
- Input: Raw OCT image (variable resolution)
- Normalization: Convert to [0, 1] range
- Standardization: Apply ImageNet statistics
- Augmentation: Test-Time Augmentation (TTA) for stability
- Output: Batch tensor (1, 1, 512, 512) ready for model

**Step 2: AI Model Inference**
- Model Selection: Load from registry based on configuration
- GPU Acceleration: CUDA-enabled PyTorch on available GPU
- Batch Processing: Ready for future multi-image batching
- Output Shapes:
  - Classification: (1, 3) logits → softmax → class probabilities
  - Segmentation: (1, 2, 512, 512) → argmax → binary mask

**Step 3: Result Postprocessing**
- Class Mapping: Argmax to ["Normal", "AMD", "DME"]
- Confidence Scoring: Max softmax probability
- Mask Generation: Upscale to original resolution
- Visualization: Apply colormap for clinical display
- Encoding: PNG compression + Base64 for JSON embedding

**Step 4: Data Persistence**
- Patient Record: Create if new, link if existing
- Scan Metadata: Store timestamp, model version, confidence
- Image Storage: Save original + mask to filesystem
- Database Commit: SQLAlchemy ORM transaction

### 2.3 Data Flow Diagram

```
┌─────────────────┐
│  OCT Image      │
│  (PNG/JPG)      │
└────────┬────────┘
         │
         ▼
    ┌─────────────────────────┐
    │ Validation              │
    │ - File type check       │
    │ - Size validation       │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Preprocessing           │
    │ - Resize 512×512        │
    │ - Normalization         │
    │ - Standardization       │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ AI Model Selection      │
    │ - DeepLabV3+ (default)  │
    │ - GPU/CPU execution     │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Inference               │
    │ - Classification        │
    │ - Segmentation          │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Postprocessing          │
    │ - Mask generation       │
    │ - Base64 encoding       │
    │ - Result formatting     │
    └─────────┬───────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Response                │
    │ {label, confidence,     │
    │  mask_base64}           │
    └─────────────────────────┘
```

### 2.4 Database Schema

**OCTScan Table:**
| Column | Type | Purpose |
|--------|------|---------|
| id | Primary Key | Unique identifier |
| patient_id | Foreign Key | Link to patient |
| image_path | String | Original image storage |
| mask_path | String | Generated mask storage |
| classification | String | Lesion type (Normal/AMD/DME) |
| confidence | Float | Classification confidence |
| model_version | String | Model architecture used |
| processing_time | Float | Inference duration (ms) |
| created_at | DateTime | Analysis timestamp |

---

## 3. Deployment Strategy

### 3.1 Deployment Architecture

**Multi-Tier Deployment Model:**

```
┌────────────────────────────────────────────────────────────┐
│           Production Environment                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  Load        │         │  Load        │                 │
│  │  Balancer    │         │  Balancer    │  (Nginx)        │
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
│         │  Shared Storage  │                               │
│         │  (SQLite/PG)     │                               │
│         │  Image Storage   │                               │
│         └──────────────────┘                               │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 3.2 Deployment Environments

**Development:**
- Local Docker Compose (backend + frontend)
- SQLite database
- CPU-based inference
- Hot-reload enabled

**Staging:**
- Docker containers on staging server
- PostgreSQL database
- GPU-accelerated inference
- HTTPS enabled
- Monitoring stack (optional)

**Production:**
- Kubernetes orchestration (optional)
- Multi-node API backend with load balancing
- PostgreSQL with replication
- GPU nodes for inference scaling
- CDN for static assets
- Monitoring, logging, alerting

### 3.3 Deployment Procedures

#### A. Local Machine Deployment (Recommended)

**Step 1: Prepare Environment**
```bash
# Clone project
git clone <repository-url>
cd capstone_code/Multitask_test

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

**Step 2: Install Backend**
```bash
# Install backend dependencies
cd backend_2.0
pip install -r requirements.txt

# Create .env file from .env.example
cp .env.example .env

# Configure DATABASE_URL (leave as SQLite)
# DATABASE_URL=sqlite:///./oct_app.db
```

**Step 3: Start Backend Server**
```bash
# Run FastAPI server with auto-reload
cd backend_2.0
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend available at http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

**Step 4: Install Frontend**
```bash
# Open new terminal
cd UX
npm install  # or pnpm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

**Step 5: Start Frontend Server**
```bash
# Run Next.js development server
npm run dev  # or pnpm dev

# Frontend available at http://localhost:3000
```

**Step 6: Verify System**
```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check frontend-backend connectivity
# Open http://localhost:3000 in browser
```

**Local Deployment Benefits:**
- ✅ Easy debugging and development
- ✅ No Docker required, saves resources
- ✅ Automatic hot-reload on code changes
- ✅ Suitable for development and testing
- ✅ Direct GPU setup (CUDA/cuDNN)

---

#### B. Docker-Based Deployment (If Needed)

**Step 1: Build Container Images**
```bash
# Backend image with GPU support
docker build -f Dockerfile -t oct-api:v1.0 .

# Frontend image
docker build -f UX/Dockerfile -t oct-ui:v1.0 ./UX
```

**Step 2: Push to Registry (Optional)**
```bash
docker push myregistry.azurecr.io/oct-api:v1.0
docker push myregistry.azurecr.io/oct-ui:v1.0
```

**Step 3: Deploy with Docker Compose**
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

**Step 4: Start Docker Containers**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Step 5: Verify Deployment**
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Test analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@test_oct.png"
```

**When to Use Docker:**
- 📦 Need to deploy on different machines
- 📦 Ensure consistent deployment environment
- 📦 Using Kubernetes orchestration
- 📦 Deploying to cloud (AWS, GCP, Azure)

### 3.4 Environment Configuration

**Production Environment Variables:**
```env
# Database
DATABASE_URL=postgresql://user:password@prod-db.azure.com:5432/oct_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# API Configuration
API_TITLE=RetinaAI OCT Analysis
API_VERSION=1.0.0
LOG_LEVEL=INFO

# Model Configuration
DEFAULT_MODEL=deeplabv3plus
DEEPLAB_WEIGHT_PATH=/app/weights/deeplabv3_best_model.pth
USE_GPU=True
CUDA_VISIBLE_DEVICES=0,1

# File Upload
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_EXTENSIONS=png,jpg,jpeg,tiff

# CORS
CORS_ORIGINS=https://retinaai.com,https://api.retinaai.com

# Security
API_KEY_ENABLED=True
JWT_SECRET=your-secret-key-here
```

---

## 4. Scalability and Maintenance

### 4.1 System Scalability Design

**Horizontal Scaling:**

1. **Backend Scaling**
   - Stateless API servers → Add/remove instances via load balancer
   - Connection pooling → Scale database connections
   - Request queuing → Handle burst loads
   - GPU resource sharing → Multiple inference instances per GPU

2. **Database Scaling**
   - Read replicas → Distribute read-heavy queries
   - Write primary → Centralized transaction handling
   - Connection pooling → Efficient resource utilization
   - Partitioning → Split large tables by patient/date

3. **Storage Scaling**
   - Object storage (S3/Azure Blob) → Unlimited image storage
   - CDN distribution → Global image access
   - Archive strategy → Move old images to cold storage
   - Retention policy → Automatic cleanup of expired scans

**Vertical Scaling:**
- GPU upgrade → Larger GPU for faster inference
- Memory expansion → Support larger batch sizes
- CPU upgrade → Faster preprocessing
- SSD upgrade → Faster I/O operations

### 4.2 Version Management

**Model Versioning:**

```
Version Format: major.minor.patch-identifier
Example: 1.0.0-deeplabv3plus

Structure:
weights/
├── v1.0.0/
│   ├── deeplabv3_best_model.pth
│   ├── checkpoint_epoch_99.pth
│   └── metadata.json
├── v1.1.0/
│   └── [updated weights]
└── v2.0.0/
    └── [production ready]
```

**Database Migration Strategy:**

- Version control: Track schema changes in git
- Backup before upgrade: Full database backup
- Rollback plan: Keep previous schema definitions
- Testing: Validate migrations on staging first

**API Versioning:**

```
/api/v1/analyze      # Version 1 (stable)
/api/v2/analyze      # Version 2 (new features)
/api/v3/analyze      # Version 3 (beta)
```

### 4.3 Maintenance Procedures

**Regular Maintenance Tasks:**

| Task | Frequency | Duration |
|------|-----------|----------|
| Database backup | Daily | < 5 min |
| Log rotation | Weekly | N/A |
| Dependency updates | Monthly | 2-4 hours |
| Security patches | As needed | 1-2 hours |
| Model retraining | Quarterly | 24-48 hours |
| Performance tuning | Bi-monthly | 2-3 hours |
| Capacity planning | Monthly | 1 hour |

**Update Deployment Strategy:**

1. **Patch Release (1.0.0 → 1.0.1)**
   - Bug fixes only
   - No database migration
   - Rolling update (blue-green)
   - Automatic failover

2. **Minor Release (1.0.0 → 1.1.0)**
   - New features, backward compatible
   - Optional database migration
   - Canary deployment (10% → 50% → 100%)
   - A/B testing enabled

3. **Major Release (1.0.0 → 2.0.0)**
   - Breaking changes possible
   - Required database migration
   - Scheduled maintenance window
   - Data backup mandatory

### 4.4 Monitoring and Observability

**Key Metrics:**

```
Infrastructure:
├── CPU utilization (target: < 70%)
├── Memory usage (target: < 80%)
├── GPU utilization (target: > 80%)
├── Disk I/O latency (target: < 10ms)
└── Network throughput (target: > 100Mbps)

Application:
├── Request latency (p95: < 500ms)
├── Error rate (target: < 0.1%)
├── Model inference time (target: < 300ms)
├── Database query time (target: < 50ms)
└── API availability (target: > 99.9%)

Model:
├── Classification accuracy
├── Segmentation Dice score
├── Inference throughput (images/sec)
└── GPU memory usage
```

**Logging Strategy:**

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

### 4.5 Disaster Recovery

**Backup Strategy:**

- **Database**: Daily incremental, weekly full backup
- **Model weights**: Version control + backup storage
- **Patient data**: Encrypted backup to secondary location
- **Recovery time objective (RTO)**: < 1 hour
- **Recovery point objective (RPO)**: < 15 minutes

**Failover Mechanism:**

1. Health check fails → Automatic failover to standby
2. Multi-region replication → Geographic redundancy
3. Database replication lag < 5 seconds
4. DNS failover < 30 seconds
5. Total downtime < 1 minute

---

## Summary

RetinaAI demonstrates enterprise-grade system design with:
- **Modular AI integration**: Multiple model architectures with dynamic selection
- **Efficient data processing**: Optimized pipeline from image to clinical insights
- **Production-ready deployment**: Containerized, scalable, multi-environment support
- **Maintainable architecture**: Versioning, monitoring, disaster recovery
- **Future-proof design**: Horizontal scaling, model updates, performance optimization

This foundation ensures clinician adoption while maintaining scientific rigor and operational excellence.
