// component/patients/patients-dashboard.tsx
"use client"

import { useState } from "react"
import type { Patient } from "@/lib/store"
import { useAppState } from "@/lib/store"
import { PatientList } from "./patient-list"
import { PatientProfile } from "./patient-profile"
import { NewPatientModal } from "@/components/new-patient-modal"
import { DoctorHeader } from "@/components/doctor-header"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu"
import { Users, MoreHorizontal } from "lucide-react"

export function PatientsDashboard() {
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)
  const { setNewPatientModalOpen, patients, deletePatient } = useAppState()

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
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                <MoreHorizontal className="h-4 w-4" />
                Manage Patient
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <button onClick={() => setNewPatientModalOpen(true)}>
                  Add Patient
                </button>
              </DropdownMenuItem>
              <DropdownMenuItem asChild disabled={!syncedPatient}>
                <button
                  className="w-full text-left text-destructive hover:bg-destructive/10 hover:text-destructive"
                  onClick={async () => {
                    if (!syncedPatient) return
                    const confirmed = window.confirm(
                      `Delete patient ${syncedPatient.name}? This cannot be undone.`
                    )
                    if (!confirmed) return

                    try {
                      await deletePatient(syncedPatient.id)
                      setSelectedPatient(null)
                    } catch (error) {
                      window.alert(
                        error instanceof Error
                          ? error.message
                          : "Failed to delete patient"
                      )
                    }
                  }}
                >
                  Delete Patient
                </button>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
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

      {/*}  Footer */}
      <footer className="py-2 px-6 border-t border-border bg-background">
        <p className="text-[11px] text-center text-muted-foreground">
          This is a graduation project by GSP26AI02 group, mentored by Mr. Le Phu Nguyen 
        </p>
      </footer>

      <NewPatientModal />
    </div>
  )
}
