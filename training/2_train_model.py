import numpy as np
import joblib
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

def train_model():
    print("=== GESTURE RECOGNITION MODEL TRAINING ===")
    
    # Load processed data
    try:
        data = joblib.load('training/models/processed_dataset.pkl')
        X = data['features']
        y = data['labels']
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("Run 1_process_dataset.py first!")
        return
    
    print(f"📊 Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"🎯 Classes: {np.unique(y)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📚 Training samples: {len(X_train)}")
    print(f"🧪 Testing samples: {len(X_test)}")
    
    # Train Random Forest
    print("\n🤖 Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=3,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*60}")
    print(f"🎉 TRAINING COMPLETE!")
    print(f"{'='*60}")
    print(f"📈 Accuracy: {accuracy:.1%}")
    print(f"🧪 Test samples: {len(X_test)}")
    
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print("📊 Confusion Matrix:")
    print(cm)
    
    # Feature importance
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        print(f"\n💪 Feature importance range: {importance.min():.6f} to {importance.max():.6f}")
        print(f"🔝 Top 5 most important features:")
        top_indices = np.argsort(importance)[-5:][::-1]
        for i, idx in enumerate(top_indices):
            print(f"   {i+1}. Feature {idx}: {importance[idx]:.6f}")
    
    # Save model to realtime directory
    os.makedirs('../realtime', exist_ok=True)
    model_path = '../realtime/gesture_model.pkl'
    joblib.dump(model, model_path)
    print(f"\n💾 Model saved to: {model_path}")
    
    # Also save to training/models for backup
    backup_path = 'training/models/gesture_model.pkl'
    joblib.dump(model, backup_path)
    print(f"💾 Backup saved to: {backup_path}")
    
    # Test loading the model to verify
    try:
        test_model = joblib.load(model_path)
        print("✅ Model verification: Successfully loaded from realtime directory")
    except Exception as e:
        print(f"❌ Model verification failed: {e}")
    
    return accuracy

if __name__ == "__main__":
    train_model()