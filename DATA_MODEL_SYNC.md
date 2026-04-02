# 🔄 Frontend-Backend Data Model Synchronization Guide

**Purpose:** Map & align data structures between frontend (React Context) and backend (SQLAlchemy)

---

## 1. Current Data Models

### Frontend (React Context) - `UX/lib/store.tsx`

```typescript
interface Patient {
  id: string                    // Generated as "P-{timestamp}"
  name: string
  age: number
  dob: string                   // ISO date string
  gender: string                // "Male" | "Female" | "Other"
  totalScans: number
  lastVisit: string             // ISO date string
  scans: ScanResult[]           // Stored IN MEMORY
  contact?: string              // OPTIONAL (not currently saved)
  medicalNotes?: string         // OPTIONAL (not currently saved)
}

interface ScanResult {
  id: string                    // "scan-{timestamp}" or "scan-{analysisId}"
  originalImage: string         // URL to uploaded image
  maskOverlay: string           // Base64 PNG data URI
  confidence: number            // 0-100 (percentage)
  processingTime: number        // seconds
  lesionTypes: LesionType[]
  date: string                  // ISO date string
  doctorLabel: string
  validationStatus?: "pending" | "approved" | "edited"
}

interface LesionType {
  name: string                  // "AMD" | "DME" | "Normal"
  color: string                 // Hex color
  percentage: number            // 0-100
}
```

### Backend (SQLAlchemy) - `backend_2.0/app/models.py`

```python
class OCTScan(Base):
    __tablename__ = "oct_scans"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    lesion_type = Column(String, index=True)  # Single lesion type only!
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    # NOTE: No patient_id foreign key yet — must be added!

# MISSING: Patient model
# MISSING: Association between scans and patients
```

---

## 2. Gaps & Misalignments

| Aspect | Frontend | Backend | Issue |
|--------|----------|---------|-------|
| **Patient Storage** | React Context (in-memory) | Not modeled | ❌ Data lost on refresh |
| **Patient-Scan Link** | `patient.scans: ScanResult[]` | No FK relationship | ❌ Not persisted |
| **Lesion Types Multiple** | `lesionTypes: LesionType[]` array | Single `lesion_type` string | ⚠️ Schema mismatch |
| **Doctor Label** | `doctorLabel: string` | Not stored | ❌ Validation lost |
| **Validation Status** | `validationStatus: enum` | Not tracked | ❌ Not persisted |
| **Contact/Notes** | Optional fields | Not in model | ❌ Not saved |
| **Age Calculation** | Computed from DOB | Not computed | ⚠️ Inconsistent |

---

## 3. Recommended Data Model Update

### Backend Changes Required

#### New Patient Model

```python
# backend_2.0/app/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Patient(Base):
    __tablename__ = "patients"
    
    # Identifiers
    id = Column(Integer, primary_key=True)
    
    # Personal Info
    name = Column(String, nullable=False, index=True)
    dob = Column(Date, nullable=True)  # Used to compute age
    gender = Column(String, default="Other")  # "Male", "Female", "Other"
    
    # Contact & Medical
    contact = Column(String, nullable=True)
    medical_notes = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scans = relationship("OCTScan", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}')>"
    
    @property
    def age(self) -> int:
        """Computed property: calculate age from DOB"""
        if not self.dob:
            return 0
        from datetime import date
        today = date.today()
        age = today.year - self.dob.year
        if (today.month, today.day) < (self.dob.month, self.dob.day):
            age -= 1
        return age
    
    @property
    def total_scans(self) -> int:
        """Count of associated scans"""
        return len(self.scans) if self.scans else 0
    
    @property
    def last_visit(self) -> str:
        """ISO date string of latest scan"""
        if not self.scans:
            return self.created_at.isoformat()
        latest = max(self.scans, key=lambda s: s.created_at)
        return latest.created_at.isoformat()


# Modify existing OCTScan model
class OCTScan(Base):
    __tablename__ = "oct_scans"
    
    id = Column(Integer, primary_key=True)
    
    # Foreign Key
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=True)
    
    # Analysis Results
    filename = Column(String, nullable=False)
    lesion_type = Column(String, index=True)  # Single primary lesion (from model output)
    confidence = Column(Float)
    segmentation_mask_base64 = Column(String, nullable=True)  # BASE64 PNG
    
    # Doctor Validation
    doctor_label = Column(String, nullable=True)  # Doctor's override/notes
    validation_status = Column(String, default="pending")  # "pending" | "approved" | "edited"
    validation_notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="scans")
    
    def __repr__(self):
        return f"<OCTScan(id={self.id}, type='{self.lesion_type}', confidence={self.confidence})>"
```

