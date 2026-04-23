# backend_2.0/app/api/endpoints.py
import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models
from . import schemas
from ..services import preprocess
# BUG FIX #1: Import model_runner directly, not the module.
# Previously: inference.predict() was called, but 'inference' is a MODULE.
# The actual callable is 'model_runner' (the InferenceService instance at the bottom of inference.py).
from ..services.inference import model_runner

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "storage"


@router.get("/system/gpu-status")
def get_gpu_status():
    """
    Returns GPU/CUDA availability and inference provider status.
    Useful for debugging GPU initialization issues.
    """
    return model_runner.get_gpu_status()


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
    import time
    start_time = time.time()  # Start timing
    
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

        # 4. INFERENCE
        prediction = model_runner.predict(processed_image)

        # 5. PERSIST to database
        new_record = models.OCTScan(
            filename=unique_filename,
            lesion_type=prediction["label"],
            confidence=prediction["confidence"],
            #reliability_score=prediction.get("reliability_score", 0.0),
            #stability_metrics=prediction.get("stability_metrics", None),
            mask_viz_base64=prediction.get("mask_viz"),  # NEW: Save heatmap for PDF export
            patient_id=patient_id,
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        # Calculate response time in milliseconds (rounded)
        response_time_ms = round((time.time() - start_time) * 1000, 2)

        # 6. RESPONSE
        return schemas.AnalysisResponse(
            id=new_record.id,
            lesion_type=new_record.lesion_type,
            confidence=new_record.confidence,
            mask_viz=prediction["mask_viz"],
            mask_viz_base64=prediction.get("mask_viz"),  # NEW: Include in response
            #reliability_score=prediction.get("reliability_score", 0.0),
            #stability_metrics=prediction.get("stability_metrics", None),
            filename=unique_filename,
            image_url=f"http://localhost:8000/images/{unique_filename}",
            architecture=prediction.get("architecture", "unknown"),
            response_time=response_time_ms,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Processing failed: {str(e)}")


@router.post("/analyze-all", response_model=schemas.AnalyzeAllResponse)
async def analyze_all_models(
    file: UploadFile = File(...),
    patient_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Receives an OCT image and runs inference on ALL available models in parallel.
    Returns results from all models for comparison.
    
    Optional: patient_id to link scan to a specific patient.
    """
    import concurrent.futures
    
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
        # 3. PREPROCESS (once for all models)
        processed_image = preprocess.prepare_image(file_path)

        # 4. INFERENCE ON ALL MODELS (parallel, no DB save)
        all_results = []
        available_models = model_runner.list_models()

        def run_single_model_inference(model_name: str):
            try:
                current_model = model_runner.selected_model
                model_runner.set_model(model_name)
                prediction = model_runner.predict(processed_image)
                model_runner.set_model(current_model)
                return model_name, prediction, None
            except Exception as e:
                return model_name, None, str(e)

        # Run all models in parallel
        import time
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(available_models)) as executor:
            futures = {
                executor.submit(run_single_model_inference, model_name): model_name
                for model_name in available_models
            }
            for future in concurrent.futures.as_completed(futures):
                model_name, prediction, error = future.result()
                if error:
                    logger.error(f"Error running {model_name}: {error}")
                    continue
                # Build response for this model (no DB id)
                result = schemas.AnalysisResponse(
                    id=None,
                    lesion_type=prediction["label"],
                    confidence=prediction["confidence"],
                    mask_viz=prediction["mask_viz"],
                    mask_viz_base64=prediction.get("mask_viz"),
                    reliability_score=prediction.get("reliability_score", 0.0),
                    stability_metrics=prediction.get("stability_metrics", None),
                    filename=unique_filename,
                    image_url=f"http://localhost:8000/images/{unique_filename}",
                    architecture=prediction.get("architecture", model_name),
                    response_time=prediction.get("response_time", 0.0),
                )
                all_results.append(result)

        return schemas.AnalyzeAllResponse(results=all_results)

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
    # Attach computed image_url before returning (not stored in DB)
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
        "selected_model": model_runner.selected_model,
    }


@router.get("/models", response_model=schemas.ModelListResponse)
def get_model_list():
    """Return the models available in backend_2.0/weights."""
    return schemas.ModelListResponse(
        available_models=model_runner.list_models(),
        selected_model=model_runner.selected_model,
    )


@router.post("/models/select", response_model=schemas.ModelListResponse)
def select_model(selection: schemas.ModelSelectionRequest):
    """Switch the backend to use the selected ONNX model."""
    try:
        model_runner.set_model(selection.model_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return schemas.ModelListResponse(
        available_models=model_runner.list_models(),
        selected_model=model_runner.selected_model,
    )
