"use client"

import { Loader2, Brain } from "lucide-react"
import { useEffect, useState } from "react"

export function ProcessingOverlay() {
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState("Initializing model...")

  useEffect(() => {
    const stages = [
      { at: 15, label: "Preprocessing OCT image..." },
      { at: 35, label: "Running Multi-task U-Net..." },
      { at: 60, label: "Generating segmentation masks..." },
      { at: 80, label: "Classifying lesion types..." },
      { at: 92, label: "Computing confidence scores..." },
    ]

    const interval = setInterval(() => {
      setProgress((prev) => {
        const next = prev + 1.2
        const currentStage = stages.findLast((s) => next >= s.at)
        if (currentStage) setStage(currentStage.label)
        return next >= 100 ? 100 : next
      })
    }, 30)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex flex-col items-center justify-center gap-6 py-16">
      <div className="relative flex h-20 w-20 items-center justify-center">
        <div className="absolute inset-0 animate-ping rounded-full bg-primary/20" />
        <div className="relative flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
          <Brain className="h-8 w-8 text-primary animate-pulse" />
        </div>
      </div>

      <div className="flex flex-col items-center gap-2 text-center">
        <h3 className="text-lg font-semibold text-foreground">AI Analysis in Progress</h3>
        <p className="text-sm text-muted-foreground">{stage}</p>
      </div>

      <div className="w-full max-w-xs">
        <div className="h-2 rounded-full bg-muted overflow-hidden">
          <div
            className="h-full rounded-full bg-primary transition-all duration-100 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="mt-2 text-center text-xs text-muted-foreground">
          {Math.round(progress)}%
        </p>
      </div>

      <div className="flex items-center gap-2 text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-xs">Multi-task U-Net</span>
      </div>
    </div>
  )
}
