"use client"

import { useAppState } from "@/lib/store"
import { Bell, Settings } from "lucide-react"

export function DoctorHeader() {
  const { doctor } = useAppState()

  return (
    <div className="flex items-center gap-3">
      <button
        className="relative rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        aria-label="Notifications"
      >
        <Bell className="h-4 w-4" />
        <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full bg-destructive" />
      </button>
      <button
        className="rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        aria-label="Settings"
      >
        <Settings className="h-4 w-4" />
      </button>
      <div className="h-6 w-px bg-border" />
      <div className="flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
          {doctor.avatarInitials}
        </div>
        <div className="hidden sm:flex flex-col">
          <span className="text-sm font-medium text-foreground leading-tight">{doctor.name}</span>
          <span className="text-xs text-muted-foreground leading-tight">{doctor.title}</span>
        </div>
      </div>
    </div>
  )
}
