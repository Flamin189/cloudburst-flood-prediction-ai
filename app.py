# cd d:\1cloudburst\cloud && python app.py
import os
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import datetime
from datetime import datetime
from flood_predictor import get_flood_predictor, combine_alerts, fetch_latest_cloudburst_from_db

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Model loading
MODEL_PATH = 'https://github.com/Flamin189/cloudburst-flood-prediction-ai/releases/download/v1.0/AlexNet_best.h5'
model = load_model(MODEL_PATH)

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Predictions table (for image-based cloudburst detection)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        image_path TEXT NOT NULL,
        prediction_result TEXT NOT NULL,
        confidence REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Flood predictions table (for CSV-based flood forecasting)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flood_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        rainfall REAL NOT NULL,
        humidity REAL NOT NULL,
        temperature REAL NOT NULL,
        flood_risk TEXT NOT NULL,
        flood_confidence REAL NOT NULL,
        cloudburst_result TEXT,
        final_alert TEXT,
        alert_level TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()
#flamin
# Initialize database
init_db()

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_alert_email(to_email, flood_risk, cloudburst_result=None, confidence=None, mention_cloudburst=True):
    """
    Send human-friendly emergency alert email for critical flood conditions
    
    Args:
        to_email: Recipient email address
        flood_risk: Flood risk level (High/Medium/Low)
        cloudburst_result: Cloudburst detection result (optional)
        confidence: Model confidence percentage (optional)
        mention_cloudburst: Whether to mention cloudburst in the email (True/False)
    """
    # Email configuration
    sender_email = "test.abn000@gmail.com"
    sender_password = "rlcz nvgj uuux iurl"  # Use app-specific password if using Gmail
    receiver_email = to_email
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    
    # Dynamic subject based on risk level and cloudburst
    if mention_cloudburst and cloudburst_result == "Cloud Burst":
        if flood_risk == "High":
            message["Subject"] = "🚨 Emergency Alert: Cloudburst and High Flood Risk Detected"
        elif flood_risk == "Medium":
            message["Subject"] = "⚠️ Warning Alert: Cloudburst and Moderate Flood Risk Detected"
        else:  # Low
            message["Subject"] = "⚠️ Alert: Cloudburst Detected - Flood Risk is Low"
    else:
        # Only flood risk mentioned (no cloudburst)
        if flood_risk == "High":
            message["Subject"] = "🚨 Emergency Alert: High Flood Risk Detected"
        elif flood_risk == "Medium":
            message["Subject"] = "⚠️ Warning Alert: Moderate Flood Risk Detected"
        else:  # Low
            message["Subject"] = "📢 Update: Low Flood Risk"
    
    # Determine risk description and instructions
    if flood_risk == "High":
        risk_description = "HIGH"
        instructions = """
        <strong>Immediate Actions Required:</strong>
        <ul>
            <li>Move to a safe location immediately</li>
            <li>Avoid low-lying areas and waterlogged zones</li>
            <li>Follow instructions from local authorities</li>
            <li>Prepare emergency supplies and documents</li>
            <li>Stay alert for further updates</li>
        </ul>
        """
    elif flood_risk == "Medium":
        risk_description = "MODERATE"
        instructions = """
        <strong>Recommended Precautions:</strong>
        <ul>
            <li>Stay vigilant and monitor weather conditions</li>
            <li>Prepare for possible evacuation</li>
            <li>Avoid unnecessary travel in affected areas</li>
            <li>Keep emergency contacts ready</li>
            <li>Follow local authority guidance</li>
        </ul>
        """
    else:  # Low
        risk_description = "LOW"
        instructions = """
        <strong>Current Status:</strong>
        <ul>
            <li>Current conditions indicate low flood probability</li>
            <li>Continue to monitor weather forecasts</li>
            <li>Remain prepared for changing conditions</li>
        </ul>
        """
    
    # Build alert details section based on mention_cloudburst flag
    if mention_cloudburst and cloudburst_result == "Cloud Burst":
        alert_details = f"""
        <p><strong>Alert Details:</strong></p>
        <ul>
            <li>A cloudburst event has been detected in your monitored area</li>
            <li>Based on environmental analysis, the flood risk is <strong>{risk_description}</strong></li>
        </ul>
        """
        header_title = "Cloudburst and Flood Risk Alert"
    else:
        alert_details = f"""
        <p><strong>Flood Risk Alert Details:</strong></p>
        <ul>
            <li>Based on environmental analysis, the flood risk is <strong>{risk_description}</strong></li>
        </ul>
        """
        header_title = "Flood Risk Alert"
    
    # Build email body
    confidence_text = f" (Model Confidence: {confidence:.1%})" if confidence else ""
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #d9534f;">{header_title}</h2>
            
            <p>Dear User,</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #d9534f; margin: 20px 0;">
                {alert_details}
                {f'<p style="margin: 10px 0 0 0;">{confidence_text}</p>' if confidence_text else ''}
            </div>
            
            {instructions}
            
            <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                <p><strong>Important:</strong> This is an automated alert from the Cloud Burst & Flood Detection System. 
                Please verify the situation with local authorities and take appropriate safety measures.</p>
            </div>
            
            <p>Stay safe and informed.</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                This alert was generated by the AI Disaster Prediction System<br>
                For support, contact your local emergency services
            </p>
        </div>
    </body>
    </html>
    """
    
    message.attach(MIMEText(body, "html"))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print(f"✅ Emergency alert email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending emergency alert email: {e}")
        return False

def predict_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    prediction = model.predict(img_array)[0][0]
    
    if prediction < 0.5:
        result = "Cloud Burst"
        confidence = (1 - prediction) * 100
    else:
        result = "Normal Cloud"
        confidence = prediction * 100
    
    return result, confidence

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Allow accessing columns by name
    return conn

def get_latest_cloudburst():
    """
    Fetch the MOST RECENT cloudburst prediction from database
    
    Returns:
        str: Latest cloudburst result ("Cloud Burst" or "Normal Cloud") or "Normal Cloud" as default
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query for the MOST RECENT prediction
        cursor.execute('''
            SELECT prediction_result
            FROM predictions
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            return "Normal Cloud"
        
        cloudburst_value = result['prediction_result']
        # Ensure return value is either "Cloud Burst" or "Normal Cloud"
        if cloudburst_value == "Cloud Burst":
            return "Cloud Burst"
        else:
            return "Normal Cloud"
    
    except sqlite3.Error as e:
        print(f"Database error in get_latest_cloudburst: {e}")
        return "Normal Cloud"
    except Exception as e:
        print(f"Error in get_latest_cloudburst: {e}")
        return "No Data Available"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                          (username, email, hashed_password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('register'))
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            session['is_admin'] = False
            flash('Login successful!', 'success')
            return redirect(url_for('user_home'))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hardcoded admin credentials
        admin_username = "admin"
        admin_password = "admin123"
        
        if username == admin_username and password == admin_password:
            session['user_id'] = 0  # Special ID for admin
            session['username'] = admin_username
            session['is_admin'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'danger')
            return redirect(url_for('admin_login'))
    
    return render_template('admin_login.html')

@app.route('/user_home')
def user_home():
    if 'user_id' not in session or session.get('is_admin', False):
        flash('Please login as a user!', 'danger')
        return redirect(url_for('login'))
    
    # Get recent predictions for this user
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT prediction_result, confidence, timestamp
    FROM predictions
    WHERE user_id = ?
    ORDER BY timestamp DESC
    LIMIT 5
    ''', (session['user_id'],))
    
    recent_predictions = cursor.fetchall()
    conn.close()
    
    # Format recent predictions
    formatted_recent = []
    for pred in recent_predictions:
        confidence = pred['confidence']
        try:
            confidence = float(confidence)
        except (ValueError, TypeError) as e:
            print(f"Error converting confidence: {e}")
            confidence = 0.0
        
        formatted_recent.append({
            'prediction_result': pred['prediction_result'],
            'confidence': confidence,
            'timestamp': pred['timestamp']
        })
    
    return render_template('user_home.html', recent_predictions=formatted_recent)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session or session.get('is_admin', False):
        flash('Please login as a user!', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part!', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No image selected!', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Make prediction
            result, confidence = predict_image(file_path)
            
            # Save prediction to database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO predictions (user_id, image_path, prediction_result, confidence) VALUES (?, ?, ?, ?)', 
                          (session['user_id'], file_path, result, float(confidence)))
            conn.commit()
            conn.close()
            
            # Note: Email alerts are now sent from flood prediction route when both cloudburst AND high flood risk are detected
            
            # Get the relative path for the template
            relative_path = os.path.relpath(file_path, start=os.path.dirname(os.path.abspath(__file__)))
            
            return render_template('result.html', 
                                  result=result, 
                                  confidence=confidence, 
                                  image_path=relative_path,
                                  current_time=now)
        else:
            flash('Invalid file format! Please upload a PNG, JPG, or JPEG image.', 'danger')
            return redirect(request.url)
    
    return render_template('predict.html')

