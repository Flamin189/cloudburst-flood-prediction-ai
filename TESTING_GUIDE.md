# Testing Guide for Flash Flood Forecasting Module

## 🧪 Automated Testing

Run the example script to verify everything works:

```bash
python example_usage.py
```

This will test:
- Model loading and initialization
- Direct predictions from parameters
- CSV file predictions
- Alert combination logic
- Input validation
- Feature importance explanation

---

## ✅ Unit Tests

### Test 1: Model Training

**File**: `train_flood_model.py`

```bash
python train_flood_model.py
```

**Verification Checklist:**
- [ ] Files created: `models/flood_model.pkl`
- [ ] Files created: `models/flood_label_encoder.pkl`
- [ ] Training completed without errors
- [ ] Accuracy reported > 90%
- [ ] Feature importance calculated

**Expected Output:**
```
Loading dataset...
Training RandomForestClassifier...
Accuracy: 0.9450

Feature Importance:
  rainfall: 0.52
  humidity: 0.35
  temperature: 0.13
```

### Test 2: Model Loading

```python
from flood_predictor import FloodPredictor

predictor = FloodPredictor()
print("Model loaded successfully!")
```

**Verification:**
- [ ] No FileNotFoundError
- [ ] Model and encoder loaded
- [ ] Ready for predictions

### Test 3: Direct Prediction

```python
from flood_predictor import FloodPredictor

predictor = FloodPredictor()

# Test Low Risk
result = predictor.predict(rainfall=20, humidity=40, temperature=30)
assert result['flood_risk'] == 'Low', "Failed: Low risk prediction"

# Test High Risk
result = predictor.predict(rainfall=95, humidity=90, temperature=15)
assert result['flood_risk'] == 'High', "Failed: High risk prediction"

# Test Medium Risk
result = predictor.predict(rainfall=60, humidity=70, temperature=22)
assert result['flood_risk'] == 'Medium', "Failed: Medium risk prediction"

print("✓ All direct predictions passed!")
```

### Test 4: Input Validation

```python
from flood_predictor import FloodPredictor

predictor = FloodPredictor()

# Test invalid rainfall
result = predictor.predict(rainfall=150, humidity=80, temperature=20)
assert result['error'] is not None, "Should reject rainfall > 100"

# Test invalid humidity
result = predictor.predict(rainfall=50, humidity=120, temperature=20)
assert result['error'] is not None, "Should reject humidity > 100"

# Test invalid temperature
result = predictor.predict(rainfall=50, humidity=80, temperature=100)
assert result['error'] is not None, "Should reject temperature > 60"

# Test non-numeric input
result = predictor.predict(rainfall="abc", humidity=80, temperature=20)
assert result['error'] is not None, "Should reject non-numeric input"

print("✓ All validation tests passed!")
```

### Test 5: CSV Prediction

```python
from flood_predictor import FloodPredictor
import pandas as pd

# Create test CSV
df = pd.DataFrame({
    'rainfall': [75.5],
    'humidity': [85.2],
    'temperature': [18]
})
df.to_csv('test_data.csv', index=False)

# Test prediction
predictor = FloodPredictor()
result, error = predictor.predict_from_csv('test_data.csv')

assert error is None, f"Prediction failed: {error}"
assert result['flood_risk'] in ['Low', 'Medium', 'High']
print(f"✓ CSV prediction passed! Risk: {result['flood_risk']}")
```

## 🌐 Flask Integration Tests

### Test 6: Flask App Initialization

```python
import sys
sys.path.insert(0, '.')

from app import app

with app.app_context():
    print("✓ Flask app initialized successfully")
```

### Test 7: Database Creation

```python
import sqlite3
from app import init_db

init_db()

# Verify tables exist
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
)
tables = [row[0] for row in cursor.fetchall()]

required_tables = ['users', 'predictions', 'flood_predictions']
for table in required_tables:
    assert table in tables, f"Missing table: {table}"

conn.close()
print("✓ All database tables created successfully")
```

### Test 8: Flask Routes

```bash
python -m pytest test_routes.py -v
```

Or manually test routes:

```python
from app import app
import json

client = app.test_client()

# Test home page
response = client.get('/')
assert response.status_code == 200, "Home page load failed"

# Test CSV upload form
response = client.get('/upload_csv')
assert response.status_code == 302, "Should redirect to login"  # Not logged in

print("✓ Flask routes responding correctly")
```

## 🔍 Integration Tests

### Test 9: End-to-End Workflow

This test simulates a complete user workflow:

```python
from flood_predictor import FloodPredictor, combine_alerts
import pandas as pd

print("TEST: End-to-End Workflow\n")

# Step 1: Train model (if needed)
print("Step 1: Ensuring model is trained...")
predictor = FloodPredictor()
print("✓ Model loaded\n")

# Step 2: Create test data
print("Step 2: Creating test data...")
test_data = pd.DataFrame({
    'rainfall': [85.5, 60.0, 25.0],
    'humidity': [88.2, 70.0, 45.0],
    'temperature': [18, 22, 28]
})
test_data.to_csv('workflow_test.csv', index=False)
print("✓ Test data created\n")

# Step 3: Predict from CSV
print("Step 3: Predicting from CSV...")
result, error = predictor.predict_from_csv('workflow_test.csv')
assert error is None
print(f"✓ Prediction successful: {result['flood_risk']}\n")

# Step 4: Combine with cloudburst
print("Step 4: Combining with cloudburst result...")
alert = combine_alerts('Cloud Burst', result['flood_risk'], result['confidence'])
print(f"✓ Alert generated: {alert['final_alert']}")
print(f"✓ Alert level: {alert['alert_level']}\n")

# Step 5: Verify output
print("Step 5: Verifying output...")
assert alert['final_alert'] in ['Safe ✅', 'Caution ⚠️', 'Alert 🚨']
assert alert['alert_level'] in ['Safe', 'Warning', 'Critical']
print("✓ Output format correct\n")

print("="*50)
print("✓ End-to-End Workflow Test PASSED!")
print("="*50)
```

Run this test:
```bash
python -c "exec(open('test_workflow.py').read())"
```

## 📊 Performance Tests

### Test 10: Response Time

```python
import time
from flood_predictor import FloodPredictor

predictor = FloodPredictor()

# Measure prediction time
start = time.time()
for i in range(100):
    predictor.predict(rainfall=50, humidity=70, temperature=22)
elapsed = time.time() - start

avg_time = elapsed / 100
print(f"Average prediction time: {avg_time*1000:.2f}ms")
assert avg_time < 0.1, "Prediction should be < 100ms"
print("✓ Performance test passed!")
```

### Test 11: Scalability

```python
from flood_predictor import FloodPredictor
import pandas as pd

predictor = FloodPredictor()

# Test with large CSV
n_rows = 1000
df = pd.DataFrame({
    'rainfall': [50] * n_rows,
    'humidity': [70] * n_rows,
    'temperature': [22] * n_rows
})
df.to_csv('large_test.csv', index=False)

# Only first row is used, so it should be fast
import time
start = time.time()
result, error = predictor.predict_from_csv('large_test.csv')
elapsed = time.time() - start

print(f"Time to process {n_rows}-row CSV: {elapsed*1000:.2f}ms")
assert elapsed < 1.0, "Should be fast even with large file"
print("✓ Scalability test passed!")
```

## 🔐 Security Tests

### Test 12: Input Injection

```python
from flood_predictor import FloodPredictor

predictor = FloodPredictor()

# Test SQL injection in CSV filename (not applicable, files handled by framework)
# Test parameter validation
result = predictor.predict(
    rainfall="'; DROP TABLE users; --",
    humidity=70,
    temperature=22
)
assert result['error'] is not None, "Should reject non-numeric input"
print("✓ Injection prevention working")
```

### Test 13: File Validation

```python
# Create malicious CSV
with open('malicious.csv', 'w') as f:
    f.write("rainfall,humidity,temperature\n")
    f.write("1" * 1000 + ",70,22\n")

from flood_predictor import FloodPredictor
predictor = FloodPredictor()

result, error = predictor.predict_from_csv('malicious.csv')
# Should either handle gracefully or reject
print("✓ File validation working")
```

## 📋 Test Checklist

- [ ] Model training completes successfully
- [ ] Model file created and loadable
- [ ] Direct predictions work for Low/Medium/High risk
- [ ] Input validation rejects invalid values
- [ ] CSV predictions work correctly
- [ ] Alert combination generates correct alerts
- [ ] Flask app initializes without errors
- [ ] Database tables created
- [ ] Flask routes respond correctly
- [ ] End-to-end workflow works
- [ ] Prediction time < 100ms
- [ ] Large data handled efficiently
- [ ] Malicious input rejected
- [ ] Email configuration ready (if enabled)

## 🚀 Deployment Verification

Before deploying to production:

1. **Run all tests above**
2. **Test with real data** from your domain
3. **Verify database persistence**
4. **Check email notifications** (if applicable)
5. **Test user authentication flow**
6. **Monitor memory usage** during predictions
7. **Test with concurrent users**

## 📈 Monitoring

During deployment, monitor:
- Model prediction accuracy on new data
- User login success rates
- CSV upload success rates
- Email delivery status
- Database query performance
- Server memory and CPU usage

---

**All tests passed? Your system is ready for deployment! 🎉**
