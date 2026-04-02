# ✅ Quick Integration Checklist & Action Items

**Last Updated:** March 31, 2026  
**Status:** Ready for Development Sprint

---

## 🎯 Current State

### ✅ What's Already Working

- [x] Frontend UI built (Next.js + Shadcn/UI)
- [x] Backend API running (FastAPI)
- [x] Image upload & processing flow complete
- [x] AI analysis execution (with mock fallback)
- [x] Result display (confidence, lesions, mask)
- [x] PDF export functionality
- [x] Patient selection in UI (frontend-only)
- [x] CORS configured for communication
- [x] Database schema defined

### ⚠️ What Needs Connection

- [ ] Patient data persistence (in-memory → database)
- [ ] Patient CRUD API endpoints
- [ ] Patient-Scan association
- [ ] History retrieval display
- [ ] Doctor validation persistence
- [ ] Data survives page refresh

---

## 🚀 Immediate Action Items (Next 48 Hours)

### Priority 1: Backend Patient Model (2 hours)

**File:** `backend_2.0/app/models.py`

**Task:** Add Patient model to database

```python
# Copy this into models.py

from sqlalchemy.orm import relationship
from sqlalchemy import Date, ForeignKey
from datetime import date

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    dob = Column(Date, nullable=True)
    gender = Column(String, default="Other")
    contact = Column(String, nullable=True)
    medical_notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    scans = relationship("OCTScan", back_populates="patient", cascade="all, delete-orphan")
    
    @property
    def age(self) -> int:
        if not self.dob:
            return 0
        today = date.today()
        age = today.year - self.dob.year
        if (today.month, today.day) < (self.dob.month, self.dob.day):
            age -= 1
        return age

# Modify OCTScan
class OCTScan(Base):
    # ... existing code ...
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=True)
    doctor_label = Column(String, nullable=True)
    validation_status = Column(String, default="pending")
    
    patient = relationship("Patient", back_populates="scans")
```

**✓ Do This Next:**
1. Backup `oct_app.db` (or delete to recreate)
2. Update models.py
3. Restart backend
4. Verify: `SELECT * FROM patients;` returns empty table

---

### Priority 2: Patient API Endpoints (2 hours)

**File:** `backend_2.0/app/api/endpoints.py`

**Task:** Add 5 new endpoints

```python
# Add to endpoints.py

@router.post("/patients")
async def create_patient(patient_data: dict, db: Session = Depends(get_db)):
    """Create new patient"""
    new_patient = models.Patient(
        name=patient_data["name"],
        dob=patient_data.get("dob"),
        gender=patient_data.get("gender", "Other"),
        contact=patient_data.get("contact"),
        medical_notes=patient_data.get("medical_notes")
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.get("/patients")
async def list_patients(db: Session = Depends(get_db), limit: int = 50):
    """Get all patients"""
    return db.query(models.Patient).order_by(models.Patient.created_at.desc()).limit(limit).all()

@router.get("/patients/{patient_id}")
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get patient with scans"""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/patients/{patient_id}")
async def update_patient(patient_id: int, data: dict, db: Session = Depends(get_db)):
    """Update patient"""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in data.items():
        if value is not None:
            setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient

@router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete patient"""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"message": "Deleted"}
```

**✓ Verify With:**
```bash
# Test create patient
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "gender": "Male"}'

# Test list patients
curl http://localhost:8000/api/v1/patients

# Check Swagger UI
http://localhost:8000/docs
```

---

### Priority 3: Frontend API Client Update (1.5 hours)

**File:** `UX/lib/api.ts`

**Task:** Add patient functions

```typescript
// Add to api.ts after analyzeOCTImage

// PATIENT FUNCTIONS
export async function createPatient(data: {
  name: string
  dob?: string
  gender?: string
  contact?: string
  medicalNotes?: string
}): Promise<any> {
  const response = await fetch(`${API_BASE}/patients`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(`Failed to create patient`)
  return response.json()
}

export async function getPatients(): Promise<any[]> {
  const response = await fetch(`${API_BASE}/patients`)
  if (!response.ok) throw new Error(`Failed to fetch patients`)
  return response.json()
}

export async function getPatient(id: number): Promise<any> {
  const response = await fetch(`${API_BASE}/patients/${id}`)
  if (!response.ok) throw new Error(`Failed to fetch patient`)
  return response.json()
}

export async function updatePatient(id: number, data: any): Promise<any> {
  const response = await fetch(`${API_BASE}/patients/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(`Failed to update patient`)
  return response.json()
}

