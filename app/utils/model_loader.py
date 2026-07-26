import streamlit as st
from pathlib import Path
import pickle

try:
    import tensorflow as tf
    HAS_TF = True
except ImportError:
    HAS_TF = False

MODEL_DIR = Path("models")

@st.cache_resource
def load_cached_model():
    if not HAS_TF:
        st.error("TensorFlow is not installed. Real inference requires TensorFlow. Use Demo Mode instead.")
        return None
    model_path = MODEL_DIR / 'efficientnet_b3_damage.h5'
    try:
        model = tf.keras.models.load_model(str(model_path))
        return model
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None

@st.cache_resource
def load_knn_index():
    index_path = MODEL_DIR / 'feature_index.pkl'
    try:
        with open(str(index_path), 'rb') as f:
            data = pickle.load(f)
        return data['knn'], data['metadata']
    except Exception as e:
        st.error(f"Failed to load KNN index: {e}")
        return None, None
