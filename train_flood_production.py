"""
Production-Level Flash Flood Prediction Model Training
Trains RandomForestClassifier with 9 comprehensive environmental features
Proper categorical encoding and comprehensive validation
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support
import pickle
import os
import warnings

warnings.filterwarnings('ignore')

# ======================== CONFIGURATION ========================
MODEL_SAVE_PATH = 'models/flood_model.pkl'
LABEL_ENCODER_TARGET_PATH = 'models/flood_label_encoder_target.pkl'
CATEGORICAL_ENCODER_PATH = 'models/flood_categorical_encoders.pkl'
FEATURE_NAMES_PATH = 'models/flood_feature_names.pkl'
ENCODING_MAPPINGS_PATH = 'models/flood_encoding_mappings.pkl'

# Features Configuration
CATEGORICAL_FEATURES = ['terrain_type', 'soil_type', 'drainage_capacity']
NUMERICAL_FEATURES = ['rainfall_intensity', 'rainfall_duration', 'humidity', 
                      'temperature', 'elevation', 'previous_rainfall']
TARGET_COLUMN = 'flood_risk'
REQUIRED_COLUMNS = CATEGORICAL_FEATURES + NUMERICAL_FEATURES + [TARGET_COLUMN]


def load_and_prepare_data(csv_path):
    """Load dataset and validate required columns"""
    print(f"\n{'='*70}")
    print("STEP 1: LOADING AND PREPARING DATA")
    print(f"{'='*70}")
    print(f"Loading dataset from {csv_path}...")
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✓ Dataset loaded successfully")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        
        # Check for required columns
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        print(f"✓ All required columns present")
        
        # Handle missing values
        print(f"\nDataset Statistics:")
        print(f"  Total records: {len(df)}")
        
        missing_values = df[REQUIRED_COLUMNS].isnull().sum()
        if missing_values.any():
            print(f"  Removing rows with missing values...")
            df = df.dropna(subset=REQUIRED_COLUMNS)
            print(f"  Dataset shape after removing NaN: {df.shape}")
        
        # Display target distribution
        print(f"\nTarget Distribution ({TARGET_COLUMN}):")
        target_dist = df[TARGET_COLUMN].value_counts()
        for label, count in target_dist.items():
            print(f"  {label}: {count} ({count/len(df)*100:.2f}%)")
        
        # Display categorical features
        print(f"\nCategorical Features Distribution:")
        for cat_feature in CATEGORICAL_FEATURES:
            print(f"  {cat_feature}: {list(df[cat_feature].unique())}")
        
        # Display numerical features statistics
        print(f"\nNumerical Features Statistics:")
        print(df[NUMERICAL_FEATURES].describe().T)
        
        return df
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {csv_path}")
    except Exception as e:
        raise Exception(f"Error loading dataset: {str(e)}")


def split_dataset(df):
    """Split dataset into train and test sets"""
    print(f"\n{'='*70}")
    print("STEP 2: SPLITTING DATASET")
    print(f"{'='*70}")
    
    X = df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES]
    y = df[TARGET_COLUMN]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"✓ Dataset split completed (80% train, 20% test)")
    print(f"  Training set: {X_train.shape[0]} samples")
    print(f"  Test set: {X_test.shape[0]} samples")
    
    return X_train, X_test, y_train, y_test


def encode_categorical_features(X_train, X_test):
    """Encode categorical features using OneHotEncoder"""
    print(f"\n{'='*70}")
    print("STEP 3: ENCODING CATEGORICAL FEATURES")
    print(f"{'='*70}")
    
    # Use OneHotEncoder for categorical features
    categorical_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    
    # Fit on training data and transform both
    X_train_cat = categorical_encoder.fit_transform(X_train[CATEGORICAL_FEATURES])
    X_test_cat = categorical_encoder.transform(X_test[CATEGORICAL_FEATURES])
    
    # Get encoded feature names
    encoded_cat_names = categorical_encoder.get_feature_names_out(CATEGORICAL_FEATURES)
    
    # Combine numerical and encoded categorical features
    X_train_numerical = X_train[NUMERICAL_FEATURES].values
    X_test_numerical = X_test[NUMERICAL_FEATURES].values
    
    X_train_encoded = np.hstack([X_train_numerical, X_train_cat])
    X_test_encoded = np.hstack([X_test_numerical, X_test_cat])
    
    # Create feature names list
    feature_names = list(NUMERICAL_FEATURES) + list(encoded_cat_names)
    
    print(f"✓ Categorical features encoded using OneHotEncoder")
    print(f"  Numerical features: {len(NUMERICAL_FEATURES)}")
    print(f"  Encoded categorical features: {len(encoded_cat_names)}")
    print(f"  Total features: {len(feature_names)}")
    
    print(f"\nAll feature names:")
    for i, fname in enumerate(feature_names, 1):
        print(f"  {i:2d}. {fname}")
    
    return X_train_encoded, X_test_encoded, categorical_encoder, feature_names


def encode_target(y_train, y_test):
    """Encode target variable from strings to integers"""
    print(f"\n{'='*70}")
    print("STEP 4: ENCODING TARGET VARIABLE")
    print(f"{'='*70}")
    
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    y_test_encoded = label_encoder.transform(y_test)
    
    print(f"✓ Target variable encoded")
    print(f"Label encoding mapping:")
    for i, label in enumerate(label_encoder.classes_):
        print(f"  {label} -> {i}")
    
    return y_train_encoded, y_test_encoded, label_encoder


def train_random_forest(X_train, y_train, X_test, y_test):
    """Train RandomForestClassifier with 200 estimators and tuned max_depth"""
    print(f"\n{'='*70}")
    print("STEP 5: TRAINING RANDOM FOREST CLASSIFIER")
    print(f"{'='*70}")
    
    print(f"\nInitializing model with hyperparameters:")
    print(f"  n_estimators: 200")
    print(f"  max_depth: 15")
    print(f"  min_samples_split: 5")
    print(f"  min_samples_leaf: 2")
    print(f"  random_state: 42")
    
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    print(f"\nTraining model...")
    model.fit(X_train, y_train)
    print(f"✓ Model training completed!")
    
    return model


def evaluate_model(model, X_train, y_train, X_test, y_test, label_encoder, feature_names):
    """Evaluate model performance on training and test sets"""
    print(f"\n{'='*70}")
    print("STEP 6: MODEL EVALUATION")
    print(f"{'='*70}")
    
    # Training performance
    y_train_pred = model.predict(X_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    print(f"\nTraining Set Performance:")
    print(f"  Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
    
    # Test performance
    y_test_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    
    print(f"\nTest Set Performance:")
    print(f"  Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    
    # Detailed classification report
    print(f"\nClassification Report:")
    print(classification_report(
        y_test, y_test_pred,
        target_names=label_encoder.classes_,
        digits=4
    ))
    
    # Confusion matrix
    print(f"\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_test_pred)
    print(cm)
    
    # Per-class metrics
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_test_pred, labels=np.unique(y_test)
    )
    
    print(f"\nPer-Class Metrics:")
    for i, label in enumerate(label_encoder.classes_):
        print(f"  {label}:")
        print(f"    Precision: {precision[i]:.4f}")
        print(f"    Recall: {recall[i]:.4f}")
        print(f"    F1-Score: {f1[i]:.4f}")
        print(f"    Support: {support[i]}")
    
    # Cross-validation
    print(f"\nPerforming 5-Fold Cross-Validation...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    print(f"  CV Scores: {[f'{score:.4f}' for score in cv_scores]}")
    print(f"  Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Feature importance
    print(f"\nTop 10 Feature Importance:")
    importance_data = list(zip(feature_names, model.feature_importances_))
    importance_data.sort(key=lambda x: x[1], reverse=True)
    for i, (fname, importance) in enumerate(importance_data[:10], 1):
        print(f"  {i:2d}. {fname}: {importance:.4f}")
    
    return test_accuracy


def save_artifacts(model, label_encoder, categorical_encoder, feature_names):
    """Save model and all encoders to disk"""
    print(f"\n{'='*70}")
    print("STEP 7: SAVING MODEL ARTIFACTS")
    print(f"{'='*70}")
    
    # Create models directory if needed
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH) if os.path.dirname(MODEL_SAVE_PATH) else '.', exist_ok=True)
    
    # Save model
    with open(MODEL_SAVE_PATH, 'wb') as f:
        pickle.dump(model, f)
    print(f"✓ Model saved to {MODEL_SAVE_PATH}")
    
    # Save target label encoder
    with open(LABEL_ENCODER_TARGET_PATH, 'wb') as f:
        pickle.dump(label_encoder, f)
    print(f"✓ Target label encoder saved to {LABEL_ENCODER_TARGET_PATH}")
    
    # Save categorical encoder
    with open(CATEGORICAL_ENCODER_PATH, 'wb') as f:
        pickle.dump(categorical_encoder, f)
    print(f"✓ Categorical encoder saved to {CATEGORICAL_ENCODER_PATH}")
    
    # Save feature names
    with open(FEATURE_NAMES_PATH, 'wb') as f:
        pickle.dump(feature_names, f)
    print(f"✓ Feature names saved to {FEATURE_NAMES_PATH}")
    
    # Save encoding mappings reference
    encoding_mappings = {
        'categorical_features': CATEGORICAL_FEATURES,
        'numerical_features': NUMERICAL_FEATURES,
        'target_column': TARGET_COLUMN,
        'target_classes': list(label_encoder.classes_),
        'feature_names': feature_names
    }
    with open(ENCODING_MAPPINGS_PATH, 'wb') as f:
        pickle.dump(encoding_mappings, f)
    print(f"✓ Encoding mappings reference saved to {ENCODING_MAPPINGS_PATH}")


def main():
    """Main training pipeline"""
    print(f"\n{'='*70}")
    print("FLASH FLOOD PREDICTION MODEL - PRODUCTION TRAINING")
    print(f"{'='*70}")
    
    try:
        # Step 1: Load data
        df = load_and_prepare_data('flood_training_dataset.csv')
        
        # Step 2: Split data
        X_train, X_test, y_train, y_test = split_dataset(df)
        
        # Step 3: Encode categorical features
        X_train_encoded, X_test_encoded, categorical_encoder, feature_names = encode_categorical_features(X_train, X_test)
        
        # Step 4: Encode target
        y_train_encoded, y_test_encoded, label_encoder = encode_target(y_train, y_test)
        
        # Step 5: Train model
        model = train_random_forest(X_train_encoded, y_train_encoded, X_test_encoded, y_test_encoded)
        
        # Step 6: Evaluate model
        test_accuracy = evaluate_model(model, X_train_encoded, y_train_encoded, 
                                      X_test_encoded, y_test_encoded, label_encoder, feature_names)
        
        # Step 7: Save artifacts
        save_artifacts(model, label_encoder, categorical_encoder, feature_names)
        
        # Summary
        print(f"\n{'='*70}")
        print("TRAINING SUMMARY")
        print(f"{'='*70}")
        print(f"✓ Model training completed successfully!")
        print(f"  Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
        print(f"  Model saved: {MODEL_SAVE_PATH}")
        print(f"  Ready for production deployment!")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n{'='*70}")
        print("ERROR DURING TRAINING")
        print(f"{'='*70}")
        print(f"✗ Error: {str(e)}")
        print(f"{'='*70}\n")
        raise


if __name__ == '__main__':
    main()
