"use client"

import { useAppState } from "@/lib/store"
import { useState, useRef, useCallback, useEffect } from "react"
import { ZoomIn, ZoomOut, RotateCcw, Layers, Eye, EyeOff } from "lucide-react"
import { cn } from "@/lib/utils"

export function AnalysisViewer() {
  const { currentScan } = useAppState()
  const scan = currentScan

  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [zoom, setZoom] = useState(1)
  const [showOverlay, setShowOverlay] = useState(true)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })

  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const w = canvas.width
    const h = canvas.height

    ctx.clearRect(0, 0, w, h)
    ctx.save()
    ctx.translate(w / 2 + pan.x, h / 2 + pan.y)
    ctx.scale(zoom, zoom)
    ctx.translate(-w / 2, -h / 2)

    // Draw simulated OCT background
    const gradient = ctx.createLinearGradient(0, 0, 0, h)
    gradient.addColorStop(0, "#1a1a2e")
    gradient.addColorStop(0.3, "#16213e")
    gradient.addColorStop(0.5, "#0f3460")
    gradient.addColorStop(0.7, "#1a1a2e")
    gradient.addColorStop(1, "#0a0a15")
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, w, h)

    // Draw retinal layers
    for (let i = 0; i < 8; i++) {
      ctx.beginPath()
      ctx.strokeStyle = `rgba(100, 180, 220, ${0.15 + i * 0.05})`
      ctx.lineWidth = 1.5 + Math.random()
      const yBase = 60 + i * 35
      ctx.moveTo(0, yBase)
      for (let x = 0; x < w; x += 3) {
        const y = yBase + Math.sin(x * 0.015 + i) * 12 + Math.sin(x * 0.005) * 8
        ctx.lineTo(x, y)
      }
      ctx.stroke()
    }

    // Add noise texture
    for (let i = 0; i < 2000; i++) {
      const x = Math.random() * w
      const y = Math.random() * h
      const alpha = Math.random() * 0.08
      ctx.fillStyle = `rgba(180, 210, 240, ${alpha})`
      ctx.fillRect(x, y, 1, 1)
    }

    // Draw segmentation overlay
    if (showOverlay && scan) {
      scan.lesionTypes.forEach((lesion, idx) => {
        ctx.globalAlpha = 0.35
        const cx = 120 + idx * 130 + Math.sin(idx * 2) * 40
        const cy = 140 + Math.cos(idx * 3) * 30
        const rx = 40 + lesion.percentage * 1.2
        const ry = 25 + lesion.percentage * 0.8

        ctx.beginPath()
        ctx.ellipse(cx, cy, rx, ry, Math.PI * 0.1 * idx, 0, Math.PI * 2)
        ctx.fillStyle = lesion.color
        ctx.fill()

        // Dashed border
        ctx.globalAlpha = 0.7
        ctx.setLineDash([4, 3])
        ctx.strokeStyle = lesion.color
        ctx.lineWidth = 1.5
        ctx.stroke()
        ctx.setLineDash([])
      })
      ctx.globalAlpha = 1
    }

    ctx.restore()
  }, [zoom, pan, showOverlay, scan])

  useEffect(() => {
    drawCanvas()
  }, [drawCanvas])

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y })
  }

  const handleMouseUp = () => setIsDragging(false)

  const handleReset = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }

  if (!scan) return null

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-medium text-foreground">
            "Segmentation Result"
          </h3>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setShowOverlay(!showOverlay)}
            className={cn(
              "flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors",
              showOverlay
                ? "bg-primary/10 text-primary"
                : "bg-muted text-muted-foreground hover:text-foreground"
            )}
          >
            {showOverlay ? <Eye className="h-3.5 w-3.5" /> : <EyeOff className="h-3.5 w-3.5" />}
            Mask
          </button>
          <button
            onClick={() => setZoom((z) => Math.min(z + 0.25, 3))}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            aria-label="Zoom in"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(z - 0.25, 0.5))}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            aria-label="Zoom out"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <button
            onClick={handleReset}
            className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            aria-label="Reset view"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="relative overflow-hidden rounded-xl border border-border bg-card">
        <canvas
          ref={canvasRef}
          width={520}
          height={340}
          className="w-full cursor-grab active:cursor-grabbing"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        />
        <div className="absolute bottom-3 left-3 flex items-center gap-2 rounded-md bg-foreground/80 px-2.5 py-1 text-xs text-background">
          <span>{Math.round(zoom * 100)}%</span>
        </div>
      </div>

      {/* Lesion Legend */}
      <div className="flex flex-wrap gap-3">
        {scan.lesionTypes.map((lesion) => (
          <div key={lesion.name} className="flex items-center gap-2 rounded-md bg-card border border-border px-3 py-1.5">
            <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: lesion.color }} />
            <span className="text-xs font-medium text-foreground">{lesion.name}</span>
            <span className="text-xs text-muted-foreground">{lesion.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
