# GPU/CUDA Setup Guide for ONNX Runtime on Windows

## Problem
ONNX Runtime GPU (onnxruntime-gpu 1.18.0) fails with:
```
RuntimeError: CUDA wasn't able to be loaded because it cannot find the CUDA 12.8/cuDNN DLLs
```

## Solution Overview

The issue occurs because ONNX Runtime GPU requires CUDA and cuDNN DLL files to be available in your system PATH. Follow these steps to fix it:

---

## Step 1: Verify Current Setup

Run the diagnostic script to identify what's missing:

```bash
cd backend_2.0
python gpu_diagnostic.py
```

This will show:
- Available ONNX Runtime providers
- PyTorch CUDA status
- CUDA installation paths
- Missing DLL files

---

## Step 2: Install NVIDIA CUDA 12.8

### Option A: Fresh Installation

1. Download CUDA 12.8 from:
   https://developer.nvidia.com/cuda-12-8-0-download-archive

2. Select:
   - Operating System: **Windows**
   - Architecture: **x86_64** (64-bit)
   - Version: **12.8**

3. Run the installer (`cuda_12.8.0_windows_network.exe`)

4. Choose **Custom Install** and select:
   - ✓ CUDA
   - ✓ cuDNN (if available in CUDA installer)
   - Leave other options as default

5. Default installation path: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8`

### Option B: If You Have Different CUDA Version

If you have CUDA 11.8 or 12.1 installed, you have two choices:

**Choice 1**: Install CUDA 12.8 alongside (recommended)
- They can coexist in different directories

**Choice 2**: Downgrade onnxruntime-gpu
```bash
pip uninstall onnxruntime-gpu
pip install onnxruntime-gpu==1.15.0  # Compatible with CUDA 11.8
```

---

## Step 3: Install cuDNN 9.x

cuDNN must be installed separately if not bundled with CUDA:

1. Download cuDNN from:
   https://developer.nvidia.com/cudnn-download-archive
   
   Select version **9.x** compatible with CUDA 12.8

2. Extract the ZIP file to a folder (e.g., `C:\cudnn`)

3. Copy DLL files from `cudnn/bin/` to:
   ```
   C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\
   ```

   Files to copy:
   - `cudnn64_9.dll`
   - `cudnn_ops64_9.dll`
   - `cudnn_cnn64_9.dll`

---

## Step 4: Configure Environment Variables

### Windows 10/11:

1. **Open Environment Variables**:
   - Press `Win + X` → Click "System"
   - Click "Advanced system settings" on the left
   - Click "Environment Variables" button

2. **Add/Update User Variables**:
   - Click "New" (or edit if exists)
   - Variable name: `CUDA_PATH`
   - Variable value: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8`

3. **Update PATH Variable**:
   - Find `Path` in User variables (or System variables)
   - Click "Edit"
   - Click "New" and add: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin`
   - Click OK and OK again

4. **Verify PATH Update**:
   ```bash
   echo %PATH%
   ```
   Should include CUDA bin directory

5. **Restart Terminal/IDE** for changes to take effect

---

## Step 5: Update ONNX Runtime-GPU

Ensure you have the correct version installed:

```bash
# Uninstall current version
pip uninstall onnxruntime-gpu -y

# Install the version compatible with CUDA 12.8
pip install onnxruntime-gpu==1.18.0
```

Or to be safe, use a known working version:
```bash
pip install onnxruntime-gpu==1.17.3
```

---

## Step 6: Configure .env File

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:
```properties
# Enable GPU acceleration
ENABLE_GPU=true

# Enable fallback to CPU if GPU fails
FALLBACK_TO_CPU=true
```

---

## Step 7: Test GPU Setup

### Option A: Run Diagnostic Script
```bash
cd backend_2.0
python gpu_diagnostic.py
```

Expected output should show:
```
✓ ONNX Runtime installed: 1.18.0
✓ Available Providers:
  - CUDAExecutionProvider
  - CPUExecutionProvider
✓ CUDA Available: True
  CUDA Version: 12.8
