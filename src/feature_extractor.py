import os
import pickle
import numpy as np
import tensorflow as tf
from pathlib import Path
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

from src.train import load_data, CLASSES, SEVERITIES, LOCATIONS

MODEL_DIR = Path("models")

def build_feature_extractor(model):
    """Creates a sub-model that outputs features from the global average pooling layer."""
    # EfficientNet-B3 uses 'global_average_pooling' layer name in our build function
    layer_name = 'global_average_pooling'
    return tf.keras.Model(inputs=model.input, outputs=model.get_layer(layer_name).output)

def extract_features(df, extractor, batch_size=32, img_size=(224, 224)):
    """Extracts features for all images in the dataframe."""
    features = []
    
    for i in tqdm(range(0, len(df), batch_size)):
        batch_df = df.iloc[i:i+batch_size]
        X = np.zeros((len(batch_df), *img_size, 3), dtype=np.float32)
        
        for j, (_, row) in enumerate(batch_df.iterrows()):
            img_path = row['filepath']
            img = tf.io.read_file(img_path)
            img = tf.image.decode_jpeg(img, channels=3)
            img = tf.image.resize(img, img_size)
            img_np = img.numpy()
            img_np = tf.keras.applications.efficientnet.preprocess_input(img_np)
            X[j] = img_np
            
        batch_features = extractor.predict(X, verbose=0)
        features.append(batch_features)
        
    return np.vstack(features)

def create_knn_index():
    print("Loading test data...")
    train_df, _, _ = load_data()
    
    print("Loading model...")
    model_path = MODEL_DIR / 'efficientnet_b3_damage.h5'
    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        return
        
    model = tf.keras.models.load_model(str(model_path))
    extractor = build_feature_extractor(model)
    
    print("Extracting features from training set...")
    features = extract_features(train_df, extractor)
    
    print("Building KNN index...")
    # Using cosine similarity is typical for embeddings
    knn = NearestNeighbors(n_neighbors=3, metric='cosine')
    knn.fit(features)
    
    print("Saving KNN index and metadata...")
    index_data = {
        'knn': knn,
        'metadata': train_df[['filepath', 'damage_type', 'severity']].to_dict('records')
    }
    
    with open(str(MODEL_DIR / 'feature_index.pkl'), 'wb') as f:
        pickle.dump(index_data, f)
        
    print("KNN Index saved successfully.")

if __name__ == "__main__":
    create_knn_index()
