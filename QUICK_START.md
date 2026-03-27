# Quick Start Guide for Flash Flood Forecasting System

## ⚡ 5-Minute Setup

### 1. Install Requirements
```bash
pip install flask tensorflow scikit-learn pandas numpy werkzeug gdown
```

**Note:** The cloudburst detection model (~500MB) will be downloaded automatically from Google Drive on first use.

### 2. Train the Model (First Time Only)
```bash
python train_flood_model.py
```

If the model training hasn't been done yet, the script will:
- Create a sample dataset automatically
- Train RandomForestClassifier on 1000 samples
- Save model to `models/flood_model.pkl` (takes ~2-5 minutes)

**Expected Output:**
```
Loading dataset from data/flood_training_data.csv...
Training RandomForestClassifier with 100 estimators...
Model saved to models/flood_model.pkl
Label encoder saved to models/flood_label_encoder.pkl
```

### 3. Run the Flask Application
```bash
python app.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 4. Open Web Browser
Navigate to: `http://localhost:5000`

### 5. Quick Test
1. Click **Register** and create an account
2. Click **Login** with your credentials
3. Go to **Flash Flood Forecasting**
4. Download the template CSV or create your own with columns:
   - `rainfall` (0-100)
   - `humidity` (0-100)
   - `temperature` (-50 to 60)
5. Upload the CSV file
6. See your flood risk prediction!

---

## 📋 CSV Template

Create a file named `test.csv`:
```csv
rainfall,humidity,temperature
75.5,85.2,18
```

**Interpretations:**
- **Low Risk**: rainfall < 40, humidity < 60
- **Medium Risk**: rainfall 40-75, humidity 60-80
- **High Risk**: rainfall > 75, humidity > 80

---

## 🧪 Quick Test Cases

### Test Case 1: Low Risk
```csv
rainfall,humidity,temperature
25,45,28
```
Expected Result: ✅ Low Risk

### Test Case 2: Medium Risk
```csv
rainfall,humidity,temperature
60,70,22
```
Expected Result: ⚠️ Medium Risk

### Test Case 3: High Risk
```csv
rainfall,humidity,temperature
95,90,15
```
Expected Result: 🚨 High Risk (Alert)

---

## 🔗 Key Routes

After logging in:

| Route | Purpose |
|-------|---------|
| `/user_home` | Dashboard |
| `/upload_csv` | 🌊 Flood Forecasting (NEW) |
| `/predict` | ☁️ Cloudburst Detection |
| `/user_history` | View all predictions |
| `/logout` | Logout |

---

## 🎯 What the Module Does

1. **Accepts CSV input** with rainfall, humidity, temperature
2. **Predicts flood risk** using RandomForest machine learning model
3. **Calculates confidence** score (0-100%)
4. **Combines with cloudburst** detection from satellite images
5. **Generates alerts** (Safe ✅, Warning ⚠️, Critical 🚨)
6. **Sends email** for critical conditions
7. **Saves results** to database for history tracking

---

## ⚙️ Configuration

### Email Alerts (Optional)

In `app.py`, configure your Gmail:

```python
# Line ~78
sender_email = "your_email@gmail.com"
sender_password = "your_app_password"
```

**For Gmail Users:**
1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Create "App Password" for Mail
3. Copy the 16-character password
4. Paste it in `sender_password`

---

## 🐛 Troubleshooting

### "Model file not found"
```
Solution: Run `python train_flood_model.py` first
```

### "Missing columns in CSV"
```
Solution: Ensure CSV has exactly these column names (lowercase):
- rainfall
- humidity
- temperature
```

### Port Already in Use
```bash
# Change port in app.py line ~400:
# app.run(debug=True, port=5001)  # Use different port
```

### Model Takes Too Long to Train
```
Normal: 2-5 minutes for 1000 samples
The training is CPU-intensive, be patient or reduce:
- n_estimators: 100 → 50
- max_depth: 20 → 10
In train_flood_model.py
```

---

## 📊 Model Performance

Expected Accuracy: **94-97%**

```
Classification Report:
              precision    recall  f1-score   support
        High       0.95      0.92      0.94        60
        Low        0.95      0.97      0.96        65
      Medium       0.93      0.93      0.93        75
```

---

## 🚀 Next Steps

1. **Read Full Documentation**: `FLOOD_FORECASTING_README.md`
2. **Try Examples**: `python example_usage.py`
3. **Use Your Own Data**: 
   - Prepare CSV with your environmental data
   - Train model: `python train_flood_model.py`
   - Run web app and upload CSV
4. **Integrate with Existing System**:
   - Combine with cloudburst detection
   - Deploy to production
   - Set up email alerts

---

## 📞 Need Help?

Check documentation:
- **Configuration Issues**: FLOOD_FORECASTING_README.md → Troubleshooting
- **Model Training**: train_flood_model.py code comments
- **API Usage**: flood_predictor.py docstrings
- **Examples**: example_usage.py demonstrations

---

**Happy Flood Forecasting! 🌊**