#### Database Migration Script

```python
# backend_2.0/migrations/001_add_patient_model.py
# Run this ONCE to update existing database structure

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

def upgrade():
    """Add Patient table and patient_id FK to OCTScan"""
    
    # Check if table already exists
    inspector = inspect(op.get_bind())
    existing_tables = inspector.get_table_names()
    
    # 1. Create patients table if not exists
    if 'patients' not in existing_tables:
        op.create_table(
            'patients',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('dob', sa.Date(), nullable=True),
            sa.Column('gender', sa.String(), server_default='Other'),
            sa.Column('contact', sa.String(), nullable=True),
            sa.Column('medical_notes', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_patients_name', 'patients', ['name'])
        op.create_index('ix_patients_created_at', 'patients', ['created_at'])
    
    # 2. Add columns to oct_scans table
    columns_to_add = [
        ('patient_id', sa.Integer(), False),
        ('doctor_label', sa.String(), True),
        ('validation_status', sa.String(), True),
        ('validation_notes', sa.String(), True),
        ('segmentation_mask_base64', sa.String(), True)
    ]
    
    for col_name, col_type, nullable in columns_to_add:
        if col_name not in [c.name for c in inspector.get_columns('oct_scans')]:
            server_default = 'NULL' if nullable else "'pending'" if col_name == 'validation_status' else None
            op.add_column('oct_scans', sa.Column(col_name, col_type, nullable=nullable, server_default=server_default))
    
    # 3. Add foreign key if not exists
    if 'fk_oct_scans_patient_id' not in [fk.name for fk in inspector.get_pk_constraint('oct_scans')]:
        op.create_foreign_key(
            'fk_oct_scans_patient_id',
            'oct_scans',
            'patients',
            ['patient_id'],
            ['id'],
            ondelete='CASCADE'
        )

def downgrade():
    """Rollback changes"""
    op.drop_constraint('fk_oct_scans_patient_id', 'oct_scans')
    op.drop_table('patients')
    # Remove added columns (optional, keep for safety)
```

---

## 4. API Schema Updates

### Response DTOs - `backend_2.0/app/api/schemas.py`

```python
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional

# ── Patient Schemas ──────────────────────────────────────────

class ScanResultDto(BaseModel):
    """Minimal scan info for patient detail view"""
    id: int
    lesion_type: str
    confidence: float
    created_at: datetime
    validation_status: str
    
    class Config:
        from_attributes = True

class PatientCreateRequest(BaseModel):
    """Request body for POST /patients"""
    name: str
    dob: Optional[date] = None
    gender: str = "Other"  # "Male", "Female", "Other"
    contact: Optional[str] = None
    medical_notes: Optional[str] = None

class PatientUpdateRequest(BaseModel):
    """Request body for PUT /patients/{id}"""
    name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    medical_notes: Optional[str] = None

class PatientDetailResponse(BaseModel):
    """Response from GET /patients/{id}"""
    id: int
    name: str
    age: int                    # Computed from DOB
    dob: Optional[date]
    gender: str
    contact: Optional[str]
    medical_notes: Optional[str]
    total_scans: int            # Computed from len(scans)
    last_visit: str             # ISO datetime string
    created_at: datetime
    scans: List[ScanResultDto]
    
    class Config:
        from_attributes = True

class PatientListResponse(BaseModel):
    """Response from GET /patients"""
    id: int
    name: str
    age: int
    gender: str
    total_scans: int
    last_visit: str
    
    class Config:
        from_attributes = True

# ── Analysis Schemas (UPDATED) ──────────────────────────────

class AnalysisResponse(BaseModel):
    """Response from POST /analyze"""
    id: int
    lesion_type: str
    confidence: float
    segmentation_mask_base64: Optional[str] = None
    filename: str
    image_url: str
    inference_time_ms: float
    doctor_label: Optional[str] = None
    validation_status: str = "pending"

class ScanValidationRequest(BaseModel):
    """Request body for PUT /scans/{id}/validate"""
    action: str  # "approve" | "reject" | "edit"
    doctor_label: Optional[str] = None
    validation_notes: Optional[str] = None

class ScanValidationResponse(BaseModel):
    """Response from scan validation"""
    id: int
    validation_status: str
    doctor_label: str
    validation_notes: Optional[str]
    updated_at: datetime
```

---

## 5. New API Endpoints

### Patient Management

```python
# backend_2.0/app/api/endpoints.py (ADD THESE)

@router.post("/patients", response_model=schemas.PatientDetailResponse)
async def create_patient(
    patient_data: schemas.PatientCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new patient"""
    new_patient = models.Patient(
        name=patient_data.name,
        dob=patient_data.dob,
        gender=patient_data.gender,
        contact=patient_data.contact,
        medical_notes=patient_data.medical_notes
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.get("/patients/{patient_id}", response_model=schemas.PatientDetailResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Get patient details with all scans"""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("/patients", response_model=List[schemas.PatientListResponse])
async def list_patients(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """List all patients (paginated)"""
    patients = db.query(models.Patient)\
        .order_by(models.Patient.updated_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return patients

@router.put("/patients/{patient_id}", response_model=schemas.PatientDetailResponse)
async def update_patient(
    patient_id: int,
    patient_data: schemas.PatientUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update patient details"""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    update_data = patient_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)
    
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/patients/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Delete patient and associated scans"""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted"}
```

### Scan Association

```python
@router.post("/analyze", response_model=schemas.AnalysisResponse)
async def analyze_oct_image(
    file: UploadFile = File(...),
    patient_id: Optional[int] = Query(None),  # NEW: Optional patient association
    db: Session = Depends(get_db)
):
    """NEW: Analyze OCT image, optionally associate to patient"""
    # ... existing preprocessing & inference code ...
    
    # When creating OCTScan record:
    new_record = models.OCTScan(
        patient_id=patient_id,  # Can be None for unassociated scans
        filename=unique_filename,
        lesion_type=prediction["label"],
        confidence=prediction["confidence"],
        segmentation_mask_base64=mask_string,
        validation_status="pending"
    )
    # ... rest of code ...

@router.put("/scans/{scan_id}/validate", response_model=schemas.ScanValidationResponse)
async def validate_scan(
    scan_id: int,
    validation_data: schemas.ScanValidationRequest,
    db: Session = Depends(get_db)
):
    """Doctor validates/edits scan results"""
    scan = db.query(models.OCTScan).filter(models.OCTScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan.validation_status = validation_data.action
    if validation_data.doctor_label:
        scan.doctor_label = validation_data.doctor_label
    if validation_data.validation_notes:
        scan.validation_notes = validation_data.validation_notes
    
    db.commit()
    db.refresh(scan)
    return scan

@router.get("/patients/{patient_id}/scans", response_model=List[schemas.ScanResultDto])
async def get_patient_scans(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Get all scans for a specific patient"""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return patient.scans
```

---

## 6. Frontend Integration Updates

### Update `UX/lib/api.ts`

