// component/patients/patient-profile.tsx
"use client"

import { useAppState, type Patient, type ScanResult } from "@/lib/store"
import { X, Activity, ScanLine, Calendar } from "lucide-react"
import { cn } from "@/lib/utils"

export function PatientProfile({
  patient,
  onClose,
}: {
  patient: Patient
  onClose: () => void
}) {
  const { setCurrentPage } = useAppState()

  const lesionColor = (name: string) => {
    if (name === "AMD")    return "#ef4444"
    if (name === "DME")    return "#f59e0b"
    if (name === "Normal") return "#10b981"
    return "#64748b"
  }

  return (
    <div className="flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-base font-semibold text-primary">
            {patient.name.split(" ").map((n) => n[0]).join("")}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-foreground">{patient.name}</h2>
            <p className="text-sm text-muted-foreground">
              {patient.id} · {patient.age}y · {patient.gender}
              {patient.dob && ` · DOB: ${patient.dob}`}
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-lg bg-card border border-border p-3 flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <ScanLine className="h-3.5 w-3.5" />
            <span className="text-xs">Total Scans</span>
          </div>
          <span className="text-xl font-bold text-foreground">{patient.totalScans}</span>
        </div>
        <div className="rounded-lg bg-card border border-border p-3 flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <Calendar className="h-3.5 w-3.5" />
            <span className="text-xs">Last Visit</span>
          </div>
          <span className="text-sm font-semibold text-foreground">{patient.lastVisit || "—"}</span>
        </div>
      </div>

      {/* Scan History */}
      <div className="flex flex-col gap-2">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
          <Activity className="h-3.5 w-3.5" />
          Scan History
        </h3>

        {patient.scans.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border p-6 text-center">
            <p className="text-xs text-muted-foreground">No scans yet.</p>
            <button
              onClick={() => setCurrentPage("scanner")}
              className="mt-2 text-xs font-medium text-primary hover:underline"
            >
              Go to scanner
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {patient.scans.map((scan) => {
              const lesion = scan.lesionTypes[0]
              return (
                <div
                  key={scan.id}
                  className="rounded-lg bg-card border border-border p-3 flex items-center gap-3"
                >
                  <div
                    className="h-2.5 w-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: lesion ? lesionColor(lesion.name) : "#64748b" }}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground">
                      {lesion?.name ?? "Unknown"}
                    </p>
                    <p className="text-xs text-muted-foreground">{scan.date}</p>
                  </div>
                  <span className="text-xs font-semibold text-foreground shrink-0">
                    {scan.confidence}%
                  </span>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