export async function deletePatient(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/patients/${id}`, {
    method: "DELETE",
  })
  if (!response.ok) throw new Error(`Failed to delete patient`)
}
```

**✓ Test With:**
```bash
cd UX
pnpm dev
# Open console in browser
# Try: await window.createPatient({name: "Test"})
```

---

### Priority 4: Frontend Store Update (1.5 hours)

**File:** `UX/lib/store.tsx`

**Task:** Sync patient state with backend

```typescript
// Modify AppProvider

export function AppProvider({ children }: { children: ReactNode }) {
  // ... existing state ...
  
  // Add this new function
  const loadPatientsFromBackend = useCallback(async () => {
    try {
      const patientsData = await getPatients()  // Import this function
      setPatients(patientsData)
    } catch (error) {
      console.error("Error loading patients:", error)
    }
  }, [])
  
  // Load on mount
  React.useEffect(() => {
    loadPatientsFromBackend()
  }, [])
  
  // Update addNewPatient to persist to backend
  const addNewPatient = useCallback(
    async (patient: any) => {
      try {
        const newPatient = await createPatient({  // Call API
          name: patient.name,
          dob: patient.dob,
          gender: patient.gender,
          contact: patient.contact,
          medical_notes: patient.medicalNotes
        })
        setPatients((prev) => [...prev, newPatient])
        return newPatient
      } catch (error) {
        console.error("Error creating patient:", error)
        throw error
      }
    },
    []
  )
  
  return (
    <AppContext.Provider
      value={{
        // ... all existing values ...
        loadPatientsFromBackend,  // Add this
      }}
    >
      {children}
    </AppContext.Provider>
  )
}
```

**✓ Test:**
1. Refresh page
2. New patients should persist
3. Open DevTools → Network tab
4. See API calls to `/patients`

---

## 📋 Testing After Each Step

### After Step 1 (Backend Patient Model)

```bash
# 1. Restart backend
cd backend_2.0
python -m uvicorn app.main:app --reload

# 2. Check database
sqlite3 oct_app.db ".schema patients"

# 3. Should see:
# CREATE TABLE patients (
#   id INTEGER PRIMARY KEY,
#   name VARCHAR NOT NULL,
#   ...
# )
```

### After Step 2 (Patient Endpoints)

```bash
# Test endpoint
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","gender":"Female"}'

# Should return:
# {"id":1,"name":"Alice","gender":"Female","created_at":"..."}
```

### After Step 3 (Frontend API Client)

```bash
# In browser console
await getPatients()  // Should return array

await createPatient({name: "Bob", gender: "Male"})  // Should create
```

### After Step 4 (Frontend Store)

```bash
# 1. Open frontend: http://localhost:3000
# 2. Refresh page
# 3. Switch to "Existing" patient mode
# 4. Should show: "Loading... -> Existing patients list"
# 5. Create new patient -> should appear in list
```

---

## 🔄 Full Integration Flow Test

**After all 4 steps, test complete flow:**

```
1. Open frontend: http://localhost:3000
2. Create new patient "John Smith"
   ✓ Patient appears in "Existing" list
   ✓ Refresh page: patient still there
3. Select patient "John Smith"
4. Upload OCT image
5. See analysis results
6. Click "Save to Patient Record"
   ✓ Scan saved to database
   ✓ Verify in backend: sqlite3 oct_app.db "SELECT * FROM oct_scans WHERE patient_id=1"
7. Refresh page
   ✓ Patient & scan still there
   ✓ Can see patient's scan history
```

---

## 📊 Success Metrics

After integration, verify:

- ✅ Patients created → stored in database
- ✅ Patients retrieved → shown in UI
- ✅ Scans created → linked to patient
- ✅ Data persists across refresh
- ✅ CRUD operations work (Create, Read, Update, Delete)
- ✅ Doctor labels/validations saved
- ✅ Cascade delete works (delete patient → deletes scans)
- ✅ API response times < 500ms
- ✅ No validation errors in console
- ✅ Swagger API documentation updated

---

## 📞 Troubleshooting

### "Database locked" error
```
→ Delete oct_app.db and restart backend
```

### "CORS error" when making API calls
```
→ Verify backend CORS config in app/main.py
→ Restart backend server
```

### "Patients not showing"
```
→ Check Network tab: is GET /patients succeeding?
→ Console: useAppState() returns correct patient list?
→ Verify: loadPatientsFromBackend() called on mount
```

### "Changes not persisting"
```
→ Check: Is API call succeeding? (Network tab)
→ Check: Backend database updated? (sqlite3 oct_app.db)
→ Check: Frontend state updated? (React DevTools)
```

### "Old data showing after delete"
```
→ Clear browser cache: Ctrl+Shift+Delete
→ Hard refresh: Ctrl+Shift+R
→ Or check localStorage: Client data persisting?
```

---

## 🎓 Learning Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLAlchemy Relationships:** https://docs.sqlalchemy.org/en/20/orm/relationships.html
- **React Context Performance:** https://react.dev/reference/react/useContext
- **Next.js Fetch Best Practices:** https://nextjs.org/docs/app/building-your-application/data-fetching

---

## ⏱️ Time Estimates

| Task | Time | Priority |
|------|------|----------|
| Backend Patient Model | 30 min | 🔴 HIGH |
| Patient CRUD Endpoints | 1 hr | 🔴 HIGH |
| Frontend API Functions | 1 hr | 🔴 HIGH |
| Frontend Store Sync | 1.5 hr | 🔴 HIGH |
| E2E Testing | 1 hr | 🟡 MEDIUM |
| Documentation Update | 30 min | 🟡 MEDIUM |
| **TOTAL** | **~5 hours** | |

---

## ✍️ Dev Notes

- Start with **Priority 1** first thing in the morning
- After each priority, run the "Test After" commands
- If something breaks, don't move forward — fix it first
- Use Swagger UI (http://localhost:8000/docs) to test endpoints before assuming frontend works
- Check browser console for React errors (might be UI mismatch)
- Check Network tab for API call failures

---

**Next Milestone:** Patient data persists + survives refresh ✅  
**Estimated Completion:** Same day (5 hours work)  
**Blocker:** None identified

---

**Generated by:** Project Analysis  
**Date:** March 31, 2026  
**Contact:** Development Team
