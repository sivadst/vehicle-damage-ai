import cv2
import numpy as np
import tensorflow as tf
from PIL import Image

def preprocess_image(image_file, target_size=(224, 224)):
    """
    Reads an uploaded file (PIL Image), resizes it, and applies EfficientNet preprocessing.
    """
    img = Image.open(image_file).convert('RGB')
    
    # Auto-resize if too large, max 1200px preserving aspect ratio
    max_dim = 1200
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    display_img = np.array(img)
    
    # Model input
    model_img = img.resize(target_size)
    model_img = np.array(model_img)
    model_img = tf.keras.applications.efficientnet.preprocess_input(model_img)
    model_img = np.expand_dims(model_img, axis=0)
    
    return display_img, model_img

def overlay_heatmap(img_arr, heatmap, alpha=0.4, colormap=cv2.COLORMAP_JET):
    """
    Overlays a Grad-CAM heatmap on the original image.
    """
    # Resize heatmap to match image
    heatmap = cv2.resize(heatmap, (img_arr.shape[1], img_arr.shape[0]))
    
    # Convert heatmap to RGB
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, colormap)
    
    # Overlay
    superimposed_img = cv2.addWeighted(heatmap, alpha, img_arr, 1 - alpha, 0)
    
    return superimposed_img, heatmap
