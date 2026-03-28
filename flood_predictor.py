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
        """Load trained model and all required encoders"""
        try:
            # Check if model file exists
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            # Load RandomForest model
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"✓ RandomForest model loaded from {self.model_path}")
            
            # Load target label encoder
            if not os.path.exists(self.target_encoder_path):
                raise FileNotFoundError(f"Target encoder not found: {self.target_encoder_path}")
            
            with open(self.target_encoder_path, 'rb') as f:
                self.target_encoder = pickle.load(f)
            print(f"✓ Target label encoder loaded from {self.target_encoder_path}")
            
            # Load categorical encoder (OneHotEncoder)
            if not os.path.exists(self.categorical_encoder_path):
                raise FileNotFoundError(f"Categorical encoder not found: {self.categorical_encoder_path}")
            
            with open(self.categorical_encoder_path, 'rb') as f:
                self.categorical_encoder = pickle.load(f)
            print(f"✓ Categorical encoder loaded from {self.categorical_encoder_path}")
            
            # Load feature names
            if not os.path.exists(self.feature_names_path):
                raise FileNotFoundError(f"Feature names not found: {self.feature_names_path}")
            
            with open(self.feature_names_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            print(f"✓ Feature names loaded from {self.feature_names_path}")
            print(f"  Model features: {len(self.feature_names)}")
            
        except Exception as e:
            print(f"✗ Error loading model: {e}")
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

_flood_predictor = None


def get_flood_predictor():
    """Get or create global flood predictor instance"""
    global _flood_predictor
    
    if _flood_predictor is None:
        try:
            _flood_predictor = FloodPredictor()
        except Exception as e:
            print(f"Warning: Could not initialize flood predictor: {e}")
            return None
    
    return _flood_predictor
