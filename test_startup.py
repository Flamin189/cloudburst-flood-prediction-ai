#!/usr/bin/env python3
"""Test app startup and model loading"""

import sys
import os

print("\n" + "="*70)
print("TESTING APP STARTUP")
print("="*70)

# Check models first
print("\n1. Checking models...")
from check_models import check_flood_models, check_cloudburst_model
print("\nFlood models:")
flood_ok = check_flood_models()
print("\nCloudBurst model:")
cloudburst_ok = check_cloudburst_model()

# Try importing app
print("\n2. Importing Flask app...")
try:
    from app import app, model
    print(f"✓ App imported successfully")
    print(f"  Flask app: {app.name}")
    print(f"  CloudBurst model: {type(model).__name__ if model else 'None (will use fallback)'}")
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    sys.exit(1)

# Try importing flood predictor
print("\n3. Testing Flood Predictor...")
try:
    from flood_predictor import get_flood_predictor
    fp = get_flood_predictor()
    print(f"✓ Flood predictor initialized")
    print(f"  Type: {type(fp).__name__}")
    if hasattr(fp, 'model') and fp.model is not None:
        print(f"  Model: ✓ Loaded ({type(fp.model).__name__})")
    else:
        print(f"  Model: Using fallback heuristic")
except Exception as e:
    print(f"✗ Failed to initialize flood predictor: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("APP READY TO RUN")
print("="*70)
print("\nTo start the app:")
print("  python app.py")
print("\nThe app will:")
print(f"  - Use {'ML models' if flood_ok else 'FALLBACK'} for Flood prediction")
print(f"  - Use {'ML model' if cloudburst_ok else 'FALLBACK'} for CloudBurst detection")
