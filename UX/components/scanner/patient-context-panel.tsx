"use client"

import { useState, useMemo } from "react"
import { useAppState, type Patient } from "@/lib/store"
import { cn } from "@/lib/utils"
import { Search, UserPlus, UserCheck, Check, User, CheckCircle2, AlertCircle } from "lucide-react"

type PatientMode = "existing" | "new"

export interface NewPatientFormData {
  name: string
  dob: string
  gender: string
}

interface PatientContextPanelProps {
  newPatientForm: NewPatientFormData
  setNewPatientForm: (form: NewPatientFormData) => void
  patientMode: PatientMode
  setPatientMode: (mode: PatientMode) => void
}

function computeAge(dateStr: string) {
  if (!dateStr) return 0
  const today = new Date()
  const birth = new Date(dateStr)
  let age = today.getFullYear() - birth.getFullYear()
  const m = today.getMonth() - birth.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--
  return age
}

function PatientSummaryCard({ patient }: { patient: Patient }) {
  return (
    <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 flex flex-col gap-2">
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
          {patient.name.split(" ").map((n) => n[0]).join("")}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-foreground truncate">{patient.name}</p>
          <p className="text-xs text-muted-foreground">
            {patient.id} · {patient.age}y · {patient.gender}
          </p>
        </div>
      </div>
    </div>
  )
}

