# Flash Flood Forecasting & Cloudburst Detection System

A comprehensive Flask-based AI system that combines CNN-based cloudburst detection with machine learning-powered flood risk forecasting.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Training the Flood Model](#training-the-flood-model)
- [Running the Application](#running-the-application)
- [Features](#features)
- [API Routes](#api-routes)
- [Data Format](#data-format)
- [Model Integration](#model-integration)

## 🌦️ Overview

This system provides:
1. **Cloudburst Detection**: CNN-based image analysis to detect cloud burst patterns
2. **Flood Forecasting**: RandomForest-based prediction using environmental parameters
3. **Integrated Alerts**: Combined analysis for comprehensive hazard assessment
4. **User Management**: Authentication and prediction history tracking
5. **Email Notifications**: Automatic alerts for critical conditions

## 🏗️ Architecture

```
Cloud Burst & Flood Detection System
├── Image Analysis Pipeline
│   ├── AlexNet/ResNet50/VGG16 CNN Models
│   ├── Image Upload & Processing
│   └── Cloudburst Classification
│
├── Flood Forecasting Pipeline
│   ├── RandomForestClassifier
│   ├── CSV Feature Input (rainfall, humidity, temperature)
│   └── Flood Risk Prediction (Low/Medium/High)
│
├── Alert Integration
│   ├── Combined Result Analysis
│   ├── Alert Level Classification
│   └── Email Notifications
│
└── User Management
    ├── Registration & Login
    ├── Prediction History
    ├── Admin Dashboard
    └── Data Persistence
```

## 💾 Installation

### Prerequisites
- Python 3.7+
- pip package manager
- Virtual environment (recommended)

### Step 1: Install Dependencies

```bash
pip install flask
pip install tensorflow
pip install scikit-learn
pip install pandas
pip install numpy
pip install werkzeug
```

### Step 2: Directory Structure

Ensure the following directories exist:
```
d:\modify\cloud\
├── models/
│   ├── AlexNet_best.h5
│   ├── ResNet50_best.h5
│   ├── VGG16_best.h5
│   ├── flood_model.pkl          # Will be created after training
│   └── flood_label_encoder.pkl  # Will be created after training
├── data/
│   └── flood_training_data.csv  # Your training dataset
├── static/
│   ├── uploads/                 # User uploads
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── upload_csv.html          # CSV upload form
│   ├── flood_result.html        # Flood results display
│   └── ... other templates
├── app.py                        # Main Flask app
├── flood_predictor.py           # Flood prediction module
├── train_flood_model.py         # Training script
└── database.db                  # SQLite database (auto-created)
```

## 🚀 Training the Flood Model

### Step 1: Prepare Your Dataset

Create a CSV file with the following format:
```csv
rainfall,humidity,temperature,flood_risk
85.5,88.2,18,High
25.0,45.1,28,Low
70.0,75.5,20,Medium
```

**Column Descriptions:**
- `rainfall`: Rainfall amount (0-100)
- `humidity`: Humidity percentage (0-100)
- `temperature`: Temperature in Celsius (-50 to 60)
- `flood_risk`: Target variable (Low, Medium, High)

Place your CSV file at: `data/flood_training_data.csv`

### Step 2: Train the Model

```bash
cd d:\modify\cloud
python train_flood_model.py
```

**What the training script does:**
1. Loads and validates the CSV dataset
2. Encodes target variable (flood_risk) to integers
3. Splits data into 80% training, 20% testing
4. Trains RandomForestClassifier with 100 estimators
5. Evaluates model performance (accuracy, precision, recall)
6. Saves model as `models/flood_model.pkl`
7. Saves label encoder as `models/flood_label_encoder.pkl`

**Expected Output:**
```
Loading dataset from data/flood_training_data.csv...
Dataset shape: (1000, 4)
Columns: ['rainfall', 'humidity', 'temperature', 'flood_risk']

Splitting dataset into train (80%) and test (20%)...
Training set size: (800, 3)
Test set size: (200, 3)

Training RandomForestClassifier with 100 estimators...

Accuracy: 0.9450

Classification Report:
              precision    recall  f1-score   support
        High       0.95      0.92      0.94        60
       Low        0.95      0.97      0.96        65
      Medium       0.93      0.93      0.93        75

Feature Importance:
  rainfall: 0.5234
  humidity: 0.3456
  temperature: 0.1310
```

### Step 3: Verify Model Files

After training, verify these files exist:
- `models/flood_model.pkl` (~500KB-2MB)
- `models/flood_label_encoder.pkl` (~1KB)

## 🏃 Running the Application

### Step 1: Initialize Database

The application automatically creates the SQLite database on first run.

### Step 2: Start Flask Server

```bash
cd d:\modify\cloud
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
 * Press CTRL+C to quit
```

### Step 3: Access the Application

Open web browser and navigate to: `http://localhost:5000`

## ✨ Features

### 1. User Authentication
- User registration with email verification capability
- Login/logout functionality
- Separate admin dashboard
- Session management

### 2. Cloudburst Detection
- Image upload and analysis
- CNN model prediction (AlexNet, ResNet50, VGG16)
- Confidence scoring
- Prediction history

### 3. Flood Forecasting
- CSV file upload with environmental data
- RandomForest-based prediction
- Multi-level risk assessment (Low/Medium/High)
- Probability distribution for each risk level
- Input validation for all parameters

### 4. Alert Integration
- Combined analysis of cloudburst and flood results
- Three alert levels: Safe (✅), Warning (⚠️), Critical (🚨)
- Dynamic alert messaging based on combined conditions
- Automatic email notifications for critical alerts

### 5. Data Management
- Prediction history storage in SQLite
- User-specific prediction tracking
- Admin dashboard for all predictions
- Timestamp recording for all predictions

## 🔄 API Routes

### Public Routes
- `GET /` - Home page
- `GET /register`, `POST /register` - User registration
- `GET /login`, `POST /login` - User login
- `GET /admin_login`, `POST /admin_login` - Admin login

### Authenticated User Routes
- `GET /user_home` - User dashboard
- `GET /predict`, `POST /predict` - Cloudburst detection (image upload)
- `GET /upload_csv`, `POST /upload_csv` - **Flood forecasting (CSV upload)**
- `GET /user_history` - View all predictions
- `GET /logout` - User logout

### Admin Routes
- `GET /admin_dashboard` - View all predictions

## 📊 Data Format

### CSV Input for Flood Prediction

**File Format:** `.csv` (Comma-Separated Values)

**Required Columns:**
```
rainfall,humidity,temperature
85.5,88.2,18
```

**Constraints:**
- Rainfall: 0-100 (any unit, e.g., mm, inches)
- Humidity: 0-100 (percentage)
- Temperature: -50 to 60 (Celsius)

**Validation:**
- All values must be numeric
- Missing values will cause an error
- The system uses only the first row of the CSV

### Example CSV Files

**High Flood Risk:**
```csv
rainfall,humidity,temperature
95,90,15
```

**Medium Flood Risk:**
```csv
rainfall,humidity,temperature
60,70,22
```

**Low Flood Risk:**
```csv
rainfall,humidity,temperature
20,40,30
```

## 🔗 Model Integration

### Flood Prediction Module

Located in: `flood_predictor.py`

#### FloodPredictor Class

```python
from flood_predictor import FloodPredictor, combine_alerts

# Initialize predictor
predictor = FloodPredictor()

# Predict from parameters
result = predictor.predict(rainfall=85.5, humidity=88.2, temperature=18)
print(result)
# Output:
# {
#     'flood_risk': 'High',
#     'confidence': 0.92,
#     'probabilities': {'High': 0.92, 'Medium': 0.07, 'Low': 0.01},
#     'error': None
# }

# Predict from CSV file
result, error = predictor.predict_from_csv('data/sample.csv')

# Combine alerts
alert = combine_alerts(
    cloudburst_result='Cloud Burst',
    flood_result='High',
    flood_confidence=0.92
)
# Output:
# {
#     'final_alert': 'Alert 🚨',
#     'alert_level': 'Critical',
#     'details': 'Cloudburst detected... High flood risk...',
#     'cloudburst_result': 'Cloud Burst',
#     'flood_result': 'High'
# }
```

### Integration with Flask

The Flask app automatically initializes the flood predictor:

```python
# In app.py
from flood_predictor import get_flood_predictor, combine_alerts

@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    flood_predictor = get_flood_predictor()
    
    # Make prediction
    flood_result, error = flood_predictor.predict_from_csv(csv_path)
    
    # Get cloudburst result (from image analysis or form)
    cloudburst_result = 'Normal'  # or 'Cloud Burst'
    
    # Combine results
    combined = combine_alerts(cloudburst_result, flood_result['flood_risk'])
```

## 📧 Email Notifications

### Setup Gmail Configuration

In `app.py`, configure your email:

```python
sender_email = "your_email@gmail.com"
sender_password = "your_app_specific_password"  # Use app password for Gmail
```

**For Gmail:**
1. Enable 2-factor authentication
2. Create an ["App Password"](https://myaccount.google.com/apppasswords)
3. Use the generated app password (not your regular password)

### Alert Email Triggers

- **Cloudburst Detection**: Email sent when "Cloud Burst" is detected
- **Critical Flood Risk**: Email sent when flood risk is "High" + cloudburst detected
- **Custom Messages**: Different templates for different alert types

## 🧪 Testing

### Test Flood Prediction

```python
from flood_predictor import FloodPredictor

predictor = FloodPredictor()

# Test Low Risk
result = predictor.predict(rainfall=20, humidity=40, temperature=30)
print(f"Low Risk Test: {result['flood_risk']}")  # Should be: Low

# Test High Risk
result = predictor.predict(rainfall=95, humidity=90, temperature=15)
print(f"High Risk Test: {result['flood_risk']}")  # Should be: High

# Test Medium Risk
result = predictor.predict(rainfall=60, humidity=70, temperature=22)
print(f"Medium Risk Test: {result['flood_risk']}")  # Should be: Medium
```

### Test with Sample CSV

```bash
# Upload data/sample_flood_data.csv through the web interface
# OR programmatically:

from flood_predictor import FloodPredictor
predictor = FloodPredictor()
result, error = predictor.predict_from_csv('data/sample_flood_data.csv')
print(result)
```

## 📈 Model Performance

### Expected Metrics (on sample data)
- **Accuracy**: 94-97%
- **Precision**: 93-96% (per class)
- **Recall**: 92-97% (per class)

### Feature Importance

Typical feature importance from training:
- **Rainfall**: 50-55% (most important)
- **Humidity**: 35-40%
- **Temperature**: 10-15%

## 🔧 Troubleshooting

### Model Not Found Error
```
FileNotFoundError: Model file not found: models/flood_model.pkl
```
**Solution:** Run `python train_flood_model.py` first to train the model.

### CSV Parsing Error
```
Error processing CSV: Missing columns in CSV: rainfall, humidity, temperature
```
**Solution:** Ensure your CSV has exactly these column names (case-sensitive, lowercase).

### Prediction Error: "All values must be numeric"
**Solution:** Check that rainfall, humidity, and temperature are numbers, not text.

### Email Not Sending
**Solution:** 
- Verify Gmail app password is correct
- Check internet connection
- Ensure 2-factor authentication is enabled on Gmail

## 📝 Project Structure

```
d:\modify\cloud\
│
├── app.py                          # Main Flask application
├── flood_predictor.py              # Flood prediction module
├── train_flood_model.py            # Model training script
│
├── models/
│   ├── AlexNet_best.h5            # Cloudburst detection (CNN)
│   ├── ResNet50_best.h5           # Alternative CNN model
│   ├── VGG16_best.h5              # Alternative CNN model
│   ├── flood_model.pkl            # Flood prediction model
│   └── flood_label_encoder.pkl    # Label encoder
│
├── data/
│   ├── flood_training_data.csv    # Training dataset
│   └── sample_flood_data.csv      # Sample data
│
├── static/
│   ├── uploads/                   # User uploaded files
│   ├── css/style.css              # Styling
│   └── js/script.js               # JavaScript
│
├── templates/
│   ├── base.html                  # Base template
│   ├── index.html                 # Home page
│   ├── predict.html               # Image upload form
│   ├── result.html                # Image prediction results
│   ├── upload_csv.html            # CSV upload form
│   ├── flood_result.html          # Flood prediction results
│   ├── login.html                 # User login
│   ├── register.html              # User registration
│   ├── user_home.html             # User dashboard
│   ├── user_history.html          # Prediction history
│   ├── admin_login.html           # Admin login
│   └── admin_dashboard.html       # Admin panel
│
└── database.db                     # SQLite database (auto-created)
```

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install flask tensorflow scikit-learn pandas numpy werkzeug
```

### 2. Train Model
```bash
python train_flood_model.py
```

### 3. Run Application
```bash
python app.py
```

### 4. Access Web App
Navigate to `http://localhost:5000`

### 5. Register and Login
- Create a new account
- Login with your credentials

### 6. Test Flood Forecasting
- Go to "Flash Flood Forecasting"
- Upload a CSV file with rainfall, humidity, temperature
- View predictions and alerts

## 📚 Additional Resources

- [Scikit-learn RandomForest Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [TensorFlow/Keras Documentation](https://keras.io/)
- [Pandas CSV Documentation](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)

## 📄 License

This project is provided as-is for educational and research purposes.

## 🤝 Support

For issues, questions, or improvements, please document them clearly with:
- Error message and stack trace
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, installed packages)

---

**Last Updated:** March 2026
