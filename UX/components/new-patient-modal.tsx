"use client"

import { useState } from "react"
import { useAppState } from "@/lib/store"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

function computeAge(dateStr: string) {
  if (!dateStr) return 0
  const today = new Date()
  const birth = new Date(dateStr)
  let age = today.getFullYear() - birth.getFullYear()
  const m = today.getMonth() - birth.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--
  return age
}

export function NewPatientModal() {
  const { newPatientModalOpen, setNewPatientModalOpen, addNewPatient } = useAppState()
  const [name, setName] = useState("")
  const [dob, setDob] = useState("")
  const [gender, setGender] = useState("Male")

  const reset = () => { setName(""); setDob(""); setGender("Male") }

  const handleClose = () => { setNewPatientModalOpen(false); reset() }

  const handleSubmit = () => {
    if (!name.trim()) return
    addNewPatient({
      name: name.trim(),
      age: computeAge(dob),
      dob,
      gender,
      lastVisit: new Date().toISOString().split("T")[0],
    })
    handleClose()
  }

  if (!newPatientModalOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-sm rounded-xl border border-border bg-card p-6 shadow-lg">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-base font-semibold text-foreground">New Patient</h2>
          <button onClick={handleClose} className="rounded-md p-1.5 text-muted-foreground hover:bg-muted">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex flex-col gap-4">
          {/* Name */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-foreground">
              Full Name <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              placeholder="e.g. Jane Smith"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* DOB */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-foreground">Date of Birth</label>
            <div className="flex gap-2">
              <input
                type="date"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
                className="flex-1 rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {dob && (
                <span className="flex items-center rounded-lg bg-muted px-2.5 text-sm font-medium text-foreground">
                  {computeAge(dob)}y
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
                  onClick={() => setGender(g)}
                  className={cn(
                    "flex-1 rounded-md py-1.5 text-xs font-medium transition-all",
                    gender === g
                      ? "bg-card text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-2 mt-6">
          <button
            onClick={handleClose}
            className="flex-1 rounded-lg border border-border bg-card py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!name.trim()}
            className="flex-1 rounded-lg bg-primary py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-40 transition-colors"
          >
            Create Patient
          </button>
        </div>
      </div>
    </div>
  )
}
