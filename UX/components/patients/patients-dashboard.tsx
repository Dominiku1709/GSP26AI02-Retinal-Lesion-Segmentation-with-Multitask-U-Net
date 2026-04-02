// component/patients/patients-dashboard.tsx
"use client"

import { useState } from "react"
import type { Patient } from "@/lib/store"
import { useAppState } from "@/lib/store"
import { PatientList } from "./patient-list"
import { PatientProfile } from "./patient-profile"
import { NewPatientModal } from "@/components/new-patient-modal"
import { DoctorHeader } from "@/components/doctor-header"
import { Users, UserPlus } from "lucide-react"

export function PatientsDashboard() {
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)
  const { setNewPatientModalOpen, patients } = useAppState()

  // Keep selectedPatient in sync with store updates
  const syncedPatient = selectedPatient
    ? patients.find((p) => p.id === selectedPatient.id) ?? null
    : null

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border bg-card px-6 py-3">
        <div className="flex items-center gap-3">
          <Users className="h-5 w-5 text-primary" />
          <div>
            <h1 className="text-lg font-semibold text-foreground">Patient Management</h1>
            <p className="text-xs text-muted-foreground">
              View patient records, scan histories, and clinical data
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setNewPatientModalOpen(true)}
            className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            <UserPlus className="h-4 w-4" />
            Add New Patient
          </button>
          <DoctorHeader />
        </div>
      </header>

      {/* Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Patient List */}
        <div className="flex-1 overflow-y-auto p-6">
          <PatientList
            onSelectPatient={setSelectedPatient}
            selectedId={syncedPatient?.id ?? null}
          />
        </div>

        {/* Patient Detail Panel */}
        {syncedPatient && (
          <aside className="w-[420px] shrink-0 overflow-y-auto border-l border-border bg-background p-6">
            <PatientProfile
              patient={syncedPatient}
              onClose={() => setSelectedPatient(null)}
            />
          </aside>
        )}
      </div>

      <NewPatientModal />
    </div>
  )
}
