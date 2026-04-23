"use client"

import type { ScanResult } from "@/lib/store"
import { ShieldCheck, ShieldAlert, CheckCircle2, AlertCircle } from "lucide-react"

export function InferenceMetrics({ scan }: { scan: ScanResult }) {
  // Determine reliability color based on score
  const getReliabilityColor = (score: number) => {
    if (score >= 0.7) return "text-green-600"
    if (score >= 0.5) return "text-amber-600"
    return "text-red-600"
  }

  const getReliabilityBgColor = (score: number) => {
    if (score >= 0.7) return "bg-green-50"
    if (score >= 0.5) return "bg-amber-50"
    return "bg-red-50"
  }

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

        <div className={`flex flex-col gap-1.5 rounded-lg border border-border p-3 ${getReliabilityBgColor(scan.reliabilityScore)}`}>
          <div className="flex items-center gap-2 text-muted-foreground">
            <ShieldAlert className={`h-3.5 w-3.5 ${getReliabilityColor(scan.reliabilityScore)}`} />
            <span className="text-xs">Reliability</span>
          </div>
          <span className={`text-xl font-semibold ${getReliabilityColor(scan.reliabilityScore)}`}>
            {(scan.reliabilityScore * 100).toFixed(0)}%
          </span>
          <div className="h-1.5 rounded-full bg-white/50 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                scan.reliabilityScore >= 0.7
                  ? "bg-green-500"
                  : scan.reliabilityScore >= 0.5
                  ? "bg-amber-500"
                  : "bg-red-500"
              }`}
              style={{ width: `${scan.reliabilityScore * 100}%` }}
            />
          </div>
        </div>

        <div className="flex flex-col gap-1.5 rounded-lg bg-card border border-border p-3">
          <div className="flex items-center gap-2 text-muted-foreground">
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span className="text-xs">Stability</span>
          </div>
          <span className="text-lg font-semibold text-foreground">
            {scan.stabilityMetrics.is_stable ? "✓ Stable" : "⚠ Unstable"}
          </span>
          <span className="text-xs text-muted-foreground">
            TTA IoU: {(scan.stabilityMetrics.tta_iou * 100).toFixed(1)}%
          </span>
        </div>

        <div className="flex flex-col gap-1.5 rounded-lg bg-card border border-border p-3">
          <div className="flex items-center gap-2 text-muted-foreground">
            <AlertCircle className="h-3.5 w-3.5" />
            <span className="text-xs">Objects</span>
          </div>
          <span className="text-xl font-semibold text-foreground">{scan.stabilityMetrics.objects_found}</span>
          <span className="text-xs text-muted-foreground">Contours detected</span>
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
