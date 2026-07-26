import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from src.train import load_data, MultiTaskDataGenerator, CLASSES, SEVERITIES, LOCATIONS

MODEL_DIR = Path("models")

def evaluate_model():
    print("Loading test data...")
    _, _, test_df = load_data()
    test_gen = MultiTaskDataGenerator(test_df, batch_size=32, augment=False, shuffle=False)
    
    print("Loading model...")
    model_path = MODEL_DIR / 'efficientnet_b3_damage.h5'
    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        return
        
    model = tf.keras.models.load_model(str(model_path))
    
    print("Running inference on test set...")
    predictions = model.predict(test_gen)
    
    y_pred_damage = np.argmax(predictions[0], axis=1)
    y_pred_severity = np.argmax(predictions[1], axis=1)
    y_pred_location = np.argmax(predictions[2], axis=1)
    
    # Get ground truth
    y_true_damage = test_df['damage_type_idx'].values
    y_true_severity = test_df['severity_idx'].values
    y_true_location = test_df['location_idx'].values
    
    print("\n--- Damage Type Classification Report ---")
    print(classification_report(y_true_damage, y_pred_damage, target_names=CLASSES, zero_division=0))
    
    print("\n--- Severity Classification Report ---")
    print(classification_report(y_true_severity, y_pred_severity, target_names=SEVERITIES, zero_division=0))
    
    # Save confusion matrices
    os.makedirs("outputs", exist_ok=True)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(confusion_matrix(y_true_damage, y_pred_damage), annot=True, fmt='d', cmap='Blues', xticklabels=CLASSES, yticklabels=CLASSES)
    plt.title("Damage Type Confusion Matrix")
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.savefig("outputs/confusion_matrix_damage.png")
    plt.close()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(confusion_matrix(y_true_severity, y_pred_severity), annot=True, fmt='d', cmap='Blues', xticklabels=SEVERITIES, yticklabels=SEVERITIES)
    plt.title("Severity Confusion Matrix")
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.savefig("outputs/confusion_matrix_severity.png")
    plt.close()
    
    print("Evaluation complete. Confusion matrices saved to outputs/.")

if __name__ == "__main__":
    import os
    evaluate_model()
