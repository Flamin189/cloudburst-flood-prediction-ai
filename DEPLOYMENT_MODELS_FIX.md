# Deployment Guide: Fixing Model Unavailable Issues

## Problem Summary
The Railway deployment shows "Model unavailable" for both CloudBurst and Flood prediction modules.

## Root Causes

### 1. **CloudBurst Model (AlexNet_best.h5)**
- **Issue**: Model is NOT in git repository (excluded by .gitignore)
- **Expected behavior**: Model should auto-download from Google Drive on first app startup
- **Why it's failing**:
  - Google Drive might be blocked in Railway's network
  - Google Drive link permissions issue
  - Network timeout during download

### 2. **Flood Model (.pkl files)**
- **Status**: ✓ Files ARE in git repository
- **Expected behavior**: Should deploy automatically with the app
- **Why it's failing**:
  - Possible causes:
    - models/ directory not deployed
    - File permissions issue
    - Corrupted pickle files (unlikely)

## Solutions by Priority

### Priority 1: Verify Railway Deployment (DO THIS FIRST)
1. **Check if models/ folder exists in Railway**:
   - Go to Railway dashboard
   - SSH into the deployment (if available)
   - Run: `ls -la models/`
   - Check if .pkl files are present

2. **Restart the Railway app**:
   - Go to Railway settings
   - Click "Restart" or redeploy from main branch
   - Check the build logs

3. **Run the model diagnostic**:
   - SSH into Railway instance
   - Run: `python check_models.py`
   - Check what's missing

### Priority 2: Fix CloudBurst Model Download
**Option A: Upload to Railway Storage (Recommended)**
```bash
# 1. Download AlexNet_best.h5 from Google Drive
# 2. Add to repository (but it's large, so use git-lfs if >100MB)
git lfs install
git lfs track "models/*.h5"
git add models/AlexNet_best.h5
git commit -m "Add AlexNet model"
git push

# 3. Update .gitignore to NOT exclude the model
# Remove or comment out this line:
# models/AlexNet_best.h5

# 4. Redeploy Railway
```

**Option B: Fix Google Drive Download (Current Setup)**
```bash
# 1. Ensure Google Drive file is publicly accessible:
#    - Right-click file in Drive
#    - Share settings: "Anyone with the link can view"
#    - Get shareable link ID from URL

# 2. Update the MODEL_URL in app.py if needed:
MODEL_URL = 'https://drive.google.com/uc?id=YOUR_FILE_ID_HERE'

# 3. Test locally:
python -c "from app import download_model; download_model()"

# 4. If it works locally but fails in Railway:
#    - Railway might have firewall restrictions
#    - Contact Railway support about Google Drive access
#    - Or use Option A instead
```

### Priority 3: Fix Flood Models Deployment
```bash
# These should already be deployed, but to force a redeploy:

# 1. Verify files are tracked in git:
git ls-files models/*.pkl

# 2. If any are NOT listed, add them:
git add models/*.pkl
git commit -m "Ensure flood models are tracked"
git push

# 3. Redeploy Railway

# 4. After deploy, check if it works:
# - Go to web app URL
# - Try Flood Prediction feature
```

## Automated Checks

### Local Testing
Run this before deploying to Railway:
```bash
python check_models.py
```

This will tell you exactly what's missing and how to fix it.

### During Railway Deploy
The app startup will now show detailed logs:
```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 
APPLICATION STARTUP: Loading ML Models
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 

============================================================
Loading Cloudburst Model
============================================================
Expected path: ...
File exists: [True/False]
...
```

Check the Railway build logs to see these messages.

## Railway Deployment Checklist

- [ ] **models/ folder exists** - `git ls-files models/`
- [ ] **flood .pkl files committed** - `git ls-files models/*.pkl`
- [ ] **AlexNet_best.h5 handling decided**:
  - [ ] Option A: Upload to git-lfs (if using large files)
  - [ ] Option B: Rely on Google Drive download (ensure Drive link is public)
- [ ] **Procfile is correct** - `web: python app.py`
- [ ] **requirements.txt has all packages** - tensorflow, gdown, pandas, etc.
- [ ] **Redeploy on Railway** after making changes
- [ ] **Test: upload a CSV** to flood prediction
- [ ] **Test: upload image** to cloudburst prediction

## If Models Still Unavailable After Deployment

### Step 1: Check build logs
- Go to Railway dashboard
- Click your service
- Go to "Deployments" tab
- Check the build/deploy logs for errors

### Step 2: Check runtime logs  
- Still in Railway dashboard
- Go to "Logs" tab
- Filter for MODEL loading errors (search for "Loading Cloudburst" or "Loading Flood")

### Step 3: SSH into Railway and test
```bash
# SSH into the deployment
cd /app
python check_models.py
ls -la models/
python -c "from flood_predictor import get_flood_predictor; get_flood_predictor()"
```

### Step 4: Contact Railway Support
If models are in the repo but still not deploying:
- Models might be getting cleaned up
- File size limits
- Permissions issues
- Ask Railway support to increase ephemeral storage if needed

## Environment Variables (if needed)
Add to Railway if models are remote:
```
MODEL_DOWNLOAD_TIMEOUT=300
GDOWN_QUIET=0  # Show download progress
```

## Prevention for Future
1. **Commit all model files** to git (or use git-lfs for large files)
2. **Test locally** before pushing to Railway
3. **Add to CI/CD** a step that runs `python check_models.py`
4. **Document in README** which models are auto-downloaded vs committed

---

**Last Updated**: March 27, 2026
