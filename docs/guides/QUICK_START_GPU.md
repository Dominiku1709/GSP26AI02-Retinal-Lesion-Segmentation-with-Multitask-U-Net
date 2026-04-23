# ✅ GPU Fix - Step-by-Step Checklist

## Problem (Fixed ✓)
```
RuntimeError: CUDA wasn't able to be loaded because it cannot find 
the CUDA 12.8/cuDNN DLLs
```

---

## ⚡ Quick Start (3 Steps)

### Step 1: Run Quick Fix Script
```bash
cd backend_2.0
python quick_fix_gpu.py
```
**What this does:**
- ✓ Updates CUDA_PATH to correct version
- ✓ Installs PyTorch with GPU support
- ✓ Installs ONNX Runtime GPU 1.18.0
- ✓ Creates `.env` configuration

**⏱️ Takes ~5-10 minutes (depends on download speed)**

### Step 2: Restart Terminal
- ✅ Close all terminals/PowerShell windows
- ✅ Open new terminal window
- ✅ This loads the updated environment variables

### Step 3: Verify Setup
```bash
cd backend_2.0
python gpu_diagnostic.py
```

**Look for:**
```
✓ Available Providers:
  - CUDAExecutionProvider  ← THIS IS THE KEY LINE!
  - CPUExecutionProvider
```

If you see `CUDAExecutionProvider`, **you're done!** ✅

---

## 📋 Full Process Checklist

- [ ] **Step 1: Run quick fix**
  ```bash
  cd backend_2.0
  python quick_fix_gpu.py
  ```
  Wait for it to complete

- [ ] **Step 2: Restart terminal**
  Close and reopen terminal

- [ ] **Step 3: Run diagnostic**
  ```bash
  python gpu_diagnostic.py
  ```
  Verify CUDAExecutionProvider is listed

- [ ] **Step 4: Create .env file** (if not created by quick_fix)
  ```bash
  cp .env.example .env
  ```

- [ ] **Step 5: Test server startup**
  ```bash
  uvicorn app.main:app --reload
  ```
  Look for: `[Inference] Model loaded with provider: ['CUDAExecutionProvider'`

- [ ] **Step 6: Test GPU endpoint**
  In another terminal:
  ```bash
  curl http://localhost:8000/api/system/gpu-status
  ```
  Should show: `"cuda_available": true`

- [ ] **Step 7: Validate setup** (optional, comprehensive test)
  ```bash
  cd ..
  python validate_gpu_setup.py
  ```

---

## ✅ Success Indicators

### When GPU is working:
- ✅ `gpu_diagnostic.py` shows `CUDAExecutionProvider`
- ✅ Server logs show `Model loaded with provider: ['CUDAExecutionProvider']`
- ✅ API endpoint returns `"cuda_available": true`
- ✅ GPU usage visible in Task Manager (Performance tab)
- ✅ Inference runs faster than CPU-only

### When GPU is NOT working (fallback to CPU):
- ⚠️ Only CPU provider in diagnostic output
- ⚠️ Server logs show `Model loaded with provider: ['CPUExecutionProvider']`
- ⚠️ API shows `"cuda_available": false`
- ⚠️ No GPU usage in Task Manager
- ⚠️ Inference slower but still works

---

## 🆘 Troubleshooting

### Issue: Script fails with "permission denied"
**Fix:** Run PowerShell as Administrator
```powershell
# Right-click PowerShell > Run as Administrator
cd backend_2.0
python quick_fix_gpu.py
```

### Issue: Still no CUDA after quick_fix
**Reason:** Missing cuDNN DLLs  
**Fix:**
1. Download cuDNN 9.x: https://developer.nvidia.com/cudnn-download-archive
2. Extract ZIP file
3. Copy `cudnn64_9.dll` to: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\`
4. Run quick_fix script again
5. Restart terminal

### Issue: "Module not found" error
**Fix:** Make sure you're in the correct directory
```bash
cd backend_2.0  # Must be in this folder!
python gpu_diagnostic.py
```

### Issue: Server starts but GPU not used
**Fix:** Check logs for errors
```bash
uvicorn app.main:app --reload 2>&1 | tee server.log
```
Look for `[Inference]` messages

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `quick_fix_gpu.py` | Automated fix (run this first!) |
| `gpu_diagnostic.py` | Check GPU status anytime |
| `CUDA_SETUP_GUIDE.md` | Detailed manual setup |
| `GPU_QUICK_FIX.md` | Quick reference |
| `.env.example` | Configuration template |
| `validate_gpu_setup.py` | Comprehensive validation test |

---

## 🔄 Typical Workflow

```
1. Run: python quick_fix_gpu.py
         ↓
2. Restart terminal
         ↓
3. Run: python gpu_diagnostic.py
         ↓
4. Check for CUDAExecutionProvider
         ↓
5. Start server: uvicorn app.main:app --reload
         ↓
6. Success! GPU-accelerated inference ready
```

---

## ⏱️ Expected Times

| Step | Time |
|------|------|
| Run quick_fix_gpu.py | 5-10 min |
| Restart terminal | < 1 min |
| Run gpu_diagnostic.py | < 30 sec |
| Test server startup | < 2 min |
| **Total** | **~15 minutes** |

---

## 📞 Need Help?

### Error Messages:
- Search the error in `CUDA_SETUP_GUIDE.md` under "Troubleshooting"

### Detailed Status:
- Run `python gpu_diagnostic.py` and check output

### API Issues:
- Ensure server is running: `uvicorn app.main:app --reload`
- Check endpoint: `curl http://localhost:8000/api/system/gpu-status`

### Still Stuck:
- Save diagnostic output: `python gpu_diagnostic.py > diagnostic.txt`
- Share the diagnostic.txt file with your team

---

## 🎯 Quick Commands Reference

```bash
# Navigate to backend
cd backend_2.0

# Run fix
python quick_fix_gpu.py

# Check status
python gpu_diagnostic.py

# Start server
uvicorn app.main:app --reload

# Test API
curl http://localhost:8000/api/system/gpu-status

# Validate everything
cd ..
python validate_gpu_setup.py

# Check PyTorch CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Check ONNX Runtime providers
python -c "import onnxruntime; print(onnxruntime.get_available_providers())"
```

---

## ✨ Final Notes

- ✅ All changes are **non-breaking** - if GPU fails, API uses CPU automatically
- ✅ No application code changes needed - works as-is
- ✅ Fallback mechanism ensures reliability
- ✅ Full diagnostic tools for troubleshooting
- ✅ GPU status endpoint for monitoring

**You're all set! Run `python quick_fix_gpu.py` to get started** 🚀

---

Last Updated: April 9, 2026
