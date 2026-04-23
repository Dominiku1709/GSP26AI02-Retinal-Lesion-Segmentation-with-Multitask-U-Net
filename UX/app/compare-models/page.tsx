"use client"

import { useState, useCallback } from "react"
import { AppProvider, type ScanResult } from "@/lib/store"
import { DoctorHeader } from "@/components/doctor-header"
import { analyzeAllModels } from "@/lib/api"
import { ArrowLeft, Upload, Play, Loader } from "lucide-react"
import { useRouter } from "next/navigation"

function CompareModelsContent() {
  const router = useRouter()
  
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string>("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState<ScanResult[]>([])
  const [error, setError] = useState("")

  const handleFileSelect = useCallback((file: File) => {
    setUploadedFile(file)
    setError("")
    
    const reader = new FileReader()
    reader.onload = (e) => {
      setPreview(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }, [])

  const handleRunAll = useCallback(async () => {
    if (!uploadedFile) {
      setError("Please select an image first")
      return
    }

    setIsAnalyzing(true)
    setError("")
    
    try {
      const allResults = await analyzeAllModels(uploadedFile)
      setResults(allResults)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze image")
      setResults([])
    } finally {
      setIsAnalyzing(false)
    }
  }, [uploadedFile])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <DoctorHeader />
      
      {/* Back Button */}
      <div className="flex items-center justify-between border-b border-border bg-card px-5 py-2.5">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-slate-700 hover:text-slate-900 font-medium transition"
        >
          <ArrowLeft className="w-5 h-5" />
          Back
        </button>
      </div>

      <main className="max-w-full mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upload Panel */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">
                Upload Image
              </h2>

              {/* File Upload Area */}
              <div
                className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition"
                onClick={() => document.getElementById("file-input")?.click()}
              >
                <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm text-slate-600">
                  Click to select image
                </p>
              </div>

              <input
                id="file-input"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleFileSelect(file)
                }}
              />

              {/* Preview */}
              {preview && (
                <div className="mt-4">
                  <p className="text-xs font-medium text-slate-600 mb-2">
                    Preview
                  </p>
                  <img
                    src={preview}
                    alt="Preview"
                    className="w-full h-48 object-cover rounded-lg border"
                  />
                  <p className="text-xs text-slate-500 mt-2 truncate">
                    {uploadedFile?.name}
                  </p>
                </div>
              )}

              {/* Run All Button */}
              <button
                onClick={handleRunAll}
                disabled={!uploadedFile || isAnalyzing}
                className="w-full mt-6 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-semibold py-3 px-4 rounded-lg transition flex items-center justify-center gap-2"
              >
                {isAnalyzing ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Analyzing All Models...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Run All Models
                  </>
                )}
              </button>

              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Results Grid */}
          <div className="lg:col-span-2">
            {results.length > 0 ? (
              <div>
                <h2 className="text-lg font-semibold text-slate-900 mb-4">
                  Model Comparison Results
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {results.map((result) => (
                    <ModelResultCard
                      key={result.id}
                      result={result}
                    />
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <p className="text-slate-500">
                  {isAnalyzing
                    ? "Analyzing image with all models..."
                    : "Upload and click 'Run All Models' to see results"}
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default function CompareModelsPage() {
  return (
    <AppProvider>
      <CompareModelsContent />
    </AppProvider>
  )
}

/* ─── Model Result Card ────────────────────────────────────────────── */

interface ModelResultCardProps {
  result: ScanResult
}

function ModelResultCard({ result }: ModelResultCardProps) {
  const lesion = result.lesionTypes[0]
  
  // Map architecture names to friendly display names
  const getModelDisplayName = (archName?: string): string => {
    const nameMap: Record<string, string> = {
      "deeplabv3plus": "DeepLabV3+",
      "resnet_unet": "ResNet + UNet",
      "unetplusplus": "UNet++",
      "effb3_unet": "EfficientNet-B3",
      "effb3": "EfficientNet-B3",
      "vanilla": "Vanilla UNet",
      "vanilla_plus": "Vanilla UNet+",
    }
    return nameMap[archName || ""] || archName || "Unknown Model"
  }
  
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition">
      {/* Card Header with Model Name & Result */}
      <div className="bg-gradient-to-r from-blue-50 to-slate-50 p-4 border-b">
        <h3 className="font-semibold text-slate-900 text-sm mb-2">
          {getModelDisplayName(result.architecture)}
        </h3>
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded-full"
            style={{ backgroundColor: lesion?.color || "#64748b" }}
          />
          <span className="text-sm font-medium text-slate-700">
            {lesion?.name || "Unknown"}
          </span>
        </div>
      </div>

      {/* Card Content */}
      <div className="p-4 space-y-3">
        {/* Confidence Score */}
        <div>
          <p className="text-xs text-slate-600 font-medium mb-1">
            Confidence
          </p>
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-slate-200 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-600 h-full transition-all"
                style={{ width: `${result.confidence}%` }}
              />
            </div>
            <span className="text-sm font-semibold text-slate-700 min-w-12">
              {result.confidence.toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Reliability Score */}
        <div>
          <p className="text-xs text-slate-600 font-medium mb-1">
            Reliability
          </p>
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-slate-200 rounded-full h-2 overflow-hidden">
              <div
                className="bg-green-600 h-full transition-all"
                style={{ width: `${(result.reliabilityScore || 0) * 100}%` }}
              />
            </div>
            <span className="text-sm font-semibold text-slate-700 min-w-12">
              {((result.reliabilityScore || 0) * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Mask Visualization */}
        {result.maskOverlay && (
          <div className="mt-4">
            <p className="text-xs text-slate-600 font-medium mb-2">
              Segmentation
            </p>
            <img
              src={result.maskOverlay}
              alt="Mask"
              className="w-full h-32 object-cover rounded border"
            />
          </div>
        )}
      </div>
    </div>
  )
}
