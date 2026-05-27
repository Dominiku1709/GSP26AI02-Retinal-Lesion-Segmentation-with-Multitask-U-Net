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
    id: Optional[int] = None # Cho phép None nếu chạy analyze-all (không lưu DB)
    lesion_type: str        
    confidence: float       
    mask_viz: str           
    mask_viz_base64: Optional[str] = None 
    architecture: str       
    filename: str           
    image_url: str          
    response_time: float
    # Thêm các trường optional nếu analyze-all cần
    reliability_score: Optional[float] = 0.0
    stability_metrics: Optional[StabilityMetrics] = None


class AnalyzeAllResponse(BaseModel):
    """Returned by POST /analyze-all. Results from all models."""
    results: List[AnalysisResponse]          # One result per model


class ModelInfo(BaseModel):
    """Cấu trúc cho từng model trong danh sách"""
    file_name: str
    display_name: str

class ModelListResponse(BaseModel):
    """Phản hồi danh sách model kèm model đang được chọn"""
    available_models: List[str]  # Sửa từ List[str] thành List[ModelInfo]
    selected_model: Optional[str] = None
    # Bỏ display_names cũ vì thông tin đã nằm trong ModelInfo

class ModelSelectionRequest(BaseModel):
    """Yêu cầu chọn model từ phía Frontend"""
    model_name: str  # Đây thường là file_name để backend dễ tìm file .pth

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
    name: str
    dob: Optional[date] = None
    gender: Optional[str] = "Other"
    contact: Optional[str] = None
    medical_notes: Optional[str] = None


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    medical_notes: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    name: str
    dob: Optional[date] = None
    gender: str
    contact: Optional[str] = None
    medical_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    age: int
    total_scans: int
    last_visit: Optional[str] = None # Đổi thành Optional vì có thể chưa có scan nào

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    patients: List[PatientResponse]