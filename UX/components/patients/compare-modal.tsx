// component/patients/compare-modal.tsx
"use client"

import { useAppState, type ScanResult } from "@/lib/store"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useRef, useCallback, useEffect } from "react"
import { cn } from "@/lib/utils"

function MiniOctCanvas({ scan, label }: { scan: ScanResult; label: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return
    const w = canvas.width
    const h = canvas.height

    ctx.clearRect(0, 0, w, h)

    const gradient = ctx.createLinearGradient(0, 0, 0, h)
    gradient.addColorStop(0, "#1a1a2e")
    gradient.addColorStop(0.3, "#16213e")
    gradient.addColorStop(0.5, "#0f3460")
    gradient.addColorStop(0.7, "#1a1a2e")
    gradient.addColorStop(1, "#0a0a15")
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, w, h)

    for (let i = 0; i < 8; i++) {
      ctx.beginPath()
      ctx.strokeStyle = `rgba(100, 180, 220, ${0.15 + i * 0.05})`
      ctx.lineWidth = 1.5
      const yBase = 40 + i * 25
      ctx.moveTo(0, yBase)
      for (let x = 0; x < w; x += 3) {
        const y = yBase + Math.sin(x * 0.015 + i) * 10 + Math.sin(x * 0.005) * 6
        ctx.lineTo(x, y)
      }
      ctx.stroke()
    }

    for (let i = 0; i < 1000; i++) {
      const x = Math.random() * w
      const y = Math.random() * h
      ctx.fillStyle = `rgba(180, 210, 240, ${Math.random() * 0.06})`
      ctx.fillRect(x, y, 1, 1)
    }

    scan.lesionTypes.forEach((lesion, idx) => {
      ctx.globalAlpha = 0.35
      const cx = 80 + idx * 90 + Math.sin(idx * 2) * 30
      const cy = 100 + Math.cos(idx * 3) * 20
      const rx = 30 + lesion.percentage * 0.8
      const ry = 18 + lesion.percentage * 0.5

      ctx.beginPath()
      ctx.ellipse(cx, cy, rx, ry, Math.PI * 0.1 * idx, 0, Math.PI * 2)
      ctx.fillStyle = lesion.color
      ctx.fill()
      ctx.globalAlpha = 0.6
      ctx.setLineDash([3, 2])
      ctx.strokeStyle = lesion.color
      ctx.lineWidth = 1
      ctx.stroke()
      ctx.setLineDash([])
    })
    ctx.globalAlpha = 1
  }, [scan])

  useEffect(() => {
    draw()
  }, [draw])

  return (
    <div className="flex flex-col gap-2">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <div className="overflow-hidden rounded-lg border border-border">
        <canvas ref={canvasRef} width={380} height={240} className="w-full" />
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">{scan.date}</span>
        <span className={cn(
          "font-medium",
          scan.confidence >= 95 ? "text-emerald-600" : "text-amber-600"
        )}>
          {scan.confidence}% confidence
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {scan.lesionTypes.map((l) => (
          <span key={l.name} className="flex items-center gap-1.5 rounded-md bg-card border border-border px-2 py-1 text-xs">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: l.color }} />
            {l.name}: {l.percentage}%
          </span>
        ))}
      </div>
    </div>
  )
}

export function CompareModal() {
  const { compareScans, compareModalOpen, setCompareModalOpen, setCompareScans } = useAppState()

  return (
    <Dialog
      open={compareModalOpen}
      onOpenChange={(open) => {
        setCompareModalOpen(open)
        if (!open) setCompareScans([])
      }}
    >
      <DialogContent className="sm:max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Scan Comparison - Disease Progression</DialogTitle>
        </DialogHeader>

        {compareScans.length === 2 && (
          <div className="flex flex-col gap-6 py-2">
            <div className="grid grid-cols-2 gap-6">
              <MiniOctCanvas scan={compareScans[0]} label="Earlier Scan" />
              <MiniOctCanvas scan={compareScans[1]} label="Later Scan" />
            </div>

            {/* Delta Summary */}
            <div className="rounded-lg bg-card border border-border p-4">
              <h4 className="text-sm font-medium text-foreground mb-3">Change Summary</h4>
              <div className="flex flex-col gap-2">
                {(() => {
                  const allLesionNames = Array.from(
                    new Set([
                      ...compareScans[0].lesionTypes.map((l) => l.name),
                      ...compareScans[1].lesionTypes.map((l) => l.name),
                    ])
                  )
                  return allLesionNames.map((name) => {
                    const earlier = compareScans[0].lesionTypes.find((l) => l.name === name)
                    const later = compareScans[1].lesionTypes.find((l) => l.name === name)
                    const prev = earlier?.percentage ?? 0
                    const curr = later?.percentage ?? 0
                    const delta = curr - prev
                    const color = earlier?.color ?? later?.color ?? "#888"

                    return (
                      <div key={name} className="flex items-center gap-3">
                        <span className="h-3 w-3 rounded-sm shrink-0" style={{ backgroundColor: color }} />
                        <span className="flex-1 text-sm text-foreground">{name}</span>
                        <span className="text-sm text-muted-foreground w-16 text-right">{prev.toFixed(1)}%</span>
                        <span className="text-muted-foreground">{"-->"}</span>
                        <span className="text-sm text-muted-foreground w-16 text-right">{curr.toFixed(1)}%</span>
                        <span className={cn(
                          "text-sm font-medium w-20 text-right",
                          delta > 0 ? "text-red-600" : delta < 0 ? "text-emerald-600" : "text-muted-foreground"
                        )}>
                          {delta > 0 ? "+" : ""}{delta.toFixed(1)}%
                        </span>
                      </div>
                    )
                  })
                })()}
              </div>
              <div className="mt-3 flex items-center justify-between border-t border-border pt-3 text-xs text-muted-foreground">
                <span>Confidence: {compareScans[0].confidence}% vs {compareScans[1].confidence}%</span>
                <span>
                  {Math.abs(
                    Math.round(
                      (new Date(compareScans[1].date).getTime() - new Date(compareScans[0].date).getTime()) /
                        (1000 * 60 * 60 * 24)
                    )
                  )}{" "}
                  days apart
                </span>
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
