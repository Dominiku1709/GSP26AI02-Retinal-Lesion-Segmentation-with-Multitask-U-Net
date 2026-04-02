"use client"

import { useAppState } from "@/lib/store"
import { cn } from "@/lib/utils"
import {
  ScanLine,
  Users,
  Eye,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"
import { useState } from "react"

export function AppSidebar() {
  const { currentPage, setCurrentPage, setScannerMode, setCurrentScan, setUploadedFile } = useAppState()
  const [collapsed, setCollapsed] = useState(false)

  const handleNavigate = (page: "scanner" | "patients") => {
    if (page === "scanner") {
      setScannerMode("upload")
      setCurrentScan(null)
      setUploadedFile(null)
    }
    setCurrentPage(page)
  }

  return (
    <aside
      className={cn(
        "flex h-screen flex-col bg-sidebar text-sidebar-foreground border-r border-sidebar-border transition-all duration-300",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <div className="flex items-center gap-3 px-4 py-5 border-b border-sidebar-border">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
          <Eye className="h-5 w-5" />
        </div>
        {!collapsed && (
          <div className="flex flex-col">
            <span className="text-sm font-semibold tracking-tight">RetinaAI</span>
            <span className="text-xs text-sidebar-foreground/60">OCT Analysis</span>
          </div>
        )}
      </div>

      <nav className="flex flex-1 flex-col gap-1 px-2 py-4">
        <button
          onClick={() => handleNavigate("scanner")}
          className={cn(
            "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
            currentPage === "scanner"
              ? "bg-sidebar-accent text-sidebar-primary"
              : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
          )}
        >
          <ScanLine className="h-4.5 w-4.5 shrink-0" />
          {!collapsed && <span>AI Scanner</span>}
        </button>
        <button
          onClick={() => handleNavigate("patients")}
          className={cn(
            "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
            currentPage === "patients"
              ? "bg-sidebar-accent text-sidebar-primary"
              : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
          )}
        >
          <Users className="h-4.5 w-4.5 shrink-0" />
          {!collapsed && <span>Patients</span>}
        </button>
      </nav>

      <div className="border-t border-sidebar-border p-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex w-full items-center justify-center rounded-lg p-2 text-sidebar-foreground/50 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground transition-colors"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>
    </aside>
  )
}
