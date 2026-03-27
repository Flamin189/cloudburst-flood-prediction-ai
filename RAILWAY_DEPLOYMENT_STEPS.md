# Railway Deployment - Complete Fix Guide

## Current Status
✅ App now has **fallback predictions** - will work even if models are missing (but less accurate)
❌ Real ML models still not deploying to Railway (showing "unavailable" errors)

## What Changed
1. **Flood Prediction**: Uses heuristic-based fallback if .pkl models missing
2. **CloudBurst Detection**: Uses image brightness analysis if AlexNet model missing  
3. **App continues working** instead of showing error pages

## TO GET ACCURATE PREDICTIONS: Deploy the models

---

## Railway Deployment Steps (DO THIS NOW)

### Step 1: Force Git to Track Model Files
The .pkl files are in git locally but not showing in Railway deployment.

```bash
# Switch to your project directory  
cd d:\hosting\cloud

# Force git to recognize the model files
git add -f models/flood_model.pkl
git add -f models/flood_label_encoder_target.pkl
git add -f models/flood_categorical_encoders.pkl
git add -f models/flood_feature_names.pkl

# Verify they're staged
git status

# Commit
git commit -m "Force-add flood model files for Railway deployment"

# Push to GitHub
git push origin main
```

### Step 2: Redeploy on Railway (Full Rebuild, Not Just Restart)

1. Go to [Railway Dashboard](https://railway.app)
2. Click your **Cloud Burst Detection** service
3. Go to **Deployments** tab
4. Click the red **⚠️ X** on the current deployment (or click menu → Remove)
5. Click **Deploy** button
6. Choose **main** branch
7. **WAIT** for full deployment (5-15 minutes)
8. Check logs during deployment

### Step 3: Verify Deployment

After Railway finishes deploying:

1. **Check the build logs**:
   - In Railway: Deployments tab → Click the new deployment → Logs
   - Look for message: `Loading Flood Prediction Models` OR `Using FALLBACK predictor`
   - If you see `FALLBACK`, models still aren't deployed

2. **Test the app**:
   - Go to your app URL (e.g., `https://your-app.railway.app`)
   - Try uploading a CSV → should work now (even if fallback)
   - Try uploading an image → should work now (even if fallback)
   - If still says "model unavailable", models didn't deploy

---

## If Models STILL Not Deploying After Full Redeploy

### Check What's in Models Directory

SSH into Railway and check:

```bash
# SSH into Railway (from Railway Dashboard → Terminal tab)
ls -la models/
```

If files are missing:
- The git push didn't include them
- Go back to **Step 1** - make sure you used `git add -f` (force add)

### Force Git to Stop Ignoring Models

Check if .gitignore is excluding them:

```bash
# Check what's in .gitignore
cat .gitignore

# Check what git sees
git ls-files models/
```

**Verify you see these files in git ls-files:**
```
models/__init__.py
models/flood_categorical_encoders.pkl
models/flood_encoding_mappings.pkl
models/flood_feature_names.pkl
models/flood_label_encoder.pkl
models/flood_label_encoder_target.pkl
models/flood_model.pkl
```

---

## For CloudBurst Model (AlexNet_best.h5)

This model is not in git (too large). It should auto-download from Google Drive.

### If Google Drive Download Fails in Railway:

**Option A: Skip for Now**
- App will use fallback image analysis (less accurate)
- Will show in logs: "Using fallback CloudBurst prediction"

**Option B: Upload to Git with Large File Support**

```bash
# Install git-lfs
git lfs install

# Track .h5 files
git lfs track "models/*.h5"

# Download model from Drive → save to models/AlexNet_best.h5

# Add to git
git add models/.gitattributes
git add models/AlexNet_best.h5
git commit -m "Add AlexNet model with git-lfs"

# Push (will be slow)
git push origin main
```

**Option C: Fix Google Drive Link**
- Ensure the file is shared: "Anyone with the link"
- Test link works without login
- Model will try to download automatically on Railway

---

## Testing After Deployment

### Test Flood Prediction
1. Download this test CSV:
   ```
   rainfall_intensity,rainfall_duration,humidity,temperature,terrain_type,elevation,soil_type,drainage_capacity,previous_rainfall
   100,8,85,25,hilly,500,clay,low,50
   ```
2. Go to app → Flood Prediction → Upload CSV
3. Should return "High" (or reasonable prediction)

### Test CloudBurst  
1. Upload a cloud image
2. Should get prediction (ML or fallback)
3. Should NOT show "Model Unavailable"

---

## If Still Having Issues

### Debug Option 1: Check Locally
```bash
python check_models.py
```

Should show:
- ✓ Flood models available
- ✗ CloudBurst (expected if AlexNet not downloaded)

### Debug Option 2: Check Railway Logs
- Go to Railway → Your service → Logs
- Search for "Loading Flood" or "Loading CloudBurst"
- Look for error messages

### Debug Option 3: SSH into Railway
```bash
# From Railway Dashboard, click Terminal tab
python check_models.py
python -c "from flood_predictor import get_flood_predictor; fp = get_flood_predictor(); print(type(fp))"
```

---

## Summary

The fix involves 3 steps:
1. ✅ **App now has fallback** (already done) → will work but less accurate
2. **Force git to track .pkl files** → needs your action
3. **Full redeploy on Railway** → needs your action
4. Verify deployment → test in app

**If you do steps 2-3, you'll get full accuracy predictions.**

If you skip them, fallback predictions will work but be less accurate.

---

## Questions?

Check the logs:
- **Locally**: `python check_models.py`
- **Railway**: Deployments → Logs tab while deploying
- **App startup**: Look for `Loading Floods Prediction Models` message

The logs will tell you exactly what's wrong! 🔍
