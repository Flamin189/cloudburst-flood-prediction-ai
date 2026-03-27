"""
Flash Flood Prediction Module
Handles model loading, prediction with all 9 features, and cloudburst integration
"""

import pickle
import os
import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime


class FloodPredictor:
    """
    Flash Flood risk prediction using RandomForestClassifier with 9 environmental features
    Integrates with cloudburst detection database for multistage decision logic
    """
    
    # Feature configuration (must match training script)
    CATEGORICAL_FEATURES = ['terrain_type', 'soil_type', 'drainage_capacity']
    NUMERICAL_FEATURES = ['rainfall_intensity', 'rainfall_duration', 'humidity', 
                          'temperature', 'elevation', 'previous_rainfall']
    ALL_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    TARGET_COLUMN = 'flood_risk'
    
    def __init__(self, model_path='models/flood_model.pkl', 
                 target_encoder_path='models/flood_label_encoder_target.pkl',
                 categorical_encoder_path='models/flood_categorical_encoders.pkl',
                 feature_names_path='models/flood_feature_names.pkl'):
        """
        Initialize flood predictor by loading trained model and encoders
        
        Args:
            model_path: Path to saved RandomForest model
            target_encoder_path: Path to target label encoder
            categorical_encoder_path: Path to categorical OneHotEncoder
            feature_names_path: Path to feature names list
        """
        self.model_path = model_path
        self.target_encoder_path = target_encoder_path
        self.categorical_encoder_path = categorical_encoder_path
        self.feature_names_path = feature_names_path
        
        self.model = None
        self.target_encoder = None
        self.categorical_encoder = None
        self.feature_names = None
        
        self.load_model()
    
    def load_model(self):
        """Load trained model and all required encoders with detailed diagnostics"""
        print(f"\n{'='*60}")
        print(f"Loading Flood Prediction Models")
        print(f"{'='*60}")
        print(f"Current working directory: {os.getcwd()}")
        
        model_files = [
            ("RandomForest Model", self.model_path),
            ("Target Label Encoder", self.target_encoder_path),
            ("Categorical Encoder", self.categorical_encoder_path),
            ("Feature Names", self.feature_names_path)
        ]
        
        # First, check all files exist
        print("\nChecking model files:")
        all_files_exist = True
        for name, path in model_files:
            abs_path = os.path.abspath(path)
            exists = os.path.exists(path)
            status = "✓" if exists else "✗"
            print(f"  {status} {name}: {path}")
            if exists:
                size = os.path.getsize(path) / (1024)  # KB
                print(f"     Size: {size:.2f} KB")
            else:
                all_files_exist = False
                print(f"     NOT FOUND: {abs_path}")
        
        if not all_files_exist:
            missing = [name for name, path in model_files if not os.path.exists(path)]
            error_msg = f"Missing model files: {', '.join(missing)}"
            print(f"\n✗ Critical: {error_msg}")
            print(f"\nDeployment checklist:")
            print(f"  1. Verify models/ directory exists in repository")
            print(f"  2. Commit all .pkl files to git")
            print(f"  3. Ensure Railway deploys from main branch with models/")
            print(f"{'='*60}\n")
            raise FileNotFoundError(error_msg)
        
        try:
            # Load RandomForest model
            print(f"\nLoading RandomForest model from {self.model_path}...")
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"✓ RandomForest model loaded")
            
            # Load target label encoder
            print(f"Loading target label encoder from {self.target_encoder_path}...")
            with open(self.target_encoder_path, 'rb') as f:
                self.target_encoder = pickle.load(f)
            print(f"✓ Target label encoder loaded")
            
            # Load categorical encoder (OneHotEncoder)
            print(f"Loading categorical encoder from {self.categorical_encoder_path}...")
            with open(self.categorical_encoder_path, 'rb') as f:
                self.categorical_encoder = pickle.load(f)
            print(f"✓ Categorical encoder loaded")
            
            # Load feature names
            print(f"Loading feature names from {self.feature_names_path}...")
            with open(self.feature_names_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            print(f"✓ Feature names loaded")
            print(f"  Total features: {len(self.feature_names)}")
            print(f"  Features: {self.feature_names[:3]}... (showing first 3)")
            
            print(f"\n✓ All flood models loaded successfully!")
            print(f"{'='*60}\n")
            
        except (pickle.PickleError, EOFError, IOError) as e:
            print(f"✗ Error loading model files: {e}")
            print(f"  Type: {type(e).__name__}")
            print(f"  Ensure model files are uncorrupted .pkl files")
            print(f"{'='*60}\n")
            raise
    
    def validate_csv_columns(self, df):
        """
        Validate that CSV has all required columns
        
        Args:
            df: Pandas DataFrame from CSV
        
        Returns:
            Tuple of (is_valid, error_message, missing_columns)
        """
        missing_columns = [col for col in self.ALL_FEATURES if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {missing_columns}", missing_columns
        
        return True, None, None
    
    def validate_data_values(self, row_data):
        """
        Validate that data values are within reasonable ranges
        
        Args:
            row_data: Dictionary with feature values
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        errors = []
        
        # Validate numerical features
        try:
            rainfall_intensity = float(row_data.get('rainfall_intensity', 0))
            if rainfall_intensity < 0 or rainfall_intensity > 300:
                errors.append("rainfall_intensity must be between 0 and 300 mm/hr")
            
            rainfall_duration = float(row_data.get('rainfall_duration', 0))
            if rainfall_duration < 0 or rainfall_duration > 48:
                errors.append("rainfall_duration must be between 0 and 48 hours")
            
            humidity = float(row_data.get('humidity', 0))
            if humidity < 0 or humidity > 100:
                errors.append("humidity must be between 0 and 100%")
            
            temperature = float(row_data.get('temperature', 0))
            if temperature < -50 or temperature > 60:
                errors.append("temperature must be between -50 and 60°C")
            
            elevation = float(row_data.get('elevation', 0))
            if elevation < 0 or elevation > 5000:
                errors.append("elevation must be between 0 and 5000 meters")
            
            previous_rainfall = float(row_data.get('previous_rainfall', 0))
            if previous_rainfall < 0 or previous_rainfall > 1000:
                errors.append("previous_rainfall must be between 0 and 1000 mm")
            
        except (ValueError, TypeError) as e:
            errors.append(f"Invalid numeric value: {str(e)}")
        
        # Validate categorical features
        terrain = str(row_data.get('terrain_type', '')).strip()
        if terrain not in ['Hilly', 'Flat', 'Urban']:
            errors.append("terrain_type must be 'Hilly', 'Flat', or 'Urban'")
        
        soil = str(row_data.get('soil_type', '')).strip()
        if soil not in ['Sandy', 'Clay', 'Loamy']:
            errors.append("soil_type must be 'Sandy', 'Clay', or 'Loamy'")
        
        drainage = str(row_data.get('drainage_capacity', '')).strip()
        if drainage not in ['Good', 'Moderate', 'Poor']:
            errors.append("drainage_capacity must be 'Good', 'Moderate', or 'Poor'")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, None
    
    def encode_features(self, df_row):
        """
        Encode categorical features and prepare feature vector
        
        Args:
            df_row: Pandas Series with one row of data
        
        Returns:
            Numpy array with encoded features or None if error
        """
        try:
            # Extract numerical features
            numerical_values = df_row[self.NUMERICAL_FEATURES].values.reshape(1, -1)
            
            # Extract and transform categorical features
            categorical_data = df_row[self.CATEGORICAL_FEATURES].values.reshape(1, -1)
            categorical_encoded = self.categorical_encoder.transform(categorical_data)
            
            # Combine numerical and encoded categorical
            features_combined = np.hstack([numerical_values, categorical_encoded])
            
            return features_combined
        
        except Exception as e:
            print(f"Error encoding features: {e}")
            return None
    
    def predict(self, df_row):
        """
        Predict flood risk for a single row
        
        Args:
            df_row: Pandas Series with features
        
        Returns:
            Tuple of (prediction_dict, error_message)
        """
        try:
            # Encode features
            X_encoded = self.encode_features(df_row)
            if X_encoded is None:
                return None, "Error encoding features"
            
            # Make prediction
            prediction_idx = self.model.predict(X_encoded)[0]
            probabilities = self.model.predict_proba(X_encoded)[0]
            
            # Decode prediction
            flood_risk = self.target_encoder.inverse_transform([prediction_idx])[0]
            
            # Get confidence (max probability)
            confidence = float(np.max(probabilities))
            
            # Create probability dictionary
            prob_dict = {
                self.target_encoder.classes_[i]: float(probabilities[i])
                for i in range(len(self.target_encoder.classes_))
            }
            
            return {
                'flood_risk': flood_risk,
                'confidence': confidence,
                'probabilities': prob_dict,
                'error': None
            }, None
        
        except Exception as e:
            return None, f"Prediction error: {str(e)}"
    
    def predict_from_csv(self, csv_file_path):
        """
        Predict flood risk from CSV file (uses first row)
        Validates all required columns and data
        
        Args:
            csv_file_path: Path to CSV file
        
        Returns:
            Tuple of (prediction_result, error_message)
            prediction_result: Dictionary with flood_risk, confidence, probabilities
            error_message: Error string if any
        """
        try:
            # Check file exists
            if not os.path.exists(csv_file_path):
                return None, f"File not found: {csv_file_path}"
            
            # Load CSV
            df = pd.read_csv(csv_file_path)
            
            # Check if file is empty
            if len(df) == 0:
                return None, "CSV file is empty"
            
            # Validate columns
            is_valid, error_msg, missing_cols = self.validate_csv_columns(df)
            if not is_valid:
                return None, error_msg
            
            # Get first row
            first_row = df.iloc[0]
            
            # Validate data values
            row_dict = first_row.to_dict()
            is_valid, error_msg = self.validate_data_values(row_dict)
            if not is_valid:
                return None, error_msg
            
            # Make prediction
            result, error_msg = self.predict(first_row)
            
            if error_msg:
                return None, error_msg
            
            return result, None
        
        except pd.errors.ParserError:
            return None, "Invalid CSV format"
        except Exception as e:
            return None, f"Error processing CSV: {str(e)}"

def fetch_latest_cloudburst_from_db(db_path='database.db'):
    """
    Fetch the MOST RECENT cloudburst prediction from database
    Uses proper SQL query: ORDER BY timestamp DESC LIMIT 1
    
    Args:
        db_path: Path to SQLite database
    
    Returns:
        Tuple of (cloudburst_result, error_message)
        cloudburst_result: 'Cloud Burst' or 'Normal Cloud' (string)
        error_message: Error message if any (None if success)
    """
    try:
        # Check if database exists
        if not os.path.exists(db_path):
            return 'Normal Cloud', f"Database not found: {db_path}"
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query for the MOST RECENT prediction
        # IMPORTANT: ORDER BY timestamp DESC LIMIT 1 to get latest entry
        cursor.execute('''
            SELECT prediction_result, timestamp
            FROM predictions
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            # No predictions in database yet
            return 'Normal Cloud', None
        
        cloudburst_result = result['prediction_result']
        timestamp = result['timestamp']
        
        print(f"✓ Fetched latest cloudburst from DB: {cloudburst_result} (timestamp: {timestamp})")
        
        return cloudburst_result, None
    
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return 'Normal Cloud', f"Database error: {str(e)}"
    except Exception as e:
        print(f"✗ Error fetching cloudburst: {e}")
        return 'Normal Cloud', f"Error fetching cloudburst: {str(e)}"


def combine_alerts(cloudburst_result, flood_risk, flood_confidence=None):
    """
    Multistage decision logic combining cloudburst and flood prediction
    
    Decision tree:
    IF cloudburst == "Cloud Burst" AND flood_risk == "High":
        final_alert = "Severe Alert 🚨"
    ELIF cloudburst == "Cloud Burst" AND flood_risk == "Medium":
        final_alert = "Warning ⚠️"
    ELIF flood_risk == "High":
        final_alert = "Potential Risk ⚠️"
    ELSE:
        final_alert = "Safe ✅"
    
    Args:
        cloudburst_result: Result from cloudburst detection ("Cloud Burst" or "Normal")
        flood_risk: Result from flood prediction ("Low", "Medium", "High")
        flood_confidence: Confidence score for flood prediction (optional)
    
    Returns:
        Dictionary with combined alert:
        {
            'final_alert': Alert message with emoji,
            'alert_level': 'Critical', 'Warning', 'Potential', or 'Safe',
            'description': Detailed explanation,
            'cloudburst_result': Cloudburst result,
            'flood_risk': Flood risk,
            'confidence': Flood prediction confidence
        }
    """
    final_alert = "Safe ✅"
    alert_level = "Safe"
    description = "No immediate threats detected"
    
    # Multistage decision logic
    if cloudburst_result == "Cloud Burst":
        if flood_risk == "High":
            # CRITICAL: Cloudburst + High Flood Risk
            final_alert = "Severe Alert 🚨"
            alert_level = "Critical"
            description = "CRITICAL: Cloudburst detected with high flood risk imminent. Evacuate immediately!"
        
        elif flood_risk == "Medium":
            # WARNING: Cloudburst + Medium Flood Risk
            final_alert = "Warning ⚠️"
            alert_level = "Warning"
            description = "WARNING: Cloudburst detected with moderate flood risk. Stay alert and prepare to evacuate."
        
        else:  # Low
            # ALERT: Cloudburst detected (even if low flood risk from other parameters)
            final_alert = "Alert 🚨"
            alert_level = "Critical"
            description = "ALERT: Cloudburst detected. Monitor situation closely."
    
    else:  # Normal cloud (no cloudburst)
        if flood_risk == "High":
            # POTENTIAL RISK: High flood risk without cloudburst
            final_alert = "Potential Risk ⚠️"
            alert_level = "Potential"
            description = "POTENTIAL RISK: High flood risk detected based on environmental conditions. Be cautious."
        
        elif flood_risk == "Medium":
            # CAUTION: Medium flood risk
            final_alert = "Caution ⚠️"
            alert_level = "Warning"
            description = "CAUTION: Moderate flood risk. Monitor weather updates."
        
        else:  # Low
            # SAFE
            final_alert = "Safe ✅"
            alert_level = "Safe"
            description = "Current conditions indicate low flood risk. Stay informed of weather updates."
    
    # Add confidence if available
    confidence_str = ""
    if flood_confidence is not None:
        confidence_pct = flood_confidence * 100
        confidence_str = f" (Model confidence: {confidence_pct:.1f}%)"
    
    return {
        'final_alert': final_alert,
        'alert_level': alert_level,
        'description': description + confidence_str,
        'cloudburst_result': cloudburst_result,
        'flood_risk': flood_risk,
        'confidence': flood_confidence
    }


# ======================== GLOBAL INSTANCE ========================

class FallbackFloodPredictor:
    """
    Fallback flood predictor using simple heuristics when ML models are unavailable
    Provides reasonable predictions based on environmental factors without trained models
    """
    
    def predict_from_csv(self, csv_path):
        """Make fallback prediction based on simple environmental rules"""
        print("⚠️ Using FALLBACK predictor (ML models unavailable)")
        
        try:
            df = pd.read_csv(csv_path)
            if len(df) == 0:
                return None, "CSV is empty"
            
            row = df.iloc[0]
            
            # Extract key parameters with safe defaults
            rainfall_intensity = float(row.get('rainfall_intensity', 0))
            rainfall_duration = float(row.get('rainfall_duration', 0))
            humidity = float(row.get('humidity', 0))
            elevation = float(row.get('elevation', 500))
            
            # Simple heuristic-based prediction
            risk_score = 0
            
            # High rainfall intensity = high risk
            if rainfall_intensity > 100:
                risk_score += 3
            elif rainfall_intensity > 50:
                risk_score += 2
            elif rainfall_intensity > 20:
                risk_score += 1
            
            # Sustained rainfall = high risk
            if rainfall_duration > 12:
                risk_score += 2
            elif rainfall_duration > 6:
                risk_score += 1
            
            # High humidity + rainfall = higher risk
            if humidity > 80 and rainfall_intensity > 30:
                risk_score += 1
            
            # Low elevation = higher risk (water flows down)
            if elevation < 200:
                risk_score += 1
            
            # Determine risk level
            if risk_score >= 5:
                flood_risk = "High"
                confidence = min(0.85, 0.5 + (risk_score * 0.1))
            elif risk_score >= 3:
                flood_risk = "Medium"
                confidence = min(0.75, 0.4 + (risk_score * 0.1))
            else:
                flood_risk = "Low"
                confidence = min(0.65, 0.3 + (risk_score * 0.1))
            
            print(f"  Fallback prediction: {flood_risk} (score: {risk_score}, confidence: {confidence:.2%})")
            
            return {
                'flood_risk': flood_risk,
                'confidence': confidence,
                'probabilities': {'Low': 1-confidence, 'Medium': 0, 'High': confidence}
            }, None
            
        except Exception as e:
            return None, f"Fallback prediction failed: {str(e)}"


_flood_predictor = None


def get_flood_predictor():
    """Get or create global flood predictor instance with fallback support"""
    global _flood_predictor
    
    if _flood_predictor is None:
        try:
            _flood_predictor = FloodPredictor()
            print("\n✓ Flood predictor loaded successfully (ML models)")
        except FileNotFoundError as e:
            print(f"\n⚠️ WARNING: Flood predictor models not found: {e}")
            print(f"   Switching to FALLBACK mode (heuristic-based predictions)")
            print(f"   Fix: Ensure models/ directory with all .pkl files is deployed to Railway")
            _flood_predictor = FallbackFloodPredictor()
        except (pickle.PickleError, EOFError) as e:
            print(f"\n⚠️ WARNING: Model file corruption detected: {e}")
            print(f"   Switching to FALLBACK mode (heuristic-based predictions)")
            _flood_predictor = FallbackFloodPredictor()
        except Exception as e:
            print(f"\n⚠️ WARNING: Unexpected error loading flood predictor: {e}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Switching to FALLBACK mode (heuristic-based predictions)")
            _flood_predictor = FallbackFloodPredictor()
    
    return _flood_predictor
