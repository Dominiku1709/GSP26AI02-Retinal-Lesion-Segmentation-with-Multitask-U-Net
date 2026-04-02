"use client"

import type { ScanResult } from "@/lib/store"
import { Activity, Clock, ShieldCheck, Target } from "lucide-react"

export function InferenceMetrics({ scan }: { scan: ScanResult }) {
  return (
    <div className="flex flex-col gap-3">
      <h3 className="text-sm font-medium text-foreground">AI Inference Metrics</h3>

      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-1.5 rounded-lg bg-card border border-border p-3">
          <div className="flex items-center gap-2 text-muted-foreground">
            <ShieldCheck className="h-3.5 w-3.5" />
            <span className="text-xs">Confidence</span>
          </div>
          <span className="text-xl font-semibold text-foreground">{scan.confidence}%</span>
          <div className="h-1.5 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${scan.confidence}%` }}
            />
          </div>
        </div>

        <div className="flex flex-col gap-1.5 rounded-lg bg-card border border-border p-3">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            <span className="text-xs">Processing</span>
          </div>
          <span className="text-xl font-semibold text-foreground">{scan.processingTime}s</span>
          <span className="text-xs text-muted-foreground">Multi-task U-Net</span>
        </div>

        <div className="flex flex-col gap-1.5 rounded-lg bg-card border border-border p-3">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Target className="h-3.5 w-3.5" />
            <span className="text-xs">Lesions Found</span>
          </div>
          <span className="text-xl font-semibold text-foreground">{scan.lesionTypes.length}</span>
          <span className="text-xs text-muted-foreground">Distinct types</span>
        </div>

        <div className="flex flex-col gap-1.5 rounded-lg bg-card border border-border p-3">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Activity className="h-3.5 w-3.5" />
            <span className="text-xs">Coverage</span>
          </div>
          <span className="text-xl font-semibold text-foreground">
            {scan.lesionTypes.reduce((acc, l) => acc + l.percentage, 0).toFixed(1)}%
          </span>
          <span className="text-xs text-muted-foreground">Total area</span>
        </div>
      </div>

      {/* Lesion breakdown */}
      <div className="flex flex-col gap-2 rounded-lg bg-card border border-border p-3">
        <span className="text-xs font-medium text-muted-foreground">Lesion Breakdown</span>
        {scan.lesionTypes.map((lesion) => (
          <div key={lesion.name} className="flex items-center gap-3">
            <div className="h-3 w-3 rounded-sm" style={{ backgroundColor: lesion.color }} />
            <span className="flex-1 text-sm text-foreground">{lesion.name}</span>
            <span className="text-sm font-medium text-foreground">{lesion.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
