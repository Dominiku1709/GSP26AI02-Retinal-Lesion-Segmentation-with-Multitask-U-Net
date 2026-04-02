import os
import uuid
import time
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models
from . import schemas
from ..services import preprocess, postprocess
# BUG FIX #1: Import model_runner directly, not the module.
# Previously: inference.predict() was called, but 'inference' is a MODULE.
# The actual callable is 'model_runner' (the InferenceService instance at the bottom of inference.py).
from ..services.inference import model_runner

router = APIRouter()

UPLOAD_DIR = "storage"


# BUG FIX #2: response_model was schemas.HistoryRecord but the function
# returned schemas.AnalysisResponse. These have completely different shapes.
# FastAPI would silently try to coerce AnalysisResponse -> HistoryRecord,
# which would fail at runtime (missing 'id', 'created_at', 'image_url').
@router.post("/analyze", response_model=schemas.AnalysisResponse)
async def analyze_oct_image(
    file: UploadFile = File(...),
    patient_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Receives an OCT image, runs preprocessing → inference → postprocessing,
    saves the record to the database, and returns the analysis result.
    
    Optional: patient_id to link scan to a specific patient.
    """
    # 1. VALIDATION
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    # Validate patient_id if provided
    if patient_id:
        patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")

    # 2. PERSISTENCE: Save raw file with a unique name
    file_extension = os.path.splitext(file.filename or "upload.png")[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    try:
        # 3. PREPROCESS
        processed_image = preprocess.prepare_image(file_path)

        # 4. INFERENCE — using model_runner.predict(), not inference.predict()
        start_time = time.time()
        prediction = model_runner.predict(processed_image)
        inference_time_ms = round((time.time() - start_time) * 1000, 1)

        # 5. POSTPROCESS: mask → Base64 PNG data URI
        mask_string = postprocess.mask_to_base64(prediction["mask"])

        # 6. PERSIST to database (with optional patient_id)
        new_record = models.OCTScan(
            filename=unique_filename,
            lesion_type=prediction["label"],
            confidence=prediction["confidence"],
            patient_id=patient_id,  # NEW: Link to patient if provided
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        # 7. RESPONSE
        return schemas.AnalysisResponse(
            id=new_record.id,
            lesion_type=new_record.lesion_type,
            confidence=new_record.confidence,
            segmentation_mask_base64=mask_string,
            filename=unique_filename,
            image_url=f"http://localhost:8000/images/{unique_filename}",
            inference_time_ms=inference_time_ms,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Processing failed: {str(e)}")


@router.get("/history", response_model=List[schemas.HistoryRecord])
def get_history(limit: int = 20, skip: int = 0, db: Session = Depends(get_db)):
    """Returns the most recent scan records from the database."""
    scans = (
        db.query(models.OCTScan)
        .order_by(models.OCTScan.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    # Attach computed image_url before returning (it's not stored in DB)
    for scan in scans:
        scan.image_url = f"http://localhost:8000/images/{scan.filename}"

    return scans


# ─────────────────────────────────────────────────────────────────────────────
# PATIENT MANAGEMENT ENDPOINTS (NEW)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/patients", response_model=schemas.PatientResponse)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient record."""
    new_patient = models.Patient(
        name=patient.name,
        dob=patient.dob,
        gender=patient.gender or "Other",
        contact=patient.contact,
        medical_notes=patient.medical_notes,
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient


@router.get("/patients", response_model=schemas.PatientListResponse)
def list_patients(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List all patients with pagination."""
    total = db.query(models.Patient).count()
    patients = (
        db.query(models.Patient)
        .order_by(models.Patient.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return schemas.PatientListResponse(
        total=total,
        skip=skip,
        limit=limit,
        patients=patients,
    )


@router.get("/patients/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Retrieve a single patient by ID."""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    return patient


@router.put("/patients/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(
    patient_id: int, update: schemas.PatientUpdate, db: Session = Depends(get_db)
):
    """Update an existing patient record."""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")

    # Update only provided fields
    if update.name is not None:
        patient.name = update.name
    if update.dob is not None:
        patient.dob = update.dob
    if update.gender is not None:
        patient.gender = update.gender
    if update.contact is not None:
        patient.contact = update.contact
    if update.medical_notes is not None:
        patient.medical_notes = update.medical_notes

    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete a patient and all associated scans."""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")

    db.delete(patient)
    db.commit()
    return {"message": f"Patient {patient_id} deleted successfully"}


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Returns the operational status of the API and its dependencies."""
    db_status = "connected"
    try:
        db.execute(models.OCTScan.__table__.select().limit(1))
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "app_name": "OCT Analysis Backend",
        "version": "2.0.0",
        "database": db_status,
        "model_available": not model_runner.is_mock,
    }
