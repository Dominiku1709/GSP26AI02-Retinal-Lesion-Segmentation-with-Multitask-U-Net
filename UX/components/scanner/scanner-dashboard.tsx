"use client"

import { useState, useMemo, useCallback, useEffect } from "react"
import { useAppState, type ScanResult, type Patient } from "@/lib/store"
import { ImageUploader } from "./image-uploader"
import { ProcessingOverlay } from "./processing-overlay"
import { AnalysisViewer } from "./analysis-viewer"
import { PatientContextPanel, type NewPatientFormData } from "./patient-context-panel"
import { DoctorHeader } from "@/components/doctor-header"
import { fetchAvailableModels, selectModel } from "@/lib/api"
import { cn } from "@/lib/utils"
import {
  ScanLine,
  ArrowLeft,
  ShieldCheck,
  Activity,
  Clock,
  Target,
  CheckCircle2,
  Pencil,
  AlertTriangle,
  FileText,
  Check,
  Save,
  Layers,
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"

type PatientMode = "existing" | "new"

function computeAge(dateStr: string) {
  if (!dateStr) return 0
  const today = new Date()
  const birth = new Date(dateStr)
  let age = today.getFullYear() - birth.getFullYear()
  const m = today.getMonth() - birth.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--
  return age
}

/* ─── Results Right Panel ────────────────────────────────── */

function ResultsPanel({
  scan,
  isReview,
  patientMode,
  newPatientForm,
}: {
  scan: ScanResult
  isReview: boolean
  patientMode: PatientMode
  newPatientForm: NewPatientFormData
}) {
  const {
    currentScan,
    setCurrentScan,
    selectedPatientId,
    patients,
    saveScanToPatient,
    addNewPatient,
    setScannerMode,
    setUploadedFile,
    setSelectedPatientId,
    doctor,
  } = useAppState()

  const [editMode, setEditMode] = useState(false)
  const [doctorLabel, setDoctorLabel] = useState(scan.doctorLabel ?? "")
  const [saved, setSaved] = useState(false)

  const selectedPatient = useMemo(
    () => patients.find((p) => p.id === selectedPatientId),
    [patients, selectedPatientId]
  )

  const canSave = useMemo(() => {
    if (patientMode === "existing") return !!selectedPatientId
    return !!newPatientForm.name.trim()
  }, [patientMode, selectedPatientId, newPatientForm.name])

  const handleApprove = () => {
    if (!currentScan) return
    const aiLabel = scan.lesionTypes.map((l) => l.name).join(", ")
    setCurrentScan({
      ...currentScan,
      doctorLabel: doctorLabel.trim() || aiLabel,
    })
    setEditMode(false)
  }

  const handleEdit = () => {
    setEditMode(true)
  }

  const handleSaveEdit = () => {
    if (!doctorLabel.trim() || !currentScan) return
    setCurrentScan({
      ...currentScan,
      doctorLabel: doctorLabel.trim(),
    })
    setEditMode(false)
  }

  const handleSaveToRecord = useCallback(async () => {
    if (!currentScan) return

    let targetPatientId = selectedPatientId

    if (patientMode === "new" && newPatientForm.name.trim()) {
      const newPatient = await addNewPatient({
        name: newPatientForm.name.trim(),
        dob: newPatientForm.dob || undefined,
        gender: newPatientForm.gender,
       
      })
      targetPatientId = newPatient.id
    }

    if (!targetPatientId) return

    saveScanToPatient(targetPatientId, currentScan)
    setSaved(true)

    setTimeout(() => {
      setSaved(false)
      setScannerMode("upload")
      setCurrentScan(null)
      setUploadedFile(null)
      setSelectedPatientId(null)
    }, 1500)
  }, [
    currentScan,
    selectedPatientId,
    patientMode,
    newPatientForm,
    addNewPatient,
    saveScanToPatient,
    setScannerMode,
    setCurrentScan,
    setUploadedFile,
    setSelectedPatientId,
  ])

  const handleExportPdf = () => {
    generatePdfReport(scan, selectedPatient ?? null, doctor.name)
  }

  // Default status - simplified without validation tracking
  const status = {
    icon: <CheckCircle2 className="h-3 w-3" />,
    label: "Pending Review",
    className: "bg-amber-50 text-amber-700 border-amber-200",
  }

  return (
    <div className="flex h-full flex-col">
      {/* Panel Header */}
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">
            {isReview ? "Scan Details" : "Results & Validation"}
          </h2>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {/* Inference Metrics */}
        <div className="flex flex-col gap-2.5">
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            AI Metrics
          </h3>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex flex-col gap-1 rounded-lg bg-card border border-border p-2.5">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <ShieldCheck className="h-3 w-3" />
                <span className="text-xs">Confidence</span>
              </div>
              <span className="text-lg font-bold text-foreground">{scan.confidence}%</span>
              <div className="h-1 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary transition-all"
                  style={{ width: `${scan.confidence}%` }}
                />
              </div>
            </div>
            <div className="flex flex-col gap-1 rounded-lg bg-card border border-border p-2.5">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span className="text-xs">Reponse time</span>
              </div>
              <span className="text-lg font-bold text-foreground">{scan.responseTime}ms</span>
              
            </div>
            <div className="flex flex-col gap-1 rounded-lg bg-card border border-border p-2.5">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Target className="h-3 w-3" />
                <span className="text-xs">Lesions</span>
              </div>
              <span className="text-lg font-bold text-foreground">{scan.lesionTypes.length}</span>
              
            </div>
            <div className="flex flex-col gap-1 rounded-lg bg-card border border-border p-2.5">
              <div className="flex items-center gap-1.5 text-muted-foreground">
                <Activity className="h-3 w-3" />
                <span className="text-xs">Model</span>
              </div>
              <span className="text-lg font-bold text-foreground">
                {scan.architecture || "Unknown"}
              </span>
              
            </div>
          </div>

          {/* Lesion Breakdown */}
          <div className="rounded-lg bg-card border border-border p-2.5 flex flex-col gap-1.5">
            <span className="text-xs font-medium text-muted-foreground">Breakdown</span>
            {scan.lesionTypes.map((lesion) => (
              <div key={lesion.name} className="flex items-center gap-2">
                <div
                  className="h-2.5 w-2.5 rounded-sm shrink-0"
                  style={{ backgroundColor: lesion.color }}
                />
                <span className="flex-1 text-xs text-foreground">{lesion.name}</span>
                
              </div>
            ))}
          </div>
        </div>

        {/* Clinical Validation */}
        {!isReview && (
          <div className="flex flex-col gap-2.5">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Validation
              </h3>
              <span
                className={cn(
                  "flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium",
                  status.className
                )}
              >
                {status.icon}
                {status.label}
              </span>
            </div>

            {/* AI Label */}
            <div className="rounded-lg bg-card border border-border p-2.5">
              <span className="text-xs text-muted-foreground">AI Diagnosis</span>
              <p className="text-sm font-medium text-foreground mt-0.5">
                {scan.lesionTypes.map((l) => l.name).join(", ")}
              </p>
            </div>

            {/* Doctor Override */}
            <div className="rounded-lg bg-card border border-border p-2.5">
              <label htmlFor="doc-label" className="text-xs text-muted-foreground">
                Doctor&apos;s Label
              </label>
              {editMode ? (
                <textarea
                  id="doc-label"
                  rows={2}
                  value={doctorLabel}
                  onChange={(e) => setDoctorLabel(e.target.value)}
                  placeholder="Override or confirm diagnosis..."
                  className="mt-1 w-full resize-none rounded-md border border-input bg-background px-2.5 py-1.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                />
              ) : (
                <p className="mt-0.5 text-sm font-medium text-foreground">
                  {scan.doctorLabel || "Not provided"}
                </p>
              )}
            </div>

            {/* Validation Buttons */}
            {!editMode ? (
              <div className="flex gap-2">
                <button
                  onClick={handleApprove}
                  className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-emerald-600 px-2.5 py-2 text-xs font-medium text-white hover:bg-emerald-700 transition-colors"
                >
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  Approve
                </button>
                <button
                  onClick={() => {
                    handleEdit()
                    setDoctorLabel("")
                  }}
                  className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-border bg-card px-2.5 py-2 text-xs font-medium text-foreground hover:bg-muted transition-colors"
                >
                  <Pencil className="h-3.5 w-3.5" />
                  Edit / Reject
                </button>
              </div>
            ) : editMode ? (
              <div className="flex gap-2">
                <button
                  onClick={handleSaveEdit}
                  disabled={!doctorLabel.trim()}
                  className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-primary px-2.5 py-2 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
                >
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  Save
                </button>
                <button
                  onClick={() => {
                    setEditMode(false)
                    setDoctorLabel(scan.doctorLabel)
                  }}
                  className="rounded-lg border border-border bg-card px-2.5 py-2 text-xs font-medium text-foreground hover:bg-muted transition-colors"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={handleEdit}
                className="flex items-center justify-center gap-1.5 rounded-lg border border-border bg-card px-2.5 py-2 text-xs font-medium text-foreground hover:bg-muted transition-colors"
              >
                <Pencil className="h-3.5 w-3.5" />
                Edit Label
              </button>
            )}
          </div>
        )}

        {/* Review Mode Status */}
        {isReview && (
          <div className="flex flex-col gap-2.5">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Validation Record
            </h3>
            <div className="rounded-lg bg-card border border-border p-2.5 flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <span
                  className={cn(
                    "flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium",
                    status.className
                  )}
                >
                  {status.icon}
                  {status.label}
                </span>
              </div>
              {scan.doctorLabel && (
                <div>
                  <span className="text-xs text-muted-foreground">Doctor Label</span>
                  <p className="text-sm font-medium text-foreground">{scan.doctorLabel}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* CTA Buttons - Pinned at bottom */}
      {!isReview && (
        <div className="border-t border-border p-4 flex flex-col gap-2">
          <button
            onClick={handleSaveToRecord}
            disabled={!canSave || saved}
            className={cn(
              "w-full flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all",
              saved
                ? "bg-emerald-600 text-white"
                : "bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40"
            )}
          >
            {saved ? (
              <>
                <Check className="h-4 w-4" />
                Saved to Record
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Save to Patient Record
              </>
            )}
          </button>
          <button
            onClick={handleExportPdf}
            className="w-full flex items-center justify-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors"
          >
            <FileText className="h-4 w-4" />
            Export PDF Report
          </button>
        </div>
      )}
    </div>
  )
}

/* ─── Main Scanner Dashboard ────────────────────────────── */

export function ScannerDashboard() {
  const {
    scannerMode,
    currentScan,
    setScannerMode,
    setCurrentScan,
    setUploadedFile,
    selectedPatientId,
    patientsLoading,
  } = useAppState()

  const [patientMode, setPatientMode] = useState<PatientMode>("existing")
  const [newPatientForm, setNewPatientForm] = useState<NewPatientFormData>({
    name: "",
    dob: "",
    gender: "Male",
  })

  // Compute patient validation status
  const isPatientValid = useMemo(() => {
    if (patientMode === "existing") {
      return !!selectedPatientId
    }
    // For new patient: only name is required
    return newPatientForm.name.trim().length > 0
  }, [patientMode, selectedPatientId, newPatientForm.name])

  const getPatientValidationError = useMemo(() => {
    if (patientMode === "existing") {
      if (!selectedPatientId) return "Please select an existing patient"
      return null
    }
    // For new patient
    if (!newPatientForm.name.trim()) return "Please enter patient name"
    return null
  }, [patientMode, selectedPatientId, newPatientForm.name])

  const activeScan = currentScan
  const isResult = scannerMode === "result" || scannerMode === "processing"

  const [availableModels, setAvailableModels] = useState<string[]>([])
  const [selectedModel, setSelectedModel] = useState<string>("")
  const [modelStatus, setModelStatus] = useState<string | null>(null)
  const [modelError, setModelError] = useState<string | null>(null)

  const loadModelList = useCallback(async () => {
    try {
      const response = await fetchAvailableModels()
      setAvailableModels(response.available_models)
      setSelectedModel(response.selected_model ?? "")
      setModelError(null)
    } catch (error) {
      setModelError(error instanceof Error ? error.message : "Failed to load models")
    }
  }, [])

  useEffect(() => {
    loadModelList()
  }, [loadModelList])

  const handleSelectModel = useCallback(async (modelName: string) => {
    try {
      const response = await selectModel(modelName)
      setSelectedModel(response.selected_model ?? "")
      setAvailableModels(response.available_models)
      setModelStatus(`Selected model: ${modelName}`)
      setModelError(null)
    } catch (error) {
      setModelError(error instanceof Error ? error.message : "Failed to select model")
      setModelStatus(null)
    }
  }, [])

  const handleBackToUpload = () => {
    setScannerMode("upload")
    setCurrentScan(null)
    setUploadedFile(null)
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border bg-card px-5 py-2.5">
        <div className="flex items-center gap-3">
          {isResult && (
            <button
              onClick={handleBackToUpload}
              className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
              aria-label="Back"
            >
              <ArrowLeft className="h-4 w-4" />
            </button>
          )}
          <ScanLine className="h-5 w-5 text-primary" />
          <div>
            <h1 className="text-base font-semibold text-foreground leading-tight">
              {isResult ? "Scan Results" : "OCT Scanner"}
            </h1>
            <p className="text-xs text-muted-foreground">
              Multi-task U-Net retinal lesion segmentation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors"
              >
                <Layers className="h-4 w-4" />
                Select Model
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-64">
              <DropdownMenuLabel>Available models</DropdownMenuLabel>
              {availableModels.length > 0 ? (
                availableModels.map((model) => (
                  <DropdownMenuItem
                    key={model}
                    onSelect={() => handleSelectModel(model)}
                    className={model === selectedModel ? "font-semibold" : ""}
                  >
                    {model}
                  </DropdownMenuItem>
                ))
              ) : (
                <DropdownMenuItem disabled>No models found</DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
          <button
            onClick={() => window.location.href = "/compare-models"}
            className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-3 py-2 text-sm font-medium transition-all shadow-sm hover:shadow-md"
            title="Run all models at once for comparison"
          >
            <Layers className="h-4 w-4" />
            Run all model
          </button>
          <div className="rounded-full border border-border bg-card px-3 py-2 text-xs text-muted-foreground">
            {selectedModel || "Default model"}
          </div>
          <DoctorHeader />
        </div>
      </header>

      {(modelStatus || modelError) && (
        <div className="border-b border-border bg-background px-5 py-2 text-xs text-right text-muted-foreground">
          {modelError ? (
            <span className="text-destructive">{modelError}</span>
          ) : (
            <span className="text-emerald-600">{modelStatus}</span>
          )}
        </div>
      )}

      {/* 3-Column Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Column 1: Patient Context */}
        <aside className="w-72 shrink-0 border-r border-border bg-background overflow-hidden flex flex-col">
          <PatientContextPanel
            newPatientForm={newPatientForm}
            setNewPatientForm={(form) => setNewPatientForm(form)}
            patientMode={patientMode}
            setPatientMode={setPatientMode}
          />
        </aside>

        {/* Column 2: AI Scanning Workspace */}
        <main className="flex-1 overflow-y-auto bg-background">
          {scannerMode === "upload" && (
            <div className="flex h-full items-center justify-center p-6">
              <div className="w-full max-w-lg">
                <div className="flex flex-col items-center gap-2 mb-6 text-center">
                  <h2 className="text-lg font-semibold text-foreground">Upload OCT Image</h2>
                  <p className="text-sm text-muted-foreground">
                    Upload a retinal OCT scan for AI-powered lesion analysis
                  </p>
                </div>
                <ImageUploader 
                  isPatientValid={isPatientValid}
                  patientValidationError={getPatientValidationError}
                />
              </div>
            </div>
          )}

          {scannerMode === "processing" && (
            <div className="flex h-full items-center justify-center p-6">
              <div className="w-full max-w-md">
                <ProcessingOverlay />
              </div>
            </div>
          )}

          {isResult && activeScan && (
            <div className="p-5">
              <AnalysisViewer />
            </div>
          )}
        </main>

        {/* Column 3: Clinical Results & Validation */}
        {isResult && activeScan && (
          <aside className="w-80 shrink-0 border-l border-border bg-background overflow-hidden flex flex-col">
            <ResultsPanel
              scan={activeScan}
              isReview={false}
              patientMode={patientMode}
              newPatientForm={newPatientForm}
            />
          </aside>
        )}
      </div>

            {/*}  Footer */}
      <footer className="py-2 px-6 border-t border-border bg-background">
        <p className="text-[11px] text-center text-muted-foreground">
          This is a graduation project by GSP26AI02 group, mentored by Mr. Le Phu Nguyen 
        </p>
      </footer>
    </div>
  )
}

/* ─── PDF Export Helper ──────────────────────────────────── */

function generatePdfReport(scan: ScanResult, patient: Patient | null, doctorName: string) {
  const w = window.open("", "_blank")
  if (!w) return

  const lesionRows = scan.lesionTypes
    .map(
      (l) =>
        `<tr>
          <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;">
            <span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${l.color};margin-right:8px;vertical-align:middle;"></span>
            ${l.name}
          </td>
          <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;text-align:right;">${l.percentage}%</td>
        </tr>`
    )
    .join("")

  const validationLabel = "Pending Review"

  const html = `<!DOCTYPE html>
<html>
<head>
  <title>OCT Analysis Report - ${patient?.name ?? "Unassigned"}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', -apple-system, sans-serif; color: #1e293b; padding: 40px; max-width: 800px; margin: 0 auto; }
    .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #0d7377; padding-bottom: 16px; margin-bottom: 24px; }
    .logo { font-size: 22px; font-weight: 700; color: #0d7377; }
    .logo span { font-weight: 400; color: #64748b; font-size: 14px; display: block; }
    .meta { text-align: right; font-size: 12px; color: #64748b; }
    h2 { font-size: 16px; font-weight: 600; margin-bottom: 12px; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }
    .field { font-size: 13px; }
    .field .label { color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
    .field .value { font-weight: 500; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 24px; }
    th { text-align: left; padding: 8px 12px; background: #f1f5f9; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; }
    th:last-child { text-align: right; }
    .status { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 500; }
    .status.approved { background: #d1fae5; color: #065f46; }
    .status.edited { background: #dbeafe; color: #1e40af; }
    .status.pending { background: #fef3c7; color: #92400e; }
    .conclusion { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 24px; }
    .footer { border-top: 1px solid #e2e8f0; padding-top: 12px; font-size: 11px; color: #94a3b8; display: flex; justify-content: space-between; }
    @media print { body { padding: 20px; } }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">RetinaAI<span>OCT Retinal Analysis Report</span></div>
    <div class="meta">
      <div>Report ID: ${scan.id}</div>
      <div>Date: ${scan.date}</div>
      <div>Generated: ${new Date().toLocaleString()}</div>
    </div>
  </div>

  <h2>Patient Information</h2>
  <div class="grid">
    <div class="field"><div class="label">Name</div><div class="value">${patient?.name ?? "Not assigned"}</div></div>
    <div class="field"><div class="label">Patient ID</div><div class="value">${patient?.id ?? "N/A"}</div></div>
    <div class="field"><div class="label">Age / Gender</div><div class="value">${patient ? `${patient.age} / ${patient.gender}` : "N/A"}</div></div>
    <div class="field"><div class="label">Date of Birth</div><div class="value">${patient?.dob ?? "N/A"}</div></div>
  </div>

  <h2>AI Analysis Results</h2>
  <div class="grid" style="margin-bottom:16px;">
    <div class="field"><div class="label">Model Confidence</div><div class="value">${scan.confidence}%</div></div>
    <div class="field"><div class="label">Processing Time</div><div class="value">${scan.processingTime}s</div></div>
    <div class="field"><div class="label">Model</div><div class="value">Multi-task U-Net v2.4</div></div>
    <div class="field"><div class="label">Total Lesion Area</div><div class="value">${scan.lesionTypes.reduce((a, l) => a + l.percentage, 0).toFixed(1)}%</div></div>
  </div>

  <table>
    <thead><tr><th>Lesion Type</th><th>Coverage</th></tr></thead>
    <tbody>${lesionRows}</tbody>
  </table>

  <h2>Clinical Validation</h2>
  <div class="conclusion">
    <div style="margin-bottom:8px;">
      <span class="status pending">Pending Review</span>
    </div>
    <div class="field" style="margin-bottom:6px;"><div class="label">Doctor's Diagnostic Label</div><div class="value">${scan.doctorLabel || "Pending doctor review"}</div></div>
  </div>

  <div class="footer">
    <span>Reviewed by: ${doctorName}</span>
    <span>RetinaAI - For clinical use only</span>
  </div>

  <script>window.onload = () => window.print();</script>
</body>
</html>`

  w.document.write(html)
  w.document.close()
}
