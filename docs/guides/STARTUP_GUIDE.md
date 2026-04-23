# 🚀 Starting the OCT Analysis System

This guide explains how to use the startup scripts to run both the backend and frontend servers simultaneously.

## 📋 Prerequisites

Before running the scripts, ensure you have:

- **Python 3.10+** installed and available in PATH
  ```bash
  python --version
  ```

- **Node.js & pnpm** installed
  ```bash
  pnpm --version
  ```

- **Project dependencies installed**
  ```bash
  # Backend
  cd backend_2.0
  pip install -r requirements.txt
  
  # Frontend
  cd ../UX
  pnpm install
  ```

- **Port availability**: Ensure ports `8000` (backend) and `3000` (frontend) are not in use

---

## 🖥️ Choose Your Script by Operating System

### **Windows Users (Recommended for Windows)**

#### Option 1: Batch Script (Easiest - No Configuration)
```bash
start_servers.bat
```
- ✅ Simplest approach
- ✅ Opens servers in separate command windows
- ✅ Easy to stop (just close the windows)
- ⚠️ Requires cmd.exe

**Steps:**
1. Navigate to the project root directory
2. Double-click `start_servers.bat` OR run from PowerShell/CMD:
   ```bash
   .\start_servers.bat
   ```
3. Two new command windows will open
4. Wait for both servers to start (1-2 seconds each)
5. Open your browser to `http://localhost:3000`

#### Option 2: PowerShell Script (Most Control)
```bash
.\start_servers.ps1
```
- ✅ More control over processes
- ✅ Better error messaging
- ✅ Runs in current window (you can see logs)
- ⚠️ May require PowerShell execution policy adjustment

**Steps:**
1. Open PowerShell as Administrator
2. Allow execution of scripts (first time only):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Navigate to project root:
   ```powershell
   cd "d:\KEEP\FPTUni\DH_FPT\FPTU\Syllabuses\Sem9\capstone\code\capstone_code\Multitask_test"
   ```
4. Run the script:
   ```powershell
   .\start_servers.ps1
   ```
5. Keep the PowerShell window open
6. Open your browser to `http://localhost:3000`

---

### **Linux / macOS / WSL Users**

#### Bash Script
```bash
bash start_servers.sh
```

**Steps:**
1. First, make the script executable (one-time setup):
   ```bash
   chmod +x start_servers.sh
   ```

2. Navigate to project root:
   ```bash
   cd /path/to/Multitask_test
   ```

3. Run the script:
   ```bash
   bash start_servers.sh
   # OR
   ./start_servers.sh
   ```

4. Press `Ctrl+C` to stop both servers

---

## 📍 What Gets Started

Once scripts run successfully, you'll see:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | React/Next.js UI for scanning & patient management |
| **Backend API** | http://localhost:8000 | FastAPI server with OCT analysis |
| **API Docs** | http://localhost:8000/docs | Swagger UI for testing endpoints |
| **Health Check** | http://localhost:8000/api/health | Backend status verification |

---

## ✅ Verify Servers Are Running

### Check Backend
```bash
curl http://localhost:8000/api/health
```
Expected response:
```json
{
  "status": "healthy",
  "app_name": "OCT Analysis Backend",
  "version": "2.0.0",
  "database": "connected",
  "model_available": false
}
```

### Check Frontend
```bash
curl http://localhost:3000
```
Should return HTML (React app)

---

## 🛑 Stopping Servers

### **Windows - Batch Script**
Close the two command windows that opened (one for backend, one for frontend)

### **Windows - PowerShell Script**
Press `Ctrl+C` in the PowerShell window

### **Linux / macOS / WSL**
Press `Ctrl+C` in your terminal

---

## 🔧 Troubleshooting

### ❌ "Port 8000 is already in use"

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000

# Linux/macOS
lsof -i :8000
```
Then kill the process and try again.

---

### ❌ "pnpm: command not found"

**Solution:** Install pnpm globally
```bash
npm install -g pnpm
```

---

### ❌ "Python: command not found"

**Solution:** Ensure Python is in your PATH
```bash
python --version
```
If not found, add Python installation directory to PATH.

---

### ❌ PowerShell: "cannot be loaded because running scripts is disabled"

**Solution:** Allow script execution
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### ❌ Backend won't start - "ModuleNotFoundError"

**Solution:** Install dependencies
```bash
cd backend_2.0
pip install -r requirements.txt
cd ..
```

---

### ❌ Frontend won't start - "ENOENT: no such file or directory"

**Solution:** Install dependencies
```bash
cd UX
pnpm install
cd ..
```

---

## 📊 Script Comparison

| Feature | Batch | PowerShell | Bash |
|---------|-------|------------|------|
| Platform | Windows | Windows | Linux/macOS/WSL |
| Ease of Use | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Separate Windows | Yes | No | No |
| Log Visibility | Limited | Full | Full |
| Stop Method | Close window | Ctrl+C | Ctrl+C |

---

## 🎯 Next Steps After Starting

1. **Open Frontend**: Go to http://localhost:3000
2. **Create a Patient**: Use the patient creation modal
3. **Upload OCT Image**: Use the scanner dashboard
4. **View Results**: See segmentation and analysis
5. **Check API**: Visit http://localhost:8000/docs for full API docs

---

## 📝 Log Files

Logs are displayed in the console/command window where the servers are running. Look for:

- `INFO: Application startup complete` (backend ready)
- `ready - started server on 0.0.0.0:3000` (frontend ready)

---

## ❓ Still Having Issues?

Check the following:

1. ✅ Verify Python version: `python --version` (should be 3.10+)
2. ✅ Verify pnpm installed: `pnpm --version`
3. ✅ Verify ports are free: `8000` and `3000`
4. ✅ Re-run dependency installation for both backend and frontend
5. ✅ Check for typos in project paths (especially Windows backslashes)

---

**Happy coding! 🎉**
