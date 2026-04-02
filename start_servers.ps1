# start_servers.ps1 - Start both backend and frontend development servers
# Usage: .\start_servers.ps1

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🚀 Starting OCT Analysis System (Backend + Frontend)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend (FastAPI)
Write-Host "[1/2] Starting Backend (FastAPI on port 8000)..." -ForegroundColor Blue
Push-Location backend_2.0
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -PassThru -NoNewWindow
Write-Host "✓ Backend running (PID: $($backendProcess.Id))" -ForegroundColor Green
Pop-Location
Start-Sleep -Seconds 3

# Start Frontend (Next.js)
Write-Host ""
Write-Host "[2/2] Starting Frontend (Next.js on port 3000)..." -ForegroundColor Blue
Push-Location UX
$frontendProcess = Start-Process -FilePath "pnpm" -ArgumentList "dev" -PassThru -NoNewWindow
Write-Host "✓ Frontend running (PID: $($frontendProcess.Id))" -ForegroundColor Green
Pop-Location

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "✅ Both servers started successfully!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "📍 Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  Keep this PowerShell window open to maintain the servers running." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop all servers." -ForegroundColor Yellow
Write-Host ""

# Wait for processes to complete
$backendProcess.WaitForExit()
$frontendProcess.WaitForExit()

Write-Host "✓ All servers stopped." -ForegroundColor Green
