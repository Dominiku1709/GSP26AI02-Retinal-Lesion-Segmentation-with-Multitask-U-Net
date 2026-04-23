// component/patients/patient-list.tsx
"use client"

import { useAppState, type Patient } from "@/lib/store"
import { useState, useMemo } from "react"
import { Search, ArrowUpDown, ArrowUp, ArrowDown, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

type SortField = "name" | "age" | "lastVisit" | "totalScans"
type SortDir = "asc" | "desc"

export function PatientList({
  onSelectPatient,
  selectedId,
}: {
  onSelectPatient: (patient: Patient) => void
  selectedId: string | null
}) {
  const { patients } = useAppState()
  const [search, setSearch] = useState("")
  const [sortField, setSortField] = useState<SortField>("lastVisit")
  const [sortDir, setSortDir] = useState<SortDir>("desc")

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"))
    } else {
      setSortField(field)
      setSortDir("asc")
    }
  }

  const filtered = useMemo(() => {
    let result = patients.filter(
      (p) =>
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.id.toLowerCase().includes(search.toLowerCase())
    )

    result.sort((a, b) => {
      let cmp = 0
      switch (sortField) {
        case "name":
          cmp = a.name.localeCompare(b.name)
          break
        case "age":
          cmp = a.age - b.age
          break
        case "lastVisit":
          cmp = (a.last_visit || '').localeCompare(b.last_visit || '')
          break
        case "totalScans":
          cmp = a.total_scans - b.total_scans
          break
      }
      return sortDir === "desc" ? -cmp : cmp
    })

    return result
  }, [patients, search, sortField, sortDir])

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <ArrowUpDown className="h-3 w-3 text-muted-foreground/50" />
    return sortDir === "asc" ? (
      <ArrowUp className="h-3 w-3 text-primary" />
    ) : (
      <ArrowDown className="h-3 w-3 text-primary" />
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search by name or patient ID..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-input bg-card py-2.5 pl-10 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
        />
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        {/* Table Header */}
        <div className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-4 border-b border-border bg-muted/50 px-4 py-2.5">
          <button onClick={() => toggleSort("name")} className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors">
            Patient <SortIcon field="name" />
          </button>
          <button onClick={() => toggleSort("age")} className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors w-16 justify-end">
            Age <SortIcon field="age" />
          </button>
          <button onClick={() => toggleSort("lastVisit")} className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors w-24 justify-end">
            Last Visit <SortIcon field="lastVisit" />
          </button>
          <button onClick={() => toggleSort("totalScans")} className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors w-16 justify-end">
            Scans <SortIcon field="totalScans" />
          </button>
          <div className="w-6" />
        </div>

        {/* Table Body */}
        <div className="flex flex-col divide-y divide-border">
          {filtered.map((patient) => (
            <button
              key={patient.id}
              onClick={() => onSelectPatient(patient)}
              className={cn(
                "grid grid-cols-[1fr_auto_auto_auto_auto] gap-4 px-4 py-3 text-left transition-colors",
                selectedId === patient.id
                  ? "bg-primary/5"
                  : "hover:bg-muted/50"
              )}
            >
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-muted text-xs font-medium text-foreground shrink-0">
                  {patient.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">{patient.name}</p>
                  <p className="text-xs text-muted-foreground">{patient.id}</p>
                </div>
              </div>
              <span className="flex items-center w-16 justify-end text-sm text-foreground">
                {patient.age}
              </span>
              <span className="flex items-center w-24 justify-end text-sm text-muted-foreground">
                {patient.last_visit || '—'}
              </span>
              <span className="flex items-center w-16 justify-end text-sm font-medium text-foreground">
                {patient.total_scans}
              </span>
              <div className="flex items-center w-6">
                <ChevronRight className={cn(
                  "h-4 w-4 transition-colors",
                  selectedId === patient.id ? "text-primary" : "text-muted-foreground/40"
                )} />
              </div>
            </button>
          ))}
          {filtered.length === 0 && (
            <div className="flex items-center justify-center py-12 text-sm text-muted-foreground">
              No patients found
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
