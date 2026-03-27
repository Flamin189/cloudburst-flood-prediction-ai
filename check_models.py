#!/usr/bin/env python3
"""
Model Diagnostic Tool
Checks if all required ML models are available and can be loaded
Run this script to diagnose "model unavailable" issues
"""

import os
import sys
import pickle
from pathlib import Path

def check_cloudburst_model():
    """Check cloudburst model availability"""
    print("\n" + "="*70)
    print("CLOUDBURST MODEL CHECK")
    print("="*70)
    
    MODEL_PATH = 'models/AlexNet_best.h5'
    MODEL_URL = 'https://drive.google.com/uc?id=1khdF5Xn9nTkVqmQti_44RdT-XcRTkgxr'
    
    print(f"Expected location: {MODEL_PATH}")
    print(f"Absolute path: {os.path.abspath(MODEL_PATH)}")
    
    if os.path.exists(MODEL_PATH):
        file_size = os.path.getsize(MODEL_PATH) / (1024*1024)
        print(f"✓ FILE EXISTS")
        print(f"  Size: {file_size:.2f} MB")
        
        try:
            from tensorflow.keras.models import load_model
            model = load_model(MODEL_PATH)
            print(f"✓ MODEL LOADS SUCCESSFULLY")
            print(f"  Type: {type(model)}")
            return True
        except Exception as e:
            print(f"✗ MODEL FAILED TO LOAD")
            print(f"  Error: {e}")
            return False
    else:
        print(f"✗ FILE NOT FOUND")
        print(f"\nTo fix:")
        print(f"  1. Option A: Download model from Google Drive")
        print(f"     URL: {MODEL_URL}")
        print(f"     Save to: {MODEL_PATH}")
        print(f"\n  2. Option B: In Railway, model will auto-download on first run")
        print(f"     Ensure Google Drive link is 'Anyone with link' accessible")
        print(f"\n  3. Option C: If in Railway, check deployment logs:")
        print(f"     - Google Drive might be blocked")
        print(f"     - Network might be restricted")
        return False

def check_flood_models():
    """Check flood predictor models availability"""
    print("\n" + "="*70)
    print("FLOOD PREDICTION MODELS CHECK")
    print("="*70)
    
    model_files = {
        'RandomForest Model': 'models/flood_model.pkl',
        'Target Encoder': 'models/flood_label_encoder_target.pkl',
        'Categorical Encoder': 'models/flood_categorical_encoders.pkl',
        'Feature Names': 'models/flood_feature_names.pkl'
    }
    
    all_exist = True
    all_load = True
    
    for name, path in model_files.items():
        print(f"\n{name}:")
        print(f"  Path: {path}")
        
        if os.path.exists(path):
            try:
                file_size = os.path.getsize(path) / (1024)
                print(f"  ✓ File exists ({file_size:.2f} KB)")
                
                with open(path, 'rb') as f:
                    obj = pickle.load(f)
                print(f"  ✓ Loads as pickle (type: {type(obj).__name__})")
                
            except (pickle.PickleError, EOFError) as e:
                print(f"  ✗ PICKLE ERROR: {e}")
                all_load = False
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                all_load = False
        else:
            print(f"  ✗ FILE NOT FOUND")
            all_exist = False
    
    if all_exist and all_load:
        print(f"\n✓ ALL FLOOD MODELS AVAILABLE AND LOADABLE")
        return True
    else:
        print(f"\n✗ FLOOD MODELS MISSING OR CORRUPTED")
        if not all_exist:
            print(f"\nTo fix missing files:")
            print(f"  1. Ensure models/ directory exists in repository root")
            print(f"  2. Commit all .pkl files to git:")
            print(f"     - flood_model.pkl")
            print(f"     - flood_label_encoder_target.pkl")
            print(f"     - flood_categorical_encoders.pkl")
            print(f"     - flood_feature_names.pkl")
            print(f"  3. Push to main branch")
            print(f"  4. Redeploy on Railway")
        if not all_load:
            print(f"\nTo fix corrupted files:")
            print(f"  1. Regenerate models by running train_flood_production.py")
            print(f"  2. Commit new .pkl files")
            print(f"  3. Redeploy")
        return False

def check_repository_structure():
    """Check overall repository structure"""
    print("\n" + "="*70)
    print("REPOSITORY STRUCTURE CHECK")
    print("="*70)
    
    required_dirs = ['models', 'static', 'templates', 'Backend']
    
    for dir_name in required_dirs:
        exists = os.path.isdir(dir_name)
        status = "✓" if exists else "✗"
        print(f"{status} {dir_name}/")
    
    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Python path:")
    for p in sys.path[:3]:
        print(f"  - {p}")

def main():
    print("\n" + "#"*70)
    print("# ML MODEL DIAGNOSTIC TOOL")
    print("#"*70)
    
    print(f"\nPython version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    check_repository_structure()
    
    cloudburst_ok = check_cloudburst_model()
    flood_ok = check_flood_models()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Cloudburst model: {'✓ OK' if cloudburst_ok else '✗ ISSUE'}")
    print(f"Flood models:     {'✓ OK' if flood_ok else '✗ ISSUE'}")
    
    if cloudburst_ok and flood_ok:
        print("\n✓ All models ready! Application should work normally.")
        sys.exit(0)
    else:
        print("\n✗ Some models are missing or have issues.")
        print("\nDeployment checklist for Railway:")
        print("  1. Ensure models/ folder is in git repository")
        print("  2. Verify all .pkl and AlexNet_best.h5 files are committed")
        print("  3. Check .gitignore doesn't exclude model files")
        print("  4. For AlexNet_best.h5:")
        print("     - Either upload to repo OR")
        print("     - Let it auto-download from Google Drive on first deploy")
        print("  5. Restart Railway deployment after fixing")
        sys.exit(1)

if __name__ == '__main__':
    main()