@app.route('/user_history')
def user_history():
    if 'user_id' not in session or session.get('is_admin', False):
        flash('Please login as a user!', 'danger')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user's predictions
    cursor.execute('''
    SELECT id, image_path, prediction_result, confidence, timestamp
    FROM predictions
    WHERE user_id = ?
    ORDER BY timestamp DESC
    ''', (session['user_id'],))
    
    predictions = cursor.fetchall()
    conn.close()
    
    # Convert predictions to a list of dictionaries with properly formatted data
    formatted_predictions = []
    for pred in predictions:
        # Handle confidence value
        confidence = pred['confidence']
        try:
            confidence = float(confidence)
        except (ValueError, TypeError) as e:
            print(f"Error converting confidence: {e}")
            confidence = 0.0  # Default value
        
        formatted_predictions.append({
            'id': pred['id'],
            'image_path': pred['image_path'],
            'prediction_result': pred['prediction_result'],
            'confidence': confidence,
            'timestamp': pred['timestamp']
        })
    
    return render_template('user_history.html', predictions=formatted_predictions)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin', False):
        flash('Please login as an admin!', 'danger')
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all predictions with user info
    cursor.execute('''
    SELECT p.id, u.username, u.email, p.image_path, p.prediction_result, p.confidence, p.timestamp
    FROM predictions p
    JOIN users u ON p.user_id = u.id
    ORDER BY p.timestamp DESC
    ''')
    
    predictions = cursor.fetchall()
    conn.close()
    
    # Convert predictions to a list of dictionaries with properly formatted data
    formatted_predictions = []
    for pred in predictions:
        # Handle confidence value - it should be a float now
        confidence = pred['confidence']
        try:
            confidence = float(confidence)
        except (ValueError, TypeError) as e:
            print(f"Error converting confidence: {e}")
            confidence = 0.0  # Default value
        
        formatted_predictions.append({
            'id': pred['id'],
            'username': pred['username'],
            'email': pred['email'],
            'image_path': pred['image_path'],
            'prediction_result': pred['prediction_result'],
            'confidence': confidence,
            'timestamp': pred['timestamp']
        })
    
    return render_template('admin_dashboard.html', predictions=formatted_predictions)