```typescript
// Add Patient API functions

export async function createPatient(data: {
  name: string
  dob?: string
  gender?: string
  contact?: string
  medical_notes?: string
}): Promise<Patient> {
  const response = await fetch(`${API_BASE}/patients`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(`Failed to create patient: ${response.status}`)
  return response.json()
}

export async function getPatients(): Promise<Patient[]> {
  const response = await fetch(`${API_BASE}/patients`)
  if (!response.ok) throw new Error(`Failed to fetch patients: ${response.status}`)
  return response.json()
}

export async function getPatient(id: string): Promise<Patient> {
  const response = await fetch(`${API_BASE}/patients/${id}`)
  if (!response.ok) throw new Error(`Failed to fetch patient: ${response.status}`)
  return response.json()
}

export async function updatePatient(id: string, data: Partial<Patient>): Promise<Patient> {
  const response = await fetch(`${API_BASE}/patients/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(`Failed to update patient: ${response.status}`)
  return response.json()
}

export async function deletePatient(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/patients/${id}`, {
    method: "DELETE",
  })
  if (!response.ok) throw new Error(`Failed to delete patient: ${response.status}`)
}

export async function validateScan(scanId: string, validation: {
  action: "approve" | "reject" | "edit"
  doctor_label?: string
  validation_notes?: string
}): Promise<void> {
  const response = await fetch(`${API_BASE}/scans/${scanId}/validate`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(validation),
  })
  if (!response.ok) throw new Error(`Failed to validate scan: ${response.status}`)
}

// Modify analyzeOCTImage to accept optional patient_id
export async function analyzeOCTImage(
  file: File,
  patientId?: string
): Promise<ScanResult> {
  const formData = new FormData()
  formData.append("file", file)
  if (patientId) formData.append("patient_id", patientId)
  
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    body: formData,
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => null)
    throw new Error(error?.detail ?? `Server error: ${response.status}`)
  }
  
  const data: BackendAnalysisResponse = await response.json()
  return adaptApiResponseToScanResult(data)
}
```

### Update `UX/lib/store.tsx`

```typescript
// Modify AppState to sync with backend

interface AppState {
  // ... existing fields ...
  loadPatientsFromBackend: () => Promise<void>  // NEW
  createPatientOnBackend: (data: CreatePatientDto) => Promise<Patient>  // NEW
  deletePatientFromBackend: (id: string) => Promise<void>  // NEW
  validateScanOnBackend: (scanId: string, validation: ValidationData) => Promise<void>  // NEW
}

export function AppProvider({ children }: { children: ReactNode }) {
  // ... existing state ...
  
  // Load patients from backend on mount
  useEffect(() => {
    loadPatientsFromBackend()
  }, [])
  
  const loadPatientsFromBackend = useCallback(async () => {
    try {
      const patients = await getPatients()
      setPatients(patients)
    } catch (error) {
      console.error("Error loading patients:", error)
    }
  }, [])
  
  const createPatientOnBackend = useCallback(async (data) => {
    const newPatient = await createPatient(data)
    setPatients(prev => [...prev, newPatient])
    return newPatient
  }, [])
  
  // ... implement other methods ...
}
```

---

## 7. Migration Path

### Phase 1: Backend Changes (1-2 hours)
- [x] Create Patient model
- [x] Update OCTScan model
- [x] Create migration script
- [x] Add patient CRUD endpoints
- [x] Add scan validation endpoints
- [x] Test with Postman/Insomnia

### Phase 2: Frontend Integration (2-3 hours)
- [ ] Update api.ts with patient functions
- [ ] Update store.tsx to load from backend
- [ ] Update patient-context-panel.tsx to sync
- [ ] Update scanner-dashboard.tsx to persist
- [ ] Test integration end-to-end

### Phase 3: Validation (1-2 hours)
- [ ] Test patient creation → scan association
- [ ] Test patient deletion cascades
- [ ] Test data persistence across page refresh
- [ ] Test backend API with Swagger
- [ ] Compare frontend/backend data

---

## 8. Validation Checklist

- [ ] All data persists to SQLite database
- [ ] Patients survive page refresh
- [ ] Scans correctly linked to patients
- [ ] Age computed from DOB on backend
- [ ] Doctor labels stored and retrieved
- [ ] Validation status tracked
- [ ] DELETE patient cascades to scans
- [ ] API responses match expected schemas
- [ ] Frontend state matches backend state

---

**Document Generated:** 2026-03-31  
**Status:** Ready for Implementation  
**Effort Estimate:** 4-5 hours total
