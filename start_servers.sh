#!/bin/bash

# start_servers.sh - Start both backend and frontend development servers
# Usage: ./start_servers.sh

set -e

echo "🚀 Starting OCT Analysis System (Backend + Frontend)..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Start Backend (FastAPI)
echo -e "${BLUE}[1/2]${NC} Starting Backend (FastAPI)..."
cd backend_2.0
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend running on port 8000 (PID: $BACKEND_PID)${NC}"
sleep 2

# Start Frontend (Next.js)
echo ""
echo -e "${BLUE}[2/2]${NC} Starting Frontend (Next.js)..."
cd ../UX
pnpm dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend running on port 3000 (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}✅ Both servers started successfully!${NC}"
echo ""
echo "📍 Backend:  http://localhost:8000"
echo "📍 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers..."
echo ""

# Wait for all background processes
wait $BACKEND_PID $FRONTEND_PID

# Cleanup on exit
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' EXIT
