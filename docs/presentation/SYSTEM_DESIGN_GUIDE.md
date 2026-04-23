# System Design and Implementation - Slide Content Guide

## Document Overview

Two complete slide presentation documents have been created:

1. **SYSTEM_DESIGN_ENGLISH.md** - Complete English version
2. **SYSTEM_DESIGN_VIETNAMESE.md** - Complete Vietnamese version

Both files are located in: `docs/presentation/`

---

## Content Structure

Both documents follow the required template with 4 main sections:

### **Section 1: AI Model Integration**
- **Multi-Model Architecture**: Description of 5 available models (DeepLabV3+, ResNet U-Net, U-Net++, EfficientNet-B3, Vanilla)
- **System Integration Interface**: How the AI models connect with frontend/backend
- **Data Exchange Mechanism**: Request/response schemas and data flow

**Key Points for Slides:**
- Show the model registry pattern
- Explain dynamic model loading capability
- Display integration diagram

### **Section 2: Data Flow and Processing**
- **Complete Data Flow Architecture**: 5-stage pipeline (input → preprocessing → inference → postprocessing → output)
- **Detailed Processing Steps**: 4 key transformation stages with technical details
- **Data Flow Diagram**: Visual representation of the complete pipeline
- **Database Schema**: OCTScan table structure with all fields

**Key Points for Slides:**
- Use the visual pipeline diagram
- Highlight preprocessing techniques (normalization, resizing, standardization)
- Show the 3 lesion classification types (Normal, AMD, DME)
- Display database schema table

### **Section 3: Deployment Strategy**
- **Deployment Architecture**: Multi-tier system with load balancing
- **Deployment Environments**: Development, Staging, Production configurations
- **Deployment Procedures**: 4-step Docker-based deployment with code examples
- **Environment Configuration**: Production environment variables

**Key Points for Slides:**
- Show the deployment architecture diagram with frontend/backend/database tiers
- Explain Docker containerization approach
- Display docker-compose configuration
- List environment variables for production

### **Section 4: Scalability and Maintenance**
- **System Scalability Design**: Horizontal and vertical scaling strategies
- **Version Management**: Model versioning, database migration, API versioning
- **Maintenance Procedures**: Regular tasks and update deployment strategies
- **Monitoring and Observability**: Key metrics for infrastructure, application, and model
- **Disaster Recovery**: Backup strategy and failover mechanisms

**Key Points for Slides:**
- Explain horizontal vs. vertical scaling
- Show version management structure
- Display maintenance task table
- List key metrics (SLAs: 99.9% availability, < 500ms latency)
- Explain RTO/RPO for disaster recovery

---

## 📊 Key Technical Details

### Model Information
- **Primary Model**: DeepLabV3+ with ResNet-50 encoder
- **Input Size**: 512×512 pixels (grayscale)
- **Output**: 3-class classification + binary segmentation mask
- **Inference Time**: ~245ms on GPU
- **Supported Models**: 5 architectures with dynamic selection

### System Architecture
```
Frontend (Next.js, Port 3000)
    ↓ HTTP/REST
Backend (FastAPI, Port 8000)
    ↓
AI Models (PyTorch GPU/CPU)
    ↓
SQLite/PostgreSQL Database
    ↓ Storage
Image Storage + Segmentation Masks
```

### API Endpoints
- **POST /api/v1/analyze** - Main image analysis endpoint
- **GET /api/v1/health** - Health check
- **GET /api/v1/patients** - Patient management
- **GET /api/v1/models** - Model selection

### Deployment Stack
- **Container**: Docker + Docker Compose
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Next.js + React 19
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ML Framework**: PyTorch with GPU support (CUDA)

---

## 🎨 Recommendations for Slide Creation

### Suggested Slide Organization

**Slide 1-2: AI Model Integration**
- Show 5 available models with their strengths
- Display model registry concept diagram
- Show integration flow diagram

**Slide 3-4: Data Flow**
- Use the 5-stage pipeline diagram
- Show before/after preprocessing examples
- Display database schema

**Slide 5-6: Deployment**
- Show multi-tier architecture diagram
- Display docker-compose configuration (simplified)
- Mention 3 environments (Dev/Staging/Prod)

**Slide 7-8: Scalability**
- Explain horizontal scaling (add instances)
- Show version management structure
- Display key metrics and SLAs

**Slide 9: Summary**
- Highlight enterprise-grade design
- Show technical achievements
- Future-proof architecture

---

## Key Metrics to Highlight

| Metric | Target | Purpose |
|--------|--------|---------|
| API Availability | > 99.9% | Reliability |
| Request Latency | < 500ms (p95) | User Experience |
| Model Inference | < 300ms | Clinical Workflow |
| DB Query | < 50ms | Performance |
| GPU Utilization | > 80% | Efficiency |
| Error Rate | < 0.1% | Quality |

---

## Technical Highlights

1. **Multi-Model Support**: Easy switching between 5 different architectures
2. **GPU Acceleration**: CUDA-enabled PyTorch for real-time inference
3. **Scalable Architecture**: Stateless backend for horizontal scaling
4. **Database Persistence**: SQLAlchemy ORM supporting SQLite→PostgreSQL migration
5. **Containerization**: Docker/Docker Compose for consistent deployment
6. **Version Management**: Complete versioning for models, API, and database
7. **Monitoring Ready**: Structured logging and key metrics defined
8. **Disaster Recovery**: RTO < 1 hour, RPO < 15 minutes

---

## File Locations

```
docs/
├── presentation/
│   ├── SYSTEM_DESIGN_ENGLISH.md        (This content)
│   ├── SYSTEM_DESIGN_VIETNAMESE.md     (Vietnamese version)
│   └── SYSTEM_DESIGN_GUIDE.md          (This guide)
├── documentation/
│   ├── API_SPECIFICATION.md
│   ├── BACKEND_DOCUMENTATION.md
│   └── UX_DOCUMENTATION.md
├── configuration/
│   └── DEPLOYMENT_CHECKLIST.md
└── summary/
    └── PROJECT_SUMMARY.md
```

---

## Tips for Presentation

1. **Use Diagrams**: Replace text-heavy content with visual diagrams
2. **Keep It Simple**: For each slide, focus on 3-4 key points
3. **Use Screenshots**: Show actual UI/API examples
4. **Compare Models**: Create a comparison table of the 5 models
5. **Show Real Examples**: Include actual API request/response samples
6. **Highlight Achievements**: Emphasize multi-language, multi-model, multi-environment support
7. **Future Vision**: Explain how the system can evolve (K8s, microservices, etc.)

---

## Questions to Address in Presentation

**For Slide Deck:**
- How does the system handle peak loads? → Horizontal scaling explanation
- What if the model needs to be updated? → Version management strategy
- How is patient data protected? → Database backup and encryption
- What's the recovery time if something fails? → RTO/RPO metrics
- Can the system handle new disease types? → Multi-model flexibility

---

**Last Updated**: April 22, 2026
**Project**: RetinaAI - OCT Retinal Lesion Segmentation & Classification
**Version**: 1.0
