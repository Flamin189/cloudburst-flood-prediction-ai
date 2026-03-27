# 🌩️ Cloudburst Detection & Flash Flood Risk Prediction System 🚨

A **multistage AI-based web application** that detects cloudburst events using deep learning and predicts flash flood risk using environmental data and machine learning.

---

## 🚀 Project Overview

This system is designed to provide **early warning alerts** for extreme weather conditions by combining:

* 🌩️ **Cloudburst Detection (Deep Learning - CNN)**
* 🌊 **Flood Risk Prediction (Machine Learning - Random Forest)**
* 📊 **Environmental Data Analysis (CSV Input)**
* 📧 **Real-time Email Alerts**

---

## 🧠 Key Features

✨ Multistage AI Pipeline
✨ Cloudburst Detection from Images
✨ Flood Risk Prediction using Weather + Terrain Data
✨ CSV Upload for Real-time Analysis
✨ Automated Email Alerts 🚨
✨ Admin Dashboard & History Tracking
✨ Clean & Responsive UI

---

## 🏗️ System Architecture

```
User Input
   │
   ├── 📸 Image → CNN Model → Cloudburst Detection
   │
   ├── 📄 CSV → ML Model → Flood Risk Prediction
   │
   └── 🔗 Combined Logic → Final Alert 🚨
```

---

## 🛠️ Tech Stack

### 💻 Backend

* Python 🐍
* Flask

### 🎨 Frontend

* HTML5
* CSS3 (Bootstrap)
* JavaScript

### 🤖 Machine Learning

* TensorFlow / Keras (CNN Models)
* Scikit-learn (Random Forest)

### 🗄️ Database

* SQLite

### 📧 Notifications

* SMTP (Email Alerts)

---

## 📊 Input Parameters (Flood Prediction)

The system uses the following environmental factors:

* 🌧️ Rainfall Intensity
* ⏱️ Rainfall Duration
* 💧 Humidity
* 🌡️ Temperature
* 🏔️ Terrain Type
* ⛰️ Elevation
* 🌱 Soil Type
* 🚰 Drainage Capacity
* 🌧️ Previous Rainfall

---

## 📂 Project Structure

```
cloudburst-flood-prediction-ai/
│
├── app.py
├── models/
│   ├── flood_model.pkl
│   └── (deep learning models excluded)
│
├── templates/
├── static/
├── dataset/
├── uploads/
├── requirements.txt
└── README.md
```

---

## ⚠️ Important Note

> 🚫 Deep learning model files (`.h5`) are NOT included in this repository due to GitHub size limitations.

👉 The model is hosted externally and loaded dynamically during runtime.

---

## ▶️ How to Run the Project

### 1️⃣ Clone the repository

```
git clone https://github.com/Flamin189/cloudburst-flood-prediction-ai.git
cd cloudburst-flood-prediction-ai
```

---

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

---

### 3️⃣ Run the application

```
python app.py
```

---

### 4️⃣ Open in browser

```
http://localhost:5000
```

---

## 📸 Screenshots (Add your images here)

* Cloudburst Detection Page
* Flood Prediction Module
* Results Dashboard
* Email Alert

---

## 🚨 Alert System

The system generates alerts based on combined results:

| Cloudburst | Flood Risk | Alert           |
| ---------- | ---------- | --------------- |
| Yes        | High       | 🚨 Severe Alert |
| Yes        | Medium     | ⚠️ Warning      |
| No         | Low        | ✅ Safe          |

---

## 🎯 Future Improvements

* 📡 Real-time weather API integration
* 🛰️ Satellite data integration
* 📱 Mobile application
* 🌍 GIS-based flood mapping

---

## 🎓 Academic Value

This project demonstrates:

* Multimodal AI Systems
* Deep Learning + Machine Learning Integration
* Real-world Disaster Prediction
* End-to-End Full Stack Development

---

## 👨‍💻 Author

**Flamin David**
Final Year Engineering Student

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

---

##
