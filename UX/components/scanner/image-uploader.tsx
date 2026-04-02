"use client"

/**
 * components/scanner/image-uploader.tsx
 *
 * This component was IMPORTED but MISSING from the project.
 * It handles: file selection → validation → API call → state update.
 *
 * === THE FLOW ===
 *
 *  User drops/selects a file
 *       ↓
 *  Client-side validation (type, size)
 *       ↓
 *  setScannerMode("processing")  ← shows ProcessingOverlay
 *       ↓
 *  analyzeOCTImage(file)         ← real API call to FastAPI backend
 *       ↓
 *  setCurrentScan(result)        ← puts adapted result into global store
 *  setScannerMode("result")      ← switches to AnalysisViewer
 */

import { useCallback, useState } from "react"
import { useAppState } from "@/lib/store"
import { analyzeOCTImage } from "@/lib/api"
import { UploadCloud, ImageIcon, AlertCircle, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

const ACCEPTED_TYPES = ["image/png", "image/jpeg", "image/tiff", "image/tif"]
const MAX_SIZE_MB = 50

interface ImageUploaderProps {
  isPatientValid?: boolean
  patientValidationError?: string | null
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function ImageUploader({ 
  isPatientValid = false, 
  patientValidationError = null 
}: ImageUploaderProps) {
  const { setScannerMode, setCurrentScan, setUploadedFile } = useAppState()

  const [isDragOver, setIsDragOver] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  // ─── Validation ────────────────────────────────────────────────────────────
  function validateFile(file: File): string | null {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      return `Invalid file type. Accepted: PNG, JPEG, TIFF. Got: ${file.type || "unknown"}`
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File too large. Max: ${MAX_SIZE_MB}MB. Got: ${formatFileSize(file.size)}`
    }
    return null
  }

  // ─── File Selection Handler ─────────────────────────────────────────────────
  const handleFile = useCallback((file: File) => {
    setError(null)
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }

    setSelectedFile(file)
    setUploadedFile(file)

    // Generate a local preview URL so the user sees their image
    const url = URL.createObjectURL(file)
    setPreview(url)
  }, [setUploadedFile])

  // ─── Upload + API Call ──────────────────────────────────────────────────────
  const handleAnalyze = useCallback(async () => {
    if (!selectedFile) return
    setError(null)

    // Switch to the processing screen immediately (the fake progress bar)
    setScannerMode("processing")

    try {
      // THE REAL API CALL — this is where the frontend meets the backend
      const scanResult = await analyzeOCTImage(selectedFile)

      // Put the result into global state
      setCurrentScan(scanResult)

      // Switch view to the analysis results
      setScannerMode("result")

    } catch (err) {
      // If the API fails, go back to upload and show the error
      setScannerMode("upload")
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred. Is the backend running?"
      )
    }
  }, [selectedFile, setScannerMode, setCurrentScan])

  // ─── Drag & Drop Handlers ───────────────────────────────────────────────────
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }
  const handleDragLeave = () => setIsDragOver(false)
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  // ─── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col gap-4 w-full">

      {/* Drop Zone */}
      <label
        className={cn(
          "flex flex-col items-center justify-center gap-4",
          "rounded-xl border-2 border-dashed p-10 transition-all cursor-pointer",
          isDragOver
            ? "border-primary bg-primary/5 scale-[1.01]"
            : "border-border bg-card hover:border-primary/50 hover:bg-primary/[0.02]"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".png,.jpg,.jpeg,.tif,.tiff"
          className="sr-only"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleFile(file)
          }}
        />

        {preview ? (
          // Show image thumbnail once selected
          <div className="flex flex-col items-center gap-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={preview}
              alt="OCT scan preview"
              className="max-h-40 max-w-full rounded-lg object-contain border border-border"
            />
            <div className="text-center">
              <p className="text-sm font-medium text-foreground">{selectedFile?.name}</p>
              <p className="text-xs text-muted-foreground">
                {selectedFile ? formatFileSize(selectedFile.size) : ""}
              </p>
            </div>
            <p className="text-xs text-muted-foreground">Click to change image</p>
          </div>
        ) : (
          // Default empty state
          <div className="flex flex-col items-center gap-3 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
              <UploadCloud className="h-7 w-7 text-primary" />
            </div>
            <div>
              <p className="text-sm font-semibold text-foreground">
                Drop OCT image here
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                or click to browse files
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <ImageIcon className="h-3.5 w-3.5" />
              <span>PNG, JPEG, TIFF — max {MAX_SIZE_MB}MB</span>
            </div>
          </div>
        )}
      </label>

      {/* Error Message */}
      {error && (
        <div className="flex items-start gap-2.5 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2.5">
          <AlertCircle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {/* Patient Validation Warning */}
      {selectedFile && !isPatientValid && patientValidationError && (
        <div className="flex items-start gap-2.5 rounded-lg border border-amber-300/40 bg-amber-50 px-3 py-2.5">
          <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
          <p className="text-sm text-amber-700">{patientValidationError}</p>
        </div>
      )}

      {/* Analyze Button */}
      <button
        onClick={handleAnalyze}
        disabled={!selectedFile || !isPatientValid}
        title={
          !selectedFile
            ? "Select an image to continue"
            : !isPatientValid
              ? "Complete patient information to run analysis"
              : ""
        }
        className={cn(
          "w-full rounded-lg px-4 py-3 text-sm font-semibold transition-all",
          selectedFile && isPatientValid
            ? "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm"
            : "bg-muted text-muted-foreground cursor-not-allowed"
        )}
      >
        {!selectedFile
          ? "Select an image to continue"
          : !isPatientValid
            ? "Complete patient information"
            : "Run AI Analysis"}
      </button>

      {/* Hint */}
      {!selectedFile && (
        <p className="text-center text-xs text-muted-foreground">
          The backend runs in mock mode if no model is loaded —{" "}
          <span className="text-primary">safe to test without a real .onnx file</span>
        </p>
      )}
    </div>
  )
}
