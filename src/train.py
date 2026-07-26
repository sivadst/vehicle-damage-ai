import os
import argparse
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard

from src.model import build_multitask_model

# Constants
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 30
DATA_DIR = Path("data/synthetic")
METADATA_PATH = DATA_DIR / "metadata.csv"
MODEL_DIR = Path("models")

CLASSES = ["no_damage", "scratch", "dent", "broken_glass", "broken_lamp", "crushed_panel"]
SEVERITIES = ["minor", "moderate", "severe"]
LOCATIONS = ["front", "rear", "side", "roof", "multiple", "none"]

def load_data():
    """Loads metadata and splits into train/val/test."""
    df = pd.read_csv(METADATA_PATH)
    
    # Map classes to integers
    df['damage_type_idx'] = df['damage_type'].map(lambda x: CLASSES.index(x))
    df['severity_idx'] = df['severity'].map(lambda x: SEVERITIES.index(x))
    df['location_idx'] = df['location'].map(lambda x: LOCATIONS.index(x))
    
    df['filepath'] = df.apply(lambda row: str(DATA_DIR / row['damage_type'] / row['filename']), axis=1)
    
    train_df, test_df = train_test_split(df, test_size=0.15, stratify=df['damage_type'], random_state=42)
    train_df, val_df = train_test_split(train_df, test_size=0.15 / 0.85, stratify=train_df['damage_type'], random_state=42)
    
    return train_df, val_df, test_df

class MultiTaskDataGenerator(tf.keras.utils.Sequence):
    """Custom Data Generator for Multi-Output Model."""
    def __init__(self, df, batch_size=32, img_size=(224, 224), augment=False, shuffle=True):
        self.df = df
        self.batch_size = batch_size
        self.img_size = img_size
        self.augment = augment
        self.shuffle = shuffle
        self.indices = np.arange(len(self.df))
        
        self.datagen = ImageDataGenerator(
            rotation_range=15,
            width_shift_range=0.1,
            height_shift_range=0.1,
            brightness_range=[0.8, 1.2],
            horizontal_flip=True,
            zoom_range=[0.9, 1.1],
            shear_range=10
        ) if augment else ImageDataGenerator()
        
        if self.shuffle:
            np.random.shuffle(self.indices)

    def __len__(self):
        return int(np.ceil(len(self.df) / self.batch_size))

    def __getitem__(self, index):
        batch_indices = self.indices[index * self.batch_size:(index + 1) * self.batch_size]
        batch_df = self.df.iloc[batch_indices]
        
        X = np.zeros((len(batch_df), *self.img_size, 3), dtype=np.float32)
        y_damage = np.zeros((len(batch_df), len(CLASSES)), dtype=np.float32)
        y_severity = np.zeros((len(batch_df), len(SEVERITIES)), dtype=np.float32)
        y_location = np.zeros((len(batch_df), len(LOCATIONS)), dtype=np.float32)
        
        for i, (_, row) in enumerate(batch_df.iterrows()):
            # Read and process image using TensorFlow
            img_path = row['filepath']
            img = tf.io.read_file(img_path)
            img = tf.image.decode_jpeg(img, channels=3)
            img = tf.image.resize(img, self.img_size)
            
            # Convert to numpy for ImageDataGenerator augmentation (optional, but easier)
            img_np = img.numpy()
            
            if self.augment:
                # Need to add batch dim for datagen
                img_np = self.datagen.random_transform(img_np)
                
            # EfficientNetB3 in tf.keras.applications expects inputs in [0, 255] for default preprocess_input
            # but usually it's built in. Let's just pass [0, 255] and let EfficientNet handle it.
            # Actually, the built-in model expects values in [-1, 1] or [0, 255] depending on implementation.
            # We will use tf.keras.applications.efficientnet.preprocess_input
            img_np = tf.keras.applications.efficientnet.preprocess_input(img_np)
            
            X[i] = img_np
            
            # One-hot encoding
            y_damage[i, row['damage_type_idx']] = 1.0
            y_severity[i, row['severity_idx']] = 1.0
            y_location[i, row['location_idx']] = 1.0
            
        return X, {"damage_type": y_damage, "severity": y_severity, "location": y_location}

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)


def train(demo_mode=False):
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs("outputs/logs", exist_ok=True)
    
    print("Loading data...")
    train_df, val_df, test_df = load_data()
    
    print(f"Train samples: {len(train_df)}, Val samples: {len(val_df)}")
    
    if demo_mode:
        print("🟡 DEMO MODE: Training for 1 epoch on a tiny subset to generate mock weights...")
        train_df = train_df.head(BATCH_SIZE * 2)
        val_df = val_df.head(BATCH_SIZE)
        epochs = 1
    else:
        epochs = EPOCHS
        
    train_gen = MultiTaskDataGenerator(train_df, batch_size=BATCH_SIZE, augment=True)
    val_gen = MultiTaskDataGenerator(val_df, batch_size=BATCH_SIZE, augment=False, shuffle=False)
    
    model = build_multitask_model(num_damage_classes=len(CLASSES), num_severity_classes=len(SEVERITIES), num_location_classes=len(LOCATIONS))
    
    callbacks = [
        EarlyStopping(patience=5, restore_best_weights=True, monitor='val_loss'),
        ReduceLROnPlateau(factor=0.5, patience=3, min_lr=1e-6, monitor='val_loss'),
        ModelCheckpoint(filepath=str(MODEL_DIR / 'efficientnet_b3_damage.h5'), save_best_only=True, monitor='val_loss'),
        TensorBoard(log_dir="outputs/logs")
    ]
    
    print("Starting training...")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs,
        callbacks=callbacks
    )
    
    # Save the final model (in case ModelCheckpoint didn't save the very last one, or for demo mode)
    if demo_mode:
        model.save(str(MODEL_DIR / 'efficientnet_b3_damage.h5'))
        print("🟡 DEMO MODE: Initial mock weights saved to models/efficientnet_b3_damage.h5")
    else:
        print("Training complete. Best model saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo-mode', action='store_true', help='Run 1 epoch on tiny subset for demo initialization.')
    args = parser.parse_args()
    
    train(demo_mode=args.demo_mode)
