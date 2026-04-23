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
  const [maskImage, setMaskImage] = useState<HTMLImageElement | null>(null)
  const [maskLoadError, setMaskLoadError] = useState(false)

  // Load mask image when scan changes
  useEffect(() => {
    setMaskLoadError(false)
    
    if (scan?.maskOverlay) {
      const img = new Image()
      
      img.onload = () => {
        setMaskImage(img)
        setMaskLoadError(false)
      }
      
      img.onerror = () => {
        console.error("Failed to load mask image from:", scan.maskOverlay)
        setMaskImage(null)
        setMaskLoadError(true)
      }
      
      img.src = scan.maskOverlay
    } else {
      setMaskImage(null)
      setMaskLoadError(false)
    }
  }, [scan?.maskOverlay])

  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const w = canvas.width
    const h = canvas.height

    // 1. Luôn xóa sạch canvas trước khi vẽ
    ctx.clearRect(0, 0, w, h)
    
    ctx.save()
    // Thiết lập Zoom và Pan
    ctx.translate(w / 2 + pan.x, h / 2 + pan.y)
    ctx.scale(zoom, zoom)
    ctx.translate(-w / 2, -h / 2)

    // 2. CHỈ VẼ DỮ LIỆU THẬT TỪ MASK IMAGE
    if (maskImage) {
      const maskAspect = maskImage.width / maskImage.height
      const canvasAspect = w / h
      
      let drawW, drawH, drawX, drawY
      if (maskAspect > canvasAspect) {
        drawW = w
        drawH = w / maskAspect
        drawX = 0
        drawY = (h - drawH) / 2
      } else {
        drawH = h
        drawW = h * maskAspect
        drawX = (w - drawW) / 2
        drawY = 0
      }

      // Kiểm tra chẩn đoán để quyết định độ mờ
      const isNormal = scan?.lesionTypes.some(l => l.name === "Normal");
      
      if (showOverlay) {
        // Nếu bật Mask, tùy vào loại bệnh mà có thể để nguyên hoặc chỉnh alpha
        // Vì Backend của bạn thường trả về ảnh OCT có đè sẵn mask màu, nên để alpha = 1
        ctx.globalAlpha = 1.0 
        ctx.drawImage(maskImage, drawX, drawY, drawW, drawH)
      } else {
        // Nếu người dùng tắt Mask (nếu backend hỗ trợ ảnh gốc riêng thì vẽ ảnh gốc ở đây)
        // Hiện tại tạm thời vẽ maskImage nhưng có thể giảm alpha hoặc giữ nguyên
        ctx.globalAlpha = 1.0
        ctx.drawImage(maskImage, drawX, drawY, drawW, drawH)
      }
    } else {
        // Nếu chưa có ảnh, vẽ một nền đen trống
        ctx.fillStyle = "#000000"
        ctx.fillRect(0, 0, w, h)
    }

    ctx.restore()
  }, [zoom, pan, showOverlay, scan, maskImage])

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
