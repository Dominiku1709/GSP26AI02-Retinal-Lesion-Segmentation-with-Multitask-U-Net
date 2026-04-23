# backend_2.0/app/api/schemas.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


# ─── OCT SCAN SCHEMAS ──────────────────────────────────────────────────────

class StabilityMetrics(BaseModel):
    tta_iou: float
    objects_found: int
    is_stable: bool


class AnalysisResponse(BaseModel):
    """Bản rút gọn: Chỉ giữ lại những gì thực sự cần thiết"""
    id: int
    lesion_type: str        
    confidence: float       
    mask_viz: str           
    mask_viz_base64: Optional[str] = None 
    architecture: str       
    filename: str           
    image_url: str          
    response_time: float


class AnalyzeAllResponse(BaseModel):
    """Returned by POST /analyze-all. Results from all models."""
    results: List[AnalysisResponse]          # One result per model


class ModelListResponse(BaseModel):
    available_models: List[str]
    selected_model: Optional[str] = None


class ModelSelectionRequest(BaseModel):
    model_name: str

    model_config = {"protected_namespaces": ()}


class HistoryRecord(BaseModel):
    """Returned by GET /history. One row per past scan."""
    id: int
    filename: str
    lesion_type: str
    confidence: float
    reliability_score: Optional[float] = 0.0
    stability_metrics: Optional[StabilityMetrics] = None
    mask_viz_base64: Optional[str] = None  # NEW: Heatmap for PDF export
    created_at: datetime
    image_url: str             # Computed field — not stored in DB, added in endpoint

    class Config:
        from_attributes = True  # Allows building from SQLAlchemy ORM objects


# ─── PATIENT SCHEMAS ──────────────────────────────────────────────────────

class PatientCreate(BaseModel):
    """Request body for POST /patients"""
    name: str
    dob: Optional[date] = None
    gender: Optional[str] = "Other"  # "Male", "Female", "Other"
    contact: Optional[str] = None
    medical_notes: Optional[str] = None


class PatientUpdate(BaseModel):
    """Request body for PUT /patients/{id}"""
    name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    medical_notes: Optional[str] = None


class PatientResponse(BaseModel):
    """Returned by GET /patients, GET /patients/{id}, POST /patients, PUT /patients/{id}"""
    id: int
    name: str
    dob: Optional[date] = None
    gender: str
    contact: Optional[str] = None
    medical_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    age: int  # Computed property from model
    total_scans: int  # Computed property from model
    last_visit: str  # ISO datetime string (computed property)

    class Config:
        from_attributes = True  # Build from SQLAlchemy ORM objects


class PatientListResponse(BaseModel):
    """Wrapper for GET /patients with pagination"""
    total: int
    skip: int
    limit: int
    patients: List[PatientResponse]
