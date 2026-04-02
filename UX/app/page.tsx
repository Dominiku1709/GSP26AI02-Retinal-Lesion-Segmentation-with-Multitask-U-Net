"use client"

import { AppProvider, useAppState } from "@/lib/store"
import { AppSidebar } from "@/components/app-sidebar"
import { ScannerDashboard } from "@/components/scanner/scanner-dashboard"
import { PatientsDashboard } from "@/components/patients/patients-dashboard"
function AppContent() {
  const { currentPage } = useAppState()

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <AppSidebar />
      <div className="flex-1 overflow-hidden">
        {currentPage === "scanner" && <ScannerDashboard />}
        {currentPage === "patients" && <PatientsDashboard />}
      </div>
    </div>
  )
}

export default function Home() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  )
}
