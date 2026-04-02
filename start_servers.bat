@echo off
REM start_servers.bat - Start both backend and frontend development servers
REM Usage: start_servers.bat

setlocal enabledelayedexpansion

echo.
echo ====================================================
echo 🚀 Starting OCT Analysis System (Backend + Frontend)
echo ====================================================
echo.

REM Start Backend (FastAPI)
echo [1/2] Starting Backend (FastAPI on port 8000)...
cd backend_2.0
start "Backend - FastAPI" cmd /k python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd ..
timeout /t 3 /nobreak

REM Start Frontend (Next.js)
echo.
echo [2/2] Starting Frontend (Next.js on port 3000)...
cd UX
start "Frontend - Next.js" cmd /k pnpm dev
cd ..

echo.
echo ====================================================
echo ✅ Both servers started successfully!
echo ====================================================
echo.
echo 📍 Backend:  http://localhost:8000
echo 📍 Frontend: http://localhost:3000
echo.
echo You can close this window. The servers will continue running.
echo.