```

### Option B: Test API

Start the server:
```bash
cd backend_2.0
uvicorn app.main:app --reload
```

Check GPU status:
```bash
curl http://localhost:8000/api/system/gpu-status
```

You should see:
```json
{
  "gpu_config": {
    "gpu_enabled": true,
    "cuda_available": true,
    "active_providers": ["CUDAExecutionProvider", "CPUExecutionProvider"],
    "fallback_to_cpu": true
  },
  "cuda_info": {
    "cuda_available": true,
    "cuda_version": "12.8",
    "cudnn_version": 90002
  },
  "model_loaded": true,
  "current_model": "deeplabv3plus.onnx"
}
```

---

## Troubleshooting

### Symptom 1: "CUDA wasn't able to be loaded"
```
Solution:
1. Verify CUDA_PATH environment variable is set:
   echo %CUDA_PATH%
   
2. Check files exist:
   dir %CUDA_PATH%\bin\cuda*.dll
   
3. Restart terminal and retry
```

### Symptom 2: GPU status shows `cuda_available: false`
```
Solution:
1. Check PyTorch can see CUDA:
   python -c "import torch; print(torch.cuda.is_available())"
   
2. If False, reinstall PyTorch:
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### Symptom 3: API returns CPU provider even with GPU enabled
```
Solution:
1. CUDA install was successful but not available
2. Try alternative: Set ENABLE_GPU=false and use CPU
3. Or reinstall CUDA with clean installation
```

### Symptom 4: "cuDNN library not found"
```
Solution:
1. Verify cuDNN DLLs are in CUDA bin folder:
   dir "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cudnn*.dll"
   
2. If missing, download and extract cuDNN again
3. Copy all DLL files to CUDA bin folder
```

---

## Fallback Option: Use CPU-Only

If you cannot get GPU working, use CPU inference (slower but works):

Edit `.env`:
```properties
ENABLE_GPU=false
FALLBACK_TO_CPU=true
```

Downgrade ONNX Runtime:
```bash
pip uninstall onnxruntime-gpu -y
pip install onnxruntime==1.18.0
```

---

## Alternative: Docker Setup (Recommended for Production)

Instead of manual setup, use Docker with NVIDIA runtime:

```dockerfile
FROM nvidia/cuda:12.8.0-runtime-windows-ltsc2022

WORKDIR /app

# Copy requirements and install
COPY backend_2.0/requirements.txt .
RUN pip install -r requirements.txt

# Copy app
COPY backend_2.0 .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t oct-app:gpu -f Dockerfile.gpu .
docker run --gpus all -p 8000:8000 oct-app:gpu
```

---

## References

- CUDA Downloads: https://developer.nvidia.com/cuda-downloads
- CUDA Archive (older versions): https://developer.nvidia.com/cuda-toolkit-archive
- cuDNN Downloads: https://developer.nvidia.com/cudnn-download-archive
- ONNX Runtime GitHub: https://github.com/microsoft/onnxruntime
- PyTorch CUDA: https://pytorch.org/get-started/locally/

---

## Quick Checklist

- [ ] CUDA 12.8 installed at `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8`
- [ ] cuDNN DLLs copied to CUDA bin folder
- [ ] `CUDA_PATH` environment variable set
- [ ] `Path` includes CUDA bin directory
- [ ] Terminal restarted after environment changes
- [ ] `pip install onnxruntime-gpu==1.18.0` installed
- [ ] `gpu_diagnostic.py` shows CUDA available
- [ ] API `/api/system/gpu-status` returns `cuda_available: true`
- [ ] Model loads with `CUDAExecutionProvider`

---

## Getting Help

If issues persist:

1. Run diagnostic and save output:
   ```bash
   python gpu_diagnostic.py > gpu_diagnostic_output.txt
   ```

2. Check inference logs:
   ```bash
   # Start server and check console output
   cd backend_2.0
   uvicorn app.main:app --reload 2>&1 | tee server.log
   ```

3. Share logs and output from steps 1-2 with support team
