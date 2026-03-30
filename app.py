import os
import numpy as np
import pandas as pd
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from datetime import datetime

from flood_predictor import get_flood_predictor, combine_alerts

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------- MODEL ----------------
MODEL_URL = "https://alexnet948652.s3.eu-north-1.amazonaws.com/AlexNet_best.h5"
MODEL_PATH = "AlexNet_best.h5"

model = None  # Lazy loading

def download_model():
    if not os.path.exists(MODEL_PATH):
        os.makedirs("models", exist_ok=True)
        print("Downloading model...")
        r = requests.get(MODEL_URL)
        r.raise_for_status()
        with open(MODEL_PATH, "wb") as f:
            f.write(r.content)
        print("Model downloaded")

def get_model():
    global model
    if model is None:
        download_model()
        model = load_model(MODEL_PATH)
        print("Model loaded")
    return model

# ---------------- DB ----------------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        image_path TEXT,
        prediction_result TEXT,
        confidence REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- HELPERS ----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_image(image_path):
    model = get_model()

    img = image.load_img(image_path, target_size=(224, 224))
    img = image.img_to_array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)[0][0]

    if prediction < 0.5:
        return "Cloud Burst", (1 - prediction) * 100
    return "Normal Cloud", prediction * 100

# ---------------- ROUTES ----------------

@app.route('/')
def index():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)",
                         (username, email, password))
            conn.commit()
            flash("Registered successfully")
            return redirect(url_for('login'))
        except:
            flash("User already exists")
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            return redirect(url_for('predict'))

        flash("Invalid login")

    return render_template('login.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            result, confidence = predict_image(filepath)

            conn = get_db()
            conn.execute("INSERT INTO predictions (user_id,image_path,prediction_result,confidence) VALUES (?,?,?,?)",
                         (session['user_id'], filepath, result, confidence))
            conn.commit()
            conn.close()

            return render_template('result.html', result=result, confidence=confidence, image=filepath)

    return render_template('predict.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)