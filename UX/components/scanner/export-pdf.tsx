"use client"

import { useAppState, type ScanResult, type Patient } from "@/lib/store"
import { FileText, Download } from "lucide-react"

export function ExportPdfButton() {
  const { currentScan, patients, selectedPatientId, doctor } = useAppState()

  const selectedPatient = patients.find((p) => p.id === selectedPatientId)

  const handleExport = () => {
    if (!currentScan) return
    generatePdfReport(currentScan, selectedPatient ?? null, doctor.name)
  }

  return (
    <button
      onClick={handleExport}
      disabled={!currentScan}
      className="flex items-center justify-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-sm font-medium text-foreground hover:bg-muted disabled:opacity-50 transition-colors"
    >
      <FileText className="h-4 w-4" />
      Export PDF Report
    </button>
  )
}

function generatePdfReport(
  scan: ScanResult,
  patient: Patient | null,
  doctorName: string
) {
  const w = window.open("", "_blank")
  if (!w) return

  const lesionRows = scan.lesionTypes
    .map(
      (l) =>
        `<tr>
          <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;">
            <span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${l.color};margin-right:8px;vertical-align:middle;"></span>
            ${l.name}
          </td>
          <td style="padding:8px 12px;border-bottom:1px solid #e2e8f0;text-align:right;">${l.percentage}%</td>
        </tr>`
    )
    .join("")

  const validationLabel =
    scan.validationStatus === "approved"
      ? "Approved"
      : scan.validationStatus === "edited"
        ? "Edited by Doctor"
        : "Pending Review"

  const html = `<!DOCTYPE html>
<html>
<head>
  <title>OCT Analysis Report - ${patient?.name ?? "Unassigned"}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', -apple-system, sans-serif; color: #1e293b; padding: 40px; max-width: 800px; margin: 0 auto; }
    .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #0d7377; padding-bottom: 16px; margin-bottom: 24px; }
    .logo { font-size: 22px; font-weight: 700; color: #0d7377; }
    .logo span { font-weight: 400; color: #64748b; font-size: 14px; display: block; }
    .meta { text-align: right; font-size: 12px; color: #64748b; }
    h2 { font-size: 16px; font-weight: 600; margin-bottom: 12px; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }
    .field { font-size: 13px; }
    .field .label { color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
    .field .value { font-weight: 500; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 24px; }
    th { text-align: left; padding: 8px 12px; background: #f1f5f9; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; }
    th:last-child { text-align: right; }
    .status { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 500; }
    .status.approved { background: #d1fae5; color: #065f46; }
    .status.edited { background: #dbeafe; color: #1e40af; }
    .status.pending { background: #fef3c7; color: #92400e; }
    .conclusion { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 24px; }
    .footer { border-top: 1px solid #e2e8f0; padding-top: 12px; font-size: 11px; color: #94a3b8; display: flex; justify-content: space-between; }
    @media print { body { padding: 20px; } }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">RetinaAI<span>OCT Retinal Analysis Report</span></div>
    <div class="meta">
      <div>Report ID: ${scan.id}</div>
      <div>Date: ${scan.date}</div>
      <div>Generated: ${new Date().toLocaleString()}</div>
    </div>
  </div>

  <h2>Patient Information</h2>
  <div class="grid">
    <div class="field"><div class="label">Name</div><div class="value">${patient?.name ?? "Not assigned"}</div></div>
    <div class="field"><div class="label">Patient ID</div><div class="value">${patient?.id ?? "N/A"}</div></div>
    <div class="field"><div class="label">Age / Gender</div><div class="value">${patient ? `${patient.age} / ${patient.gender}` : "N/A"}</div></div>
    <div class="field"><div class="label">Date of Birth</div><div class="value">${patient?.dob ?? "N/A"}</div></div>
  </div>

  <h2>AI Analysis Results</h2>
  <div class="grid" style="margin-bottom:16px;">
    <div class="field"><div class="label">Model Confidence</div><div class="value">${scan.confidence}%</div></div>
    <div class="field"><div class="label">Processing Time</div><div class="value">${scan.processingTime}s</div></div>
    <div class="field"><div class="label">Model</div><div class="value">Multi-task U-Net v2.4</div></div>
    <div class="field"><div class="label">Total Lesion Area</div><div class="value">${scan.lesionTypes.reduce((a, l) => a + l.percentage, 0).toFixed(1)}%</div></div>
  </div>

  <table>
    <thead><tr><th>Lesion Type</th><th>Coverage</th></tr></thead>
    <tbody>${lesionRows}</tbody>
  </table>

  <h2>Clinical Validation</h2>
  <div class="conclusion">
    <div style="margin-bottom:8px;">
      <span class="status ${scan.validationStatus}">${validationLabel}</span>
    </div>
    <div class="field" style="margin-bottom:6px;"><div class="label">Doctor's Diagnostic Label</div><div class="value">${scan.doctorLabel || "Pending doctor review"}</div></div>
    ${scan.notes ? `<div class="field"><div class="label">Clinical Notes</div><div class="value">${scan.notes}</div></div>` : ""}
  </div>

  <div class="footer">
    <span>Reviewed by: ${doctorName}</span>
    <span>RetinaAI - For clinical use only</span>
  </div>

  <script>window.onload = () => window.print();</script>
</body>
</html>`

  w.document.write(html)
  w.document.close()
}
