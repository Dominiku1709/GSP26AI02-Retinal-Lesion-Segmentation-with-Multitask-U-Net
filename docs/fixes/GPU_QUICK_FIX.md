# 🔧 ONNX Runtime GPU Fix Guide

## ⚠️ Your Current Issue

Based on diagnostic analysis:
- ✗ ONNX Runtime GPU NOT using CUDA (only CPU available)
- ✗ PyTorch installed as CPU version (needs GPU)
- ✗ cuDNN missing for CUDA 12.8
- ✓ CUDA 12.8 IS installed but not properly configured

---

## 🚀 Quick Fix (Automated)

Run this script to automatically fix most issues:

```bash
cd backend_2.0
python quick_fix_gpu.py
```

This script will:
1. ✓ Fix CUDA_PATH environment variable
2. ✓ Reinstall PyTorch with GPU support
3. ✓ Reinstall ONNX Runtime GPU 1.18.0
4. ✓ Create `.env` configuration file
5. ✓ Verify CUDA is available

After running:
- **Restart your terminal/PowerShell completely**
- Run `python gpu_diagnostic.py` to verify
- Run `uvicorn app.main:app --reload` to start server

---

## 📊 Manual Diagnostic

```bash
cd backend_2.0
python gpu_diagnostic.py
```

Shows detailed CUDA/GPU configuration status.

---

## 📋 What Needs to be Fixed

### 1. **cuDNN Missing** ❌
   - CUDA 12.8 has CUDA files but no cuDNN
   - **Fix**: Download and install cuDNN 9.x

### 2. **CUDA_PATH Wrong** ❌
   - Set to `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0`
   - Should be: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8`
   - **Fix**: `quick_fix_gpu.py` updates this

### 3. **PyTorch CPU Version** ❌
   - Installed: `torch==2.9.1+cpu`
   - Needs: `torch==2.4.1` with CUDA 12.x
   - **Fix**: `quick_fix_gpu.py` reinstalls with GPU support

### 4. **ONNX Runtime Version Mismatch** ❌
   - Installed: `onnxruntime==1.24.4` (no GPU support detected)
   - Required: `onnxruntime-gpu==1.18.0`
   - **Fix**: `quick_fix_gpu.py` installs correct version

---

## 🔗 Manual Setup (Step-by-Step)

If you prefer manual setup, see [CUDA_SETUP_GUIDE.md](./CUDA_SETUP_GUIDE.md)

---

## ✅ How to Verify Success

After running `quick_fix_gpu.py`:

1. **Check diagnostic:**
   ```bash
   python gpu_diagnostic.py
   ```
   Should show:
   ```
   ✓ Available Providers:
     - CUDAExecutionProvider  ← Key indicator!
     - CPUExecutionProvider
   ```

2. **Check via API:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Then in another terminal:
   ```bash
   curl http://localhost:8000/api/system/gpu-status
   ```
   Should show `"cuda_available": true`

3. **Check PyTorch:**
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```
   Should print: `True`

---

## 📝 Environment Variables (.env)

After running `quick_fix_gpu.py`, your `.env` should have:

```properties
ENABLE_GPU=true
FALLBACK_TO_CPU=true
CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8
```

---

## 🆘 Still Having Issues?

1. **Run diagnostic and save output:**
   ```bash
   python gpu_diagnostic.py > gpu_status.txt
   ```

2. **Share the output file** with your team

3. **Check server logs:**
   ```bash
   uvicorn app.main:app --reload 2>&1 | tee server.log
   ```

4. **Common Issues:**
   - **"CUDA DLL not found"** → Restart terminal after env changes
   - **"Provider not available"** → Run quick_fix_gpu.py again
   - **"Model loading fails with GPU"** → Falls back to CPU automatically

---

## 📚 Additional Resources

- [Full Setup Guide](./CUDA_SETUP_GUIDE.md)
- [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-12-8-0-download-archive)
- [NVIDIA cuDNN Downloads](https://developer.nvidia.com/cudnn-download-archive)
- [ONNX Runtime Docs](https://onnxruntime.ai/docs/)

---

## 🎯 Quick Commands

```bash
# Run quick fix (do this first!)
python quick_fix_gpu.py

# Verify everything works
python gpu_diagnostic.py

# Start server
cd backend_2.0
uvicorn app.main:app --reload

# Check GPU status via API
curl http://localhost:8000/api/system/gpu-status

# Run test inference
python test_api.py
```
