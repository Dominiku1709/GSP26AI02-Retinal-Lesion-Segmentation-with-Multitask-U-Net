"use client"

import { useState } from "react"
import { useAppState, type ValidationStatus } from "@/lib/store"
import { CheckCircle2, Pencil, ShieldCheck, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

export function ValidationPanel() {
  const { currentScan, setCurrentScan, scannerMode } = useAppState()
  const scan = scannerMode === "review" ? null : currentScan

  const [editMode, setEditMode] = useState(false)
  const [doctorLabel, setDoctorLabel] = useState(scan?.doctorLabel ?? "")

  if (!scan) return null

  const handleApprove = () => {
    const aiLabel = scan.lesionTypes.map((l) => l.name).join(", ")
    setCurrentScan({
      ...scan,
      validationStatus: "approved",
      doctorLabel: doctorLabel.trim() || aiLabel,
    })
    setEditMode(false)
  }

  const handleEdit = () => {
    setEditMode(true)
  }

  const handleSaveEdit = () => {
    if (!doctorLabel.trim()) return
    setCurrentScan({
      ...scan,
      validationStatus: "edited",
      doctorLabel: doctorLabel.trim(),
    })
    setEditMode(false)
  }

  const statusConfig: Record<ValidationStatus, { icon: React.ReactNode; label: string; className: string }> = {
    pending: {
      icon: <AlertTriangle className="h-3.5 w-3.5" />,
      label: "Awaiting Review",
      className: "bg-amber-50 text-amber-700 border-amber-200",
    },
    approved: {
      icon: <CheckCircle2 className="h-3.5 w-3.5" />,
      label: "Approved",
      className: "bg-emerald-50 text-emerald-700 border-emerald-200",
    },
    edited: {
      icon: <Pencil className="h-3.5 w-3.5" />,
      label: "Edited by Doctor",
      className: "bg-sky-50 text-sky-700 border-sky-200",
    },
  }

  const status = statusConfig[scan.validationStatus]

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-medium text-foreground">Clinical Validation</h3>
        </div>
        <span className={cn("flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium", status.className)}>
          {status.icon}
          {status.label}
        </span>
      </div>

      {/* AI predicted label */}
      <div className="rounded-lg bg-card border border-border p-3">
        <span className="text-xs font-medium text-muted-foreground">AI Predicted Diagnosis</span>
        <p className="mt-1 text-sm text-foreground">
          {scan.lesionTypes.map((l) => l.name).join(", ")}
        </p>
      </div>

      {/* Doctor label override */}
      <div className="rounded-lg bg-card border border-border p-3">
        <label htmlFor="doctor-label" className="text-xs font-medium text-muted-foreground">
          Doctor&apos;s Diagnostic Label
        </label>
        {editMode || scan.validationStatus === "pending" ? (
          <textarea
            id="doctor-label"
            rows={2}
            value={doctorLabel}
            onChange={(e) => setDoctorLabel(e.target.value)}
            placeholder="Enter or override the diagnostic label..."
            className="mt-1.5 w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        ) : (
          <p className="mt-1 text-sm text-foreground">
            {scan.doctorLabel || "Not yet provided"}
          </p>
        )}
      </div>

      {/* Action buttons */}
      {scan.validationStatus === "pending" ? (
        <div className="flex gap-2">
          <button
            onClick={handleApprove}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-emerald-600 px-3 py-2.5 text-sm font-medium text-white hover:bg-emerald-700 transition-colors"
          >
            <CheckCircle2 className="h-4 w-4" />
            Approve AI Result
          </button>
          <button
            onClick={() => {
              handleEdit()
              setDoctorLabel("")
            }}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-border bg-card px-3 py-2.5 text-sm font-medium text-foreground hover:bg-muted transition-colors"
          >
            <Pencil className="h-4 w-4" />
            Edit / Reject
          </button>
        </div>
      ) : editMode ? (
        <div className="flex gap-2">
          <button
            onClick={handleSaveEdit}
            disabled={!doctorLabel.trim()}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-primary px-3 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            <CheckCircle2 className="h-4 w-4" />
            Save Changes
          </button>
          <button
            onClick={() => {
              setEditMode(false)
              setDoctorLabel(scan.doctorLabel)
            }}
            className="rounded-lg border border-border bg-card px-3 py-2.5 text-sm font-medium text-foreground hover:bg-muted transition-colors"
          >
            Cancel
          </button>
        </div>
      ) : (
        <button
          onClick={handleEdit}
          className="flex items-center justify-center gap-2 rounded-lg border border-border bg-card px-3 py-2.5 text-sm font-medium text-foreground hover:bg-muted transition-colors"
        >
          <Pencil className="h-4 w-4" />
          Edit Label
        </button>
      )}
    </div>
  )
}
