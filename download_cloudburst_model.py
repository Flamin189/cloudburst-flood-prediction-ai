#!/usr/bin/env python3
"""Download CloudBurst model from Google Drive"""

import os
import sys
import gdown

print("\n" + "="*70)
print("DOWNLOADING CLOUDBURST MODEL FROM GOOGLE DRIVE")
print("="*70)

# File ID from the user's link
FILE_ID = "1khdF5Xn9nTkVqmQti_44RdT-XcRTkgxr"
MODEL_URL = f"https://drive.google.com/uc?id={FILE_ID}"
MODEL_PATH = "models/AlexNet_best.h5"

print(f"\nFile ID: {FILE_ID}")
print(f"URL: {MODEL_URL}")
print(f"Save location: {MODEL_PATH}")

# Create directory if needed
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

print(f"\nStarting download...")
print("(this may take 5-15 minutes depending on your internet)")

try:
    # Download the file
    output = gdown.download(
        MODEL_URL,
        MODEL_PATH,
        quiet=False,
        use_cookies=False
    )
    
    if os.path.exists(MODEL_PATH):
        file_size = os.path.getsize(MODEL_PATH) / (1024*1024)
        print(f"\n✓✓✓ SUCCESS! ✓✓✓")
        print(f"\nModel saved to: {MODEL_PATH}")
        print(f"File size: {file_size:.2f} MB")
        
        # Verify it's a valid H5 file
        try:
            from tensorflow.keras.models import load_model
            print(f"\nValidating H5 file...")
            model = load_model(MODEL_PATH)
            print(f"✓ Model is valid and can be loaded")
            print(f"  Model type: {type(model)}")
            print(f"  Input shape: {model.input_shape}")
            print(f"  Output shape: {model.output_shape}")
        except Exception as e:
            print(f"⚠️ Warning: Could not validate model: {e}")
            print(f"But file was downloaded. Try loading in app.")
    else:
        print(f"\n✗ File not found after download")
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ Download failed: {e}")
    print(f"Error type: {type(e).__name__}")
    print(f"\nTroubleshooting:")
    print(f"  1. Check your internet connection")
    print(f"  2. Verify Google Drive file is shared ('Anyone with link')")
    print(f"  3. Try manual download:")
    print(f"     - Go to: {MODEL_URL}")
    print(f"     - Click Download")
    print(f"     - Save to: {MODEL_PATH}")
    print(f"\n  4. Or try using a terminal with direct Google Drive access:")
    print(f"     pip install gdown")
    print(f"     gdown {MODEL_URL} -O {MODEL_PATH}")
    sys.exit(1)

print(f"\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("1. Run: python test_startup.py")
print("2. Run: python app.py")
print("3. Visit: http://localhost:5000")
