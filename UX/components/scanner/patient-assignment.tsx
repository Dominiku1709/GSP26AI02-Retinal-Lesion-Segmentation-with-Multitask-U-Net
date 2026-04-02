"use client"

import { useAppState } from "@/lib/store"
import { useState, useMemo } from "react"
import { Search, Check, UserPlus } from "lucide-react"
import { cn } from "@/lib/utils"

export function PatientAssignment() {
  const {
    patients,
    currentScan,
    selectedPatientId,
    setSelectedPatientId,
    saveScanToPatient,
    setScannerMode,
    setCurrentScan,
    setUploadedFile,
    setNewPatientModalOpen,
  } = useAppState()

  const [search, setSearch] = useState("")
  const [saved, setSaved] = useState(false)

  const filteredPatients = useMemo(
    () =>
      patients.filter(
        (p) =>
          p.name.toLowerCase().includes(search.toLowerCase()) ||
          p.id.toLowerCase().includes(search.toLowerCase())
      ),
    [patients, search]
  )

  const handleSave = () => {
    if (!selectedPatientId || !currentScan) return
    saveScanToPatient(selectedPatientId, currentScan)
    setSaved(true)
    setTimeout(() => {
      setSaved(false)
      setScannerMode("upload")
      setCurrentScan(null)
      setUploadedFile(null)
      setSelectedPatientId(null)
    }, 1500)
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-foreground">Assign to Patient</h3>
        <button
          onClick={() => setNewPatientModalOpen(true)}
          className="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-primary hover:bg-primary/10 transition-colors"
        >
          <UserPlus className="h-3.5 w-3.5" />
          New Patient
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search patients..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-md border border-input bg-background py-2 pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
        />
      </div>

      <div className="flex max-h-48 flex-col gap-1 overflow-y-auto">
        {filteredPatients.map((patient) => (
          <button
            key={patient.id}
            onClick={() => setSelectedPatientId(patient.id)}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors",
              selectedPatientId === patient.id
                ? "bg-primary/10 border border-primary/30"
                : "border border-transparent hover:bg-muted"
            )}
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-xs font-medium text-foreground">
              {patient.name
                .split(" ")
                .map((n) => n[0])
                .join("")}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">{patient.name}</p>
              <p className="text-xs text-muted-foreground">
                {patient.id} / {patient.age}y / {patient.totalScans} scans
              </p>
            </div>
            {selectedPatientId === patient.id && (
              <Check className="h-4 w-4 shrink-0 text-primary" />
            )}
          </button>
        ))}
      </div>

      <button
        onClick={handleSave}
        disabled={!selectedPatientId || !currentScan || saved}
        className={cn(
          "w-full rounded-lg px-4 py-2.5 text-sm font-medium transition-all",
          saved
            ? "bg-emerald-600 text-white"
            : "bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        )}
      >
        {saved ? (
          <span className="flex items-center justify-center gap-2">
            <Check className="h-4 w-4" /> Saved to Record
          </span>
        ) : (
          "Save to Patient Record"
        )}
      </button>
    </div>
  )
}
