from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


# ─── OCT SCAN SCHEMAS ──────────────────────────────────────────────────────

# BUG FIX #3: The original AnalysisResponse was missing 'id' and 'image_url',
# which are needed by the frontend to display the uploaded image and reference
# the record. These are now included so the frontend gets everything in one call.
class AnalysisResponse(BaseModel):
    """Returned by POST /analyze. Everything the frontend needs after a scan."""
    id: int
    lesion_type: str           # e.g. "Drusen", "CNV", "Normal"
    confidence: float          # 0.0 → 1.0 (backend keeps raw; frontend scales to %)
    segmentation_mask_base64: Optional[str] = None  # data:image/png;base64,...
    filename: str              # UUID filename in /storage/
    image_url: str             # Full URL: http://localhost:8000/images/{filename}
    inference_time_ms: float   # Client can display this as processing time


class HistoryRecord(BaseModel):
    """Returned by GET /history. One row per past scan."""
    id: int
    filename: str
    lesion_type: str
    confidence: float
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