@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    """
    Flash Flood Prediction: Upload CSV and get multistage alert
    
    Expected CSV columns (9 features):
    - rainfall_intensity, rainfall_duration, humidity, temperature
    - terrain_type, elevation, soil_type, drainage_capacity, previous_rainfall
    
    Fetches latest cloudburst from database and combines results
    """
    if 'user_id' not in session or session.get('is_admin', False):
        flash('Please login as a user!', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Validate file upload
        if 'csv_file' not in request.files:
            flash('No file uploaded!', 'danger')
            return redirect(request.url)
        
        csv_file = request.files['csv_file']
        
        if csv_file.filename == '' or not csv_file.filename.lower().endswith('.csv'):
            flash('Please upload a valid CSV file!', 'danger')
            return redirect(request.url)
        
        try:
            # Save CSV file temporarily
            filename = secure_filename(csv_file.filename)
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{filename}"
            csv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            csv_file.save(csv_file_path)
            
            print(f"CSV file saved to: {csv_file_path}")
            
            # Load flood predictor
            flood_predictor = get_flood_predictor()
            if flood_predictor is None:
                flash('Flood prediction model not available. Please restart the application.', 'warning')
                return redirect(request.url)
            
            # Read CSV and validate columns
            try:
                df_csv = pd.read_csv(csv_file_path)
                if len(df_csv) == 0:
                    flash('CSV file is empty!', 'danger')
                    return redirect(request.url)
                
                first_row = df_csv.iloc[0]
                
                # Extract all 9 required parameters
                required_columns = [
                    'rainfall_intensity', 'rainfall_duration', 'humidity', 'temperature',
                    'terrain_type', 'elevation', 'soil_type', 'drainage_capacity', 'previous_rainfall'
                ]
                
                missing_columns = [col for col in required_columns if col not in df_csv.columns]
                if missing_columns:
                    flash(f'Missing required columns: {", ".join(missing_columns)}', 'danger')
                    return redirect(request.url)
                
                # Create input_data dictionary with all parameters
                input_data = {
                    "rainfall_intensity": float(first_row.get('rainfall_intensity', 0)),
                    "rainfall_duration": float(first_row.get('rainfall_duration', 0)),
                    "humidity": float(first_row.get('humidity', 0)),
                    "temperature": float(first_row.get('temperature', 0)),
                    "terrain_type": str(first_row.get('terrain_type', 'Unknown')),
                    "elevation": float(first_row.get('elevation', 0)),
                    "soil_type": str(first_row.get('soil_type', 'Unknown')),
                    "drainage_capacity": str(first_row.get('drainage_capacity', 'Unknown')),
                    "previous_rainfall": float(first_row.get('previous_rainfall', 0))
                }
                
            except pd.errors.ParserError:
                flash('Invalid CSV format!', 'danger')
                return redirect(request.url)
            except Exception as e:
                flash(f'Error reading CSV: {str(e)}', 'danger')
                return redirect(request.url)
            
            # Predict flood risk from CSV
            print(f"Predicting flood risk from CSV: {csv_file_path}")
            flood_result, error_msg = flood_predictor.predict_from_csv(csv_file_path)
            
            if error_msg:
                print(f"Flood prediction error: {error_msg}")
                flash(f'CSV Processing Error: {error_msg}', 'danger')
                return redirect(request.url)
            
            # Extract flood prediction results
            flood_risk = flood_result['flood_risk']
            flood_confidence = flood_result['confidence']
            flood_probabilities = flood_result.get('probabilities', {})
            
            print(f"Flood prediction: {flood_risk} (confidence: {flood_confidence:.2%})")
            
            # Get cloudburst result: Check query parameter first, then database
            cloudburst_from_query = request.args.get('cloudburst')
            if cloudburst_from_query:
                cloudburst_result = cloudburst_from_query
                print(f"Using cloudburst from query parameter: {cloudburst_result}")
            else:
                cloudburst_result = get_latest_cloudburst()
                print(f"Using latest cloudburst from database: {cloudburst_result}")
            
            # Multistage decision logic
            combined_result = combine_alerts(cloudburst_result, flood_risk, flood_confidence)
            print(f"Combined alert: {combined_result['final_alert']}")
            
            # Save prediction to database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Store comprehensive flood prediction record
            cursor.execute('''
                INSERT INTO flood_predictions 
                (user_id, rainfall, humidity, temperature, flood_risk, flood_confidence, 
                 cloudburst_result, final_alert, alert_level, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'],
                input_data['rainfall_intensity'],
                input_data['humidity'],
                input_data['temperature'],
                flood_risk,
                float(flood_confidence),
                cloudburst_result,
                combined_result['final_alert'],
                combined_result['alert_level'],
                now
            ))
            
            conn.commit()
            conn.close()
            
            print(f"Prediction saved to database")
            
            # Send emergency alert email based on new logic:
            # 1. If cloudburst detected → send email (mention cloudburst) for ANY risk level
            # 2. If cloudburst NOT detected + High/Medium risk → send email (don't mention cloudburst)
            # 3. If cloudburst NOT detected + Low risk → no email
            email_sent = False
            
            if cloudburst_result == "Cloud Burst":
                # Always send email if cloudburst is detected (High, Medium, or Low)
                email_sent = send_alert_email(
                    session['email'],
                    flood_risk=flood_risk,
                    cloudburst_result=cloudburst_result,
                    confidence=flood_confidence,
                    mention_cloudburst=True
                )
                print(f"🚨 Alert email sent: Cloudburst detected with {flood_risk} flood risk")
            elif flood_risk in ["High", "Medium"]:
                # Send email for High/Medium flood risk without mentioning cloudburst
                email_sent = send_alert_email(
                    session['email'],
                    flood_risk=flood_risk,
                    cloudburst_result=None,
                    confidence=flood_confidence,
                    mention_cloudburst=False
                )
                print(f"⚠️ Alert email sent: {flood_risk} flood risk detected (no cloudburst)")
            # else: No email for Low risk without cloudburst
            
            if email_sent:
                print(f"Alert email sent to {session['email']}")
            else:
                print(f"No email sent - conditions not met (cloudburst: {cloudburst_result}, flood_risk: {flood_risk})")
            
            # Prepare probability display
            prob_display = {k: v for k, v in flood_probabilities.items()}
            
            # Return results with input_data
            return render_template('flood_result.html',
                                  flood_risk=flood_risk,
                                  flood_confidence=flood_confidence,
                                  flood_probabilities=prob_display,
                                  cloudburst_result=cloudburst_result,
                                  final_alert=combined_result['final_alert'],
                                  alert_level=combined_result['alert_level'],
                                  details=combined_result['description'],
                                  input_data=input_data,
                                  timestamp=now)
        
        except Exception as e:
            print(f"Exception in upload_csv: {str(e)}")
            flash(f'Error processing file: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('upload_csv.html')


@app.route('/flood_prediction', methods=['GET', 'POST'])
def flood_prediction():
    """
    Alias route for /upload_csv - provides flash flood prediction service
    Accepts CSV uploads with 9 environmental features
    """
    return upload_csv()

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out!', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)