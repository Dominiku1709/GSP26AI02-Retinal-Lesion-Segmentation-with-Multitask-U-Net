"use client"

import { useAppState } from "@/lib/store"

export function DoctorHeader() {
  const { doctor } = useAppState()

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2.5">
        
        <div className="hidden sm:flex flex-col">
          
          
        </div>
      </div>
    </div>
  )
}
