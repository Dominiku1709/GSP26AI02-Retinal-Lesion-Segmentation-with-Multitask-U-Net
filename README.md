# RetinaAI - OCT Retinal Lesion Segmentation & Classification System

**RetinaAI** is an AI-powered diagnostic system for automated detection and segmentation of retinal pathologies in Optical Coherence Tomography (OCT) scans. It combines a FastAPI backend with state-of-the-art deep learning models and a professional Next.js frontend for clinician use.

## Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Key Components](#key-components)
- [Data Flow](#data-flow)

---

## Project Overview

**Purpose:** Automated diagnosis of retinal diseases from OCT scans by detecting and segmenting three primary lesion types:
- **Normal** - Healthy retinal tissue
- **AMD** - Age-related macular degeneration marker (Drusen)
- **DME** - Diabetic macular edema

**Key Features:**
GPU-accelerated PyTorch inference for real-time analysis  
Multi-model support (4 architectures available)  
Aspect-ratio-preserving resize with zero-padding  
Morphological postprocessing (connected-component noise filtering)  
Patient data persistence with SQLite ORM  
Professional web UI with patient management  
Segmentation mask visualization & PDF report generation  
RESTful API with comprehensive error handling  

---

## System Architecture

```
┌──────────────────────────────────────────┐
│   Frontend: Next.js (Port 3000)          │
│   - React 19 + TypeScript + Tailwind     │
│   - Patient Management Dashboard         │
│   - OCT Image Upload & Analysis          │
│   - PDF Report Generation                │
└──────────────────┬───────────────────────┘
                   │ HTTP/REST + CORS
                   ▼
┌──────────────────────────────────────────┐
│   Backend: FastAPI (Port 8000)           │
│   - /api/analyze    → Image Segmentation │
│   - /api/patients   → Patient CRUD       │
│   - /api/models     → Model Selection    │
│   - /api/health     → System Status      │
└──────────────────┬───────────────────────┘
                   │
        ┌──────────┼──────────┬────────┐
        ▼          ▼          ▼        ▼
    ┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐
    │PyTorch│ │SQLite│ │Storage │ │.pth  │
    │GPU    │ │DB    │ │/Images │ │Weights│
    │/CPU   │ │      │ │        │ │      │
    └────────┘ └──────┘ └────────┘ └──────┘
```

---

## Project Structure

### **Production Code (Essential Files)**

```
Multitask_test/
│
├── backend_2.0/                    # Backend Service
│   ├── requirements.txt               # Python dependencies
│   ├── app/                        # Core Application
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app initialization
│   │   ├── database.py                # SQLAlchemy ORM setup
│   │   ├── models.py                  # Database models (Patient, OCTScan)
│   │   ├── api/
│   │   │   ├── endpoints.py           # API routes: /analyze, /patients, /models, /health
│   │   │   └── schemas.py             # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── preprocess.py          # MONAI image preprocessing
│   │   │   ├── inference.py           # PyTorch inference engine (.pth models)
│   │   │   └── postprocess.py         # Mask visualization & heatmap generation
│   │   └── core/
│   │       └── config.py              # Configuration settings
│   │
│   ├── model_architecture/         # AI Model Definitions
│   │   ├── __init__.py
│   │   ├── model_architecture.py      # Contains all models architectures
│   ├── weights/                    # Pre-trained PyTorch Models (.pth)
│   │   ├── Resnet50.pth               # ResNet50 Multi-Task UNet
│   │   ├── Vanilla.pth                # Vanilla Multi-Task UNet
│   │   ├── Vanillav2.pth              # Vanilla UNet v2 variant
│   │   ├── Unet.pth                   # UNet++ Multi-Task
│   │   └── effb3.pth                  # EfficientNet-B3 UNet
│   │
│   └── storage/                    # Runtime: Uploaded images & generated masks
│
├── UX/                             # Frontend Application
│   ├── package.json                   # Node.js dependencies
│   ├── next.config.mjs                # Next.js configuration
│   ├── tsconfig.json                  # TypeScript settings
│   ├── postcss.config.mjs             # CSS processing
│   ├── project_spec.json              # Project specifications
│   │
│   ├── app/                        # Next.js Pages/Routes
│   │   ├── layout.tsx                 # Root layout (metadata, providers)
│   │   ├── page.tsx                   # Homepage
│   │   ├── globals.css                # Global styles
│   │   └── [other pages]/             # Route pages
│   │
│   ├── components/                 # React Components
│   │   ├── app-sidebar.tsx            # Navigation sidebar
│   │   ├── doctor-header.tsx          # Header with doctor info
│   │   ├── new-patient-modal.tsx      # Patient creation form
│   │   ├── patients/               # Patient management components
│   │   ├── scanner/                # OCT upload & analysis components
│   │   └── ui/                     # Shadcn/UI base components
│   │
│   ├── lib/                        # Utilities & Helpers
│   │   ├── api.ts                     # Backend API communication
│   │   ├── store.tsx                  # Global state management
│   │   └── utils.ts                   # Helper functions
│   │
│   ├── hooks/                      # Custom React Hooks
│   │
│   ├── public/                     # Static Assets
│   │
│   └── styles/                     # Global Styles
│
├── docs/                           # Documentation
│   ├── summary/
│   │   ├── PROJECT_SUMMARY.md         # High-level overview
│   │   ├── PROJECT_ANALYSIS.md        # Deep architecture analysis
│   │   └── INTEGRATION_SUMMARY.md     # Frontend-backend integration status
│   │
│   ├── documentation/
│   │   ├── API_SPECIFICATION.md       # OpenAPI reference
│   │   ├── BACKEND_DOCUMENTATION.md   # Backend setup guide
│   │   └── UX_DOCUMENTATION.md        # UI/UX specifications
│   │
│   ├── configuration/
│   │   ├── DEPLOYMENT_CHECKLIST.md    # Production deployment steps
│   │   ├── ENV_CONFIG_SUMMARY.md      # Environment configuration
│   │   └── FINAL_CHECKLIST.md         # Final verification checklist
│   │
│   └── guides/
│       ├── QUICK_START_GPU.md         # GPU setup quick start
│       ├── IMPLEMENTATION_GUIDE.md    # Implementation reference
│       └── STARTUP_GUIDE.md           # Server startup instructions
│
├── seed_data.py                       # Demo database seeder (5 patients, 10 scans)
├── REQUIREMENTS_CHECK.txt             # Core library checklist
├── README_SUBMISSION.md               # Submission guide for review committee
└── README.md                          # This file
```

---

## Tech Stack

### **Backend**
| Technology | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.115.0 | Web framework (async, automatic API docs) |
| **SQLAlchemy** | 2.0.38 | ORM for database abstraction |
| **SQLite** | Built-in | Default database (swappable to PostgreSQL) |
| **PyTorch** | 2.4.1 | Deep learning framework with GPU support |
| **MONAI** | 1.3.2 | Medical imaging preprocessing |
| **OpenCV** | 4.9.0.80 | Computer vision operations |
| **Uvicorn** | 0.30.0 | ASGI server |

### **Frontend**
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Next.js** | 16.1.6 | React meta-framework (SSR, routing, optimization) |
| **React** | 19.2.4 | UI library |
| **TypeScript** | 5.7.3 | Static typing for JavaScript |
| **Tailwind CSS** | 4.2.0 | Utility-first CSS framework |
| **Shadcn/UI** | Latest | Pre-built accessible components |
| **React Hook Form** | Latest | Form state management |
| **Zod** | Latest | TypeScript-first schema validation |
| **Recharts** | 2.15.0 | React charting library |

### **Infrastructure**
- **GPU Support:** NVIDIA CUDA (RTX 3060+)
- **Inference:** PyTorch (GPU or CPU)
- **Model Format:** .pth (PyTorch checkpoints)

---

## Quick Start

### **Prerequisites**
```bash
# System requirements
- Python 3.9+ (backend)
- Node.js 18+ (frontend)
- NVIDIA GPU with CUDA support (recommended but optional)
- 8GB+ RAM, 2GB+ storage
```

### **Backend Setup**
```bash
cd backend_2.0

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000
# API documentation: http://localhost:8000/docs
```

### **Frontend Setup**
```bash
cd UX

# Install dependencies
npm install

# Run development server
npm run dev
# Application: http://localhost:3000
```

### **Verify Installation**
```bash
# Check backend health
curl http://localhost:8000/api/health

# Check GPU availability & loaded model
curl http://localhost:8000/api/system/gpu-status

# List available models
curl http://localhost:8000/api/models
```

---

## API Reference

All endpoints under `/api/`

### **Analysis Endpoints**

#### `POST /analyze` - Single Image Analysis
**Request:**
```bash
curl -F "file=@oct_image.png" http://localhost:8000/api/analyze
```

**Response:**
```json
{
  "id": 12,
  "lesion_type": "DME",
  "confidence": 0.9412,
  "mask_viz": "data:image/jpeg;base64,/9j/4AAQ...",
  "mask_viz_base64": "...",
  "architecture": "vanilla",
  "filename": "a1b2c3d4-uuid.png",
  "image_url": "http://localhost:8000/images/a1b2c3d4-uuid.png",
  "response_time": 342.15
}
```

### **Patient Management**

#### `POST /patients` - Create Patient
```json
{
  "name": "Nguyen Van An",
  "dob": "1958-03-15",
  "gender": "Male",
  "contact": "0901234567",
  "medical_notes": "Follow-up AMD"
}
```

#### `GET /patients` - List All Patients
#### `GET /patients/{id}` - Get Patient Details
#### `PUT /patients/{id}` - Update Patient

### **Model Management**

#### `GET /models` - List Available Models
**Response:**
```json
{
  "available_models": [
    "Resnet50.pth",
    "Unet.pth",
    "Vanilla.pth",
    "Vanillav2.pth",
    "effb3.pth"
  ],
  "selected_model": "Vanilla.pth"
}
```

#### `POST /models/select` - Switch Active Model
**Request:**
```json
{"model_name": "Resnet50.pth"}
```

### **System Status**

#### `GET /health` - System Health Check
```json
{
  "status": "healthy",
  "app_name": "OCT Analysis Backend",
  "version": "2.0.0",
  "database": "connected",
  "model_available": true,
  "selected_model": "Vanilla.pth"
}
```

#### `GET /system/gpu-status` - GPU Diagnostics
```json
{
  "device": "cuda",
  "model_loaded": true,
  "selected_model": "Vanilla.pth"
}
```

| Method | Endpoint | Purpose | Response |
|--------|----------|---------|----------|
| POST | `/analyze` | Single image analysis | AnalysisResponse (id, lesion_type, confidence, mask_viz, architecture, response_time) |
| POST | `/analyze-all` | All-model comparison | AnalyzeAllResponse (results from all models) |
| GET | `/models` | List available models | ModelListResponse |
| POST | `/models/select` | Switch active model | ModelListResponse |
| GET | `/patients` | List all patients | List[PatientResponse] |
| POST | `/patients` | Create patient | PatientResponse |
| GET | `/patients/{id}` | Get patient details | PatientResponse |
| PUT | `/patients/{id}` | Update patient | PatientResponse |
| GET | `/health` | System health | HealthResponse |
| GET | `/system/gpu-status` | GPU diagnostics | GPUStatusResponse |

---

## Key Components

### **1. Image Preprocessing** (`app/services/preprocess.py`)
- **Tool:** MONAI (Medical Open Network for AI)
- Load OCT image (grayscale via `cv2.IMREAD_GRAYSCALE`)
- Ensure channel-first format: (H, W) to (1, H, W)
- Scale intensity to [0, 1]
- Resize to 224x224 pixels (configurable via `config.py`)
- Normalize using mean/std statistics
- Convert to PyTorch tensor with batch dimension (1, 1, H, W)
- Return: (normalized_tensor, background_image_uint8)

### **2. Inference Engine** (`app/services/inference.py`)
- Load PyTorch models (.pth) from `weights/` directory
- Execute on GPU via CUDA (automatic fallback to CPU)
- Aspect-ratio-preserving resize to 512x512 with zero-padding
- Support 4 model architectures via `ARCH_REGISTRY`:
  - **Vanilla UNet** (`VanillaMultitaskUNet`)
  - **ResNet50 UNet** (`ResNet50MultiTaskUNet`)
  - **EfficientNet-B3 UNet** (`ImprovedOctMultiTaskUNet`)
  - **UNet++** (`UNetPlusPlusMultiTask`)
- Morphological postprocessing: close holes + connected-component area filter
- Un-padding and resize segmentation mask back to original image dimensions
- **Mock mode:** Returns error response when models unavailable
- Output: Classification label + Confidence + Segmentation mask overlay (Base64)

### **3. Postprocessing** (`app/services/postprocess.py`)
- Convert binary segmentation mask to PNG visualization
- Red overlay with edge contour on original image (via `visualize_result` in inference)
- Encode mask as Base64 PNG/JPEG for API response
- Save mask to disk with naming convention `mask+{image_filename}.png`
- Resize output to standard display size (224x224)

### **4. Database Models** (`app/models.py`)

**Patient Model:**
```python
class Patient(Base):
    id: int (auto-increment PK)
    name: str
    dob: date (nullable)
    gender: str (Male/Female/Other)
    contact: str
    medical_notes: str
    created_at: datetime
    updated_at: datetime
    scans: List[OCTScan]  # Relationship (cascade delete)
    # Computed: age, total_scans, last_visit
```

**OCTScan Model:**
```python
class OCTScan(Base):
    id: int (auto-increment PK)
    patient_id: int (FK, cascade delete)
    filename: str
    segmentation_mask_filename: str
    lesion_type: str (Normal/AMD/DME)
    confidence: float
    reliability_score: float
    mask_viz_base64: str (heatmap for PDF export)
    stability_metrics: JSON
    doctor_label: str
    validation_status: str (pending/approved/edited)
    validation_notes: str
    created_at: datetime
```

### **5. AI Models**

**Architecture:** U-Net variants with:
- **Encoder:** ResNet50 / EfficientNet-B3 / Custom backbones
- **Decoder:** Multi-scale U-Net decoder with attention gates
- **Heads:** Separate segmentation (1 output) + classification (3 outputs)
- **Attention:** Attention gates + SCSE (Spatial & Channel SE) blocks
- **Supervision:** Deep supervision at multiple scales
- **Training:** Multi-task learning (segmentation + classification)

**Available Models (in `weights/`):**
- `Vanilla.pth` - VanillaMultitaskUNet (default)
- `Resnet50.pth` - ResNet50 Multi-Task UNet
- `Unet.pth` - UNet++ Multi-Task
- `effb3.pth` - EfficientNet-B3 UNet
- `Vanillav2.pth` - Vanilla UNet v2 variant
- All models support GPU inference + can be fine-tuned

### **6. Frontend Components**

**Key Pages:**
- `app/page.tsx` - Dashboard/homepage
- `components/scanner/` - OCT image upload interface
- `components/patients/` - Patient management UI
- `components/ui/` - Reusable Shadcn/UI components

**Features:**
- Patient CRUD operations
- Image upload with progress tracking
- Real-time analysis results display
- Segmentation mask visualization with heatmap
- PDF report generation with analysis details
- Responsive design for tablets/laptops
- Dark mode support

---

## Data Flow

### **Typical Analysis Workflow:**

```
1. USER ACTION (Frontend)
   └─> Selects OCT image & uploads via Scanner component

2. FILE UPLOAD (API)
   └─> POST /api/analyze (multipart/form-data)
   
3. VALIDATION (Backend)
   └─> Check file type (PNG/JPEG)
   └─> Check file size (<50MB)
   
4. STORAGE
   └─> Save original image to /storage/ with UUID filename
   
5. PREPROCESSING (MONAI Pipeline)
   └─> Load image (grayscale)
   └─> Resize to 224x224 (via config)
   └─> Scale intensity + Normalize (mean/std)
   └─> Convert to PyTorch tensor (1, 1, H, W)
   
6. INFERENCE (PyTorch on GPU/CPU)
   └─> Load .pth model from weights/ directory
   └─> Aspect-ratio resize to 512x512 + zero-padding
   └─> Forward pass: tensor → classification + segmentation
   └─> Un-pad and resize mask back to original dimensions
   └─> Morphological filtering (close holes, remove small components)
   
7. POSTPROCESSING
   └─> Generate red overlay + edge contour on original image
   └─> Encode as Base64 JPEG
   └─> Prepare response data
   
8. DATABASE PERSISTENCE
   └─> Create OCTScan record with:
       - patient_id, lesion_type, confidence, mask_viz_base64
       - filename, timestamp
   
9. API RESPONSE
   └─> Return AnalysisResponse:
       {id, lesion_type, confidence, mask_viz, architecture, response_time}
   
10. FRONTEND DISPLAY
    └─> Show results in UI
    └─> Display segmentation overlay with heatmap
    └─> Allow PDF export or patient history viewing
```

### **Database Schema Relationships:**
```
Patient (1) ─────→ (Many) OCTScan
  ├─ id (PK)              ├─ id (PK)
  ├─ name                 ├─ patient_id (FK) → Patient.id
  ├─ dob                  ├─ lesion_type
  ├─ gender               ├─ confidence
  ├─ contact              ├─ reliability_score
  ├─ medical_notes        ├─ mask_viz_base64
  ├─ created_at           ├─ validation_status
  └─ updated_at           └─ created_at
```



## Configuration

### **Environment Variables** (`.env` or `backend_2.0/app/core/config.py`)
```bash
# Backend
FASTAPI_ENV=production
DATABASE_URL=sqlite:///./oct_app.db
STORAGE_PATH=./storage
MODEL_PATH=./weights
LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=RetinaAI
```

### **CORS Configuration** (auto-configured in `main.py`)
- Allows requests from frontend (Port 3000)
- Allows credentials
- Methods: GET, POST, PUT, DELETE

### **Model Selection**
Models are selected via API or configuration:
1. Default: `Vanilla.pth` (VanillaMultitaskUNet)
2. Switch at runtime: `POST /api/models/select`
3. Custom model: Add .pth file to `weights/` directory and register in `ARCH_REGISTRY`

---

## Troubleshooting

### **GPU Not Available**
```bash
# Check GPU/CUDA setup
curl http://localhost:8000/api/system/gpu-status

# Output shows:
# - "device": "cuda" or "cpu"
# - "model_loaded": true/false
# - "selected_model": currently loaded model

# Fallback: CPU inference (slower but works automatically)
```

### **Model Not Loading**
```bash
# Verify model file exists
ls -la backend_2.0/weights/

# Check for corrupted .pth file
# Solution: Re-download or re-train the model
```

### **Database Connection Error**
```bash
# Reset database
rm backend_2.0/oct_app.db

# (Optional) Seed with demo data
python seed_data.py

# Restart backend (auto-creates schema)
uvicorn app.main:app --reload
```

### **Image Upload Failed**
- Check file format (PNG, JPEG supported)
- Check file size (<50MB)
- Ensure `/storage` directory exists and writable
- Check API logs for detailed error messages

### **Frontend Cannot Connect to Backend**
- Verify backend running on `http://localhost:8000`
- Check CORS configuration in `main.py`
- Check firewall settings

---

## Deployment

### **Production Checklist**
1. Verify PyTorch model weights loaded correctly in `/weights/`
2. Configure production database (PostgreSQL recommended)
3. Set environment variables (.env file)
4. Configure SSL/TLS certificates
5. Setup reverse proxy (Nginx/Apache)
6. Enable logging & monitoring
7. Backup model weights (.pth files) & database
8. Test inference on GPU (if available)
9. See [DEPLOYMENT_CHECKLIST.md](docs/configuration/DEPLOYMENT_CHECKLIST.md)

### **Docker (Optional)**
```bash
# Build & run with Docker
docker-compose up --build
```

---

## Documentation

| File | Purpose |
|------|---------|
| [PROJECT_SUMMARY.md](docs/summary/PROJECT_SUMMARY.md) | High-level project overview |
| [PROJECT_ANALYSIS.md](docs/summary/PROJECT_ANALYSIS.md) | Deep architecture analysis |
| [API_SPECIFICATION.md](docs/documentation/API_SPECIFICATION.md) | Complete API reference |
| [BACKEND_DOCUMENTATION.md](docs/documentation/BACKEND_DOCUMENTATION.md) | Backend implementation details |
| [QUICK_START_GPU.md](docs/guides/QUICK_START_GPU.md) | GPU setup guide |
| [DEPLOYMENT_CHECKLIST.md](docs/configuration/DEPLOYMENT_CHECKLIST.md) | Production deployment steps |


## **Final Implementation Details**

### Inference Architecture: PyTorch (.pth Models) 

**Why PyTorch over ONNX:**
- Direct .pth loading without conversion overhead
- Full model flexibility for training/fine-tuning
- Better debugging & logging capabilities
- Native GPU support via PyTorch CUDA integration
- Consistent with training pipeline

**Model Pipeline:**
1. Load PyTorch model from `weights/{model_name}.pth` via `ARCH_REGISTRY`
2. Preprocess with MONAI transforms (scale intensity, resize 224x224, normalize)
3. Inference engine: aspect-ratio resize to 512x512 + zero-padding
4. Forward pass on GPU/CPU: classification + segmentation outputs
5. Un-pad mask, resize to original dimensions, morphological cleanup
6. Generate red overlay visualization + Base64 encode
7. Return JSON response with predictions + encoded mask

**Removed Components (Legacy/Unused):**
- ONNX Runtime (not needed)
- ONNX models folder (replaced by weights/)
- Note: `onnxruntime-gpu` still in requirements.txt but unused (can be safely removed)

**Active Inference Flow:**
```
Input Image --> MONAI Preprocess --> PyTorch Model (.pth) --> GPU/CPU
                                           |
                              Aspect-Ratio Resize + Padding
                                           |
                          Classification + Segmentation
                                           |
                        Un-pad + Morphological Cleanup
                                           |
                          Red Overlay Visualization
                                           |
                          API Response (JSON + Base64)
```

---

## Production Readiness Summary

| Aspect | Status | Details |
|--------|--------|---------|
| **Core Code** |  Complete | All critical files present |
| **Models** |  Complete | .pth weights in weights/ directory |
| **Frontend** |  Complete | Full Next.js application |
| **Backend** |  Complete | FastAPI with all endpoints |
| **Database** |  Complete | SQLAlchemy ORM configured |
| **API** |  Complete | All routes implemented |
| **Documentation** |  Complete | Comprehensive docs included |
| **GPU Support** |  Complete | PyTorch CUDA support enabled |
| **Error Handling** |  Complete | Mock fallback mode included |
| **Inference Engine** |  Complete | PyTorch (.pth) - NOT ONNX |

**Overall Status:** PRODUCTION READY

---

**Status:** Production Ready  
**Inference Backend:** PyTorch (GPU-accelerated on NVIDIA CUDA)  
**Models:** .pth weights in `backend_2.0/weights/` directory  
**Architectures:** Vanilla UNet, ResNet50 UNet, UNet++, EfficientNet-B3 UNet  
**Last Updated:** April 24, 2026  
**Stability:** Stable with extensive testing completed