export function PatientContextPanel({
  newPatientForm,
  setNewPatientForm,
  patientMode,
  setPatientMode,
}: PatientContextPanelProps) {
  const { patients, selectedPatientId, setSelectedPatientId } = useAppState()
  const [search, setSearch] = useState("")

  const filtered = useMemo(
    () =>
      patients.filter(
        (p) =>
          p.name.toLowerCase().includes(search.toLowerCase()) ||
          p.id.toString().includes(search)
      ),
    [patients, search]
  )

  const selectedPatient = patients.find((p) => p.id === selectedPatientId)

  const handleModeSwitch = (mode: PatientMode) => {
    setPatientMode(mode)
    if (mode === "new") setSelectedPatientId(null)
  }

  const updateField = (field: keyof NewPatientFormData, value: string) => {
    setNewPatientForm({ ...newPatientForm, [field]: value })
  }

  // Compute validation status for display
  const isValidationReady = useMemo(() => {
    if (patientMode === "existing") {
      return !!selectedPatientId
    }
    return newPatientForm.name.trim().length > 0
  }, [patientMode, selectedPatientId, newPatientForm.name])

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center gap-2 mb-3">
          <User className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold text-foreground">Patient</h2>
        </div>
        <div className="flex rounded-lg bg-muted p-0.5">
          <button
            onClick={() => handleModeSwitch("existing")}
            className={cn(
              "flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium transition-all",
              patientMode === "existing"
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <UserCheck className="h-3.5 w-3.5" />
            Existing
          </button>
          <button
            onClick={() => handleModeSwitch("new")}
            className={cn(
              "flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium transition-all",
              patientMode === "new"
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <UserPlus className="h-3.5 w-3.5" />
            New
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {patientMode === "existing" ? (
          <div className="flex flex-col gap-3">
            {/* Empty state */}
            {patients.length === 0 && (
              <div className="rounded-lg border border-dashed border-border p-6 text-center">
                <p className="text-xs text-muted-foreground">No patients yet.</p>
                <button
                  onClick={() => handleModeSwitch("new")}
                  className="mt-2 text-xs font-medium text-primary hover:underline"
                >
                  Create the first patient
                </button>
              </div>
            )}

            {patients.length > 0 && (
              <>
                <div className="relative">
                  <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search by name or ID..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full rounded-lg border border-input bg-background py-2 pl-8 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>

                {selectedPatient && <PatientSummaryCard patient={selectedPatient} />}

                <div className="flex flex-col gap-1">
                  <span className="text-xs font-medium text-muted-foreground px-1 mb-1">
                    {selectedPatient ? "Switch patient" : "Select patient"}
                  </span>
                  {filtered.map((patient) => (
                    <button
                      key={patient.id}
                      onClick={() => setSelectedPatientId(patient.id)}
                      className={cn(
                        "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-left transition-all",
                        selectedPatientId === patient.id
                          ? "bg-primary/8 ring-1 ring-primary/25"
                          : "hover:bg-muted"
                      )}
                    >
                      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-medium text-foreground">
                        {patient.name.split(" ").map((n) => n[0]).join("")}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">{patient.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {patient.id} · {patient.age}y · {patient.gender}
                        </p>
                      </div>
                      {selectedPatientId === patient.id && (
                        <Check className="h-3.5 w-3.5 shrink-0 text-primary" />
                      )}
                    </button>
                  ))}
                  {filtered.length === 0 && patients.length > 0 && (
                    <p className="py-4 text-center text-xs text-muted-foreground">No results</p>
                  )}
                </div>
              </>
            )}
          </div>
        ) : (
          /* New Patient Form */
          <div className="flex flex-col gap-3.5">
            <p className="text-xs text-muted-foreground">
              Patient is created when the scan is saved.
            </p>

            {/* Name */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="pcp-name" className="text-xs font-medium text-foreground">
                Full Name <span className="text-destructive">*</span>
              </label>
              <input
                id="pcp-name"
                type="text"
                placeholder="e.g. Jane Smith"
                value={newPatientForm.name}
                onChange={(e) => updateField("name", e.target.value)}
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            {/* DOB */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="pcp-dob" className="text-xs font-medium text-foreground">
                Date of Birth
              </label>
              <div className="flex gap-2">
                <input
                  id="pcp-dob"
                  type="date"
                  value={newPatientForm.dob}
                  onChange={(e) => updateField("dob", e.target.value)}
                  className="flex-1 rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                />
                {newPatientForm.dob && (
                  <span className="flex items-center rounded-lg bg-muted px-2.5 text-sm font-medium text-foreground">
                    {computeAge(newPatientForm.dob)}y
                  </span>
                )}
              </div>
            </div>

            {/* Gender */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-foreground">Gender</label>
              <div className="flex rounded-lg bg-muted p-0.5">
                {["Male", "Female", "Other"].map((g) => (
                  <button
                    key={g}
                    onClick={() => updateField("gender", g)}
                    className={cn(
                      "flex-1 rounded-md py-1.5 text-xs font-medium transition-all",
                      newPatientForm.gender === g
                        ? "bg-card text-foreground shadow-sm"
                        : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    {g}
                  </button>
                ))}
              </div>
            </div>

            {/* Preview */}
            {newPatientForm.name.trim() && (
              <div className="rounded-lg border border-dashed border-primary/30 bg-primary/5 p-2.5">
                <p className="text-xs text-primary font-medium">
                  Ready: &quot;{newPatientForm.name.trim()}&quot;
                  {newPatientForm.dob && ` · ${computeAge(newPatientForm.dob)}y`}
                  {newPatientForm.gender && ` · ${newPatientForm.gender}`}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Validation Status Footer */}
      <div className="border-t border-border px-4 py-3 bg-card">
        <div className="flex items-center gap-2">
          {isValidationReady ? (
            <>
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-emerald-700">
                  {patientMode === "existing" ? "Patient selected" : "Patient ready"}
                </p>
                <p className="text-xs text-emerald-600 truncate">
                  {patientMode === "existing" 
                    ? selectedPatient?.name 
                    : `"${newPatientForm.name.trim()}"`}
                </p>
              </div>
            </>
          ) : (
            <>
              <AlertCircle className="h-4 w-4 text-amber-600" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-amber-700">Incomplete</p>
                <p className="text-xs text-amber-600">
                  {patientMode === "existing" 
                    ? "Select a patient to continue" 
                    : "Enter patient name"}
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
