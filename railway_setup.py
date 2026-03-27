#!/usr/bin/env python3
"""
Railway Deployment Configuration
This script sets up the app for Railway with proper model handling
"""

import os
import sys

# Force models directory inclusion
MODEL_DIRS = ['models']
for dir_name in MODEL_DIRS:
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print(f"Created {dir_name} directory")

print("\n" + "="*70)
print("RAILWAY DEPLOYMENT SETUP")
print("="*70)
print(f"Python: {sys.version}")
print(f"Working Directory: {os.getcwd()}")

# Verify models directory
models_path = os.path.abspath('models')
print(f"\nModels directory: {models_path}")
print(f"Exists: {os.path.exists(models_path)}")

if os.path.exists(models_path):
    files = os.listdir(models_path)
    print(f"Files in models/: {len(files)}")
    for f in files:
        full_path = os.path.join(models_path, f)
        if os.path.isfile(full_path):
            size = os.path.getsize(full_path) / (1024*1024)
            print(f"  - {f} ({size:.2f} MB)")

print("\n" + "="*70)
print("IMPORTANT: Railway Deployment Checklist")
print("="*70)
print("""
1. **For this deployment to work**:
   - models/ folder with all .pkl files must be committed to git
   - git push to main branch
   - Railway will auto-pull and deploy

2. **If Flood Models Still Missing**:
   - Go to Railway Dashboard > Deployments
   - Click "Redeploy" not just "Restart"
   - Full redeploy pulls all git files

3. **CloudBurst Model (AlexNet_best.h5)**:
   - This will try to auto-download from Google Drive
   - If it fails, the app will show "Model unavailable" but continue working
   - Try uploading model file to git using git-lfs:
     git lfs install
     git lfs track "models/*.h5"
     git add models/AlexNet_best.h5
     git push
""")

print("Setup complete!")
print("="*70 + "\n")
