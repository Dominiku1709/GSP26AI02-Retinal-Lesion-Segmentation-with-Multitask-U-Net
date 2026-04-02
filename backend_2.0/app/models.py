from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from .database import Base


# ─── Patient Model (NEW) ─────────────────────────────────────────────────────

class Patient(Base):
    __tablename__ = "patients"
    
    # Identifiers
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Info
    name = Column(String, nullable=False, index=True)
    dob = Column(Date, nullable=True)  # Date of birth (used to compute age)
    gender = Column(String, default="Other")  # "Male", "Female", "Other"
    
    # Contact & Medical
    contact = Column(String, nullable=True)
    medical_notes = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships — link a patient to their scans
    scans = relationship("OCTScan", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}')>"
    
    @property
    def age(self) -> int:
        """Computed property: calculate age from DOB"""
        if not self.dob:
            return 0
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


# ─── OCTScan Model (UPDATED) ────────────────────────────────────────────────

class OCTScan(Base):
    __tablename__ = "oct_scans"

    # Unique identifier for each record
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key to Patient (NEW) — allows deletion cascade
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=True)
    
    # The name of the file saved in /storage/
    filename = Column(String, nullable=False)
    
    # The output from your AI model
    lesion_type = Column(String, index=True)
    
    # The probability/confidence score (e.g., 0.98)
    confidence = Column(Float)
    
    # Segmentation mask as Base64 PNG (NEW)
    segmentation_mask_base64 = Column(String, nullable=True)
    
    # Doctor's validation fields (NEW)
    doctor_label = Column(String, nullable=True)
    validation_status = Column(String, default="pending")  # "pending", "approved", "edited"
    validation_notes = Column(String, nullable=True)
    
    # Automatic timestamp of when the scan was processed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship back to Patient
    patient = relationship("Patient", back_populates="scans")

    def __repr__(self):
        return f"<OCTScan(id={self.id}, type='{self.lesion_type}', patient_id={self.patient_id})>"