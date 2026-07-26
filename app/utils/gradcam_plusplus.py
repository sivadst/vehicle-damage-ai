import numpy as np
import tensorflow as tf
import cv2

def apply_gradcam_plusplus(model, img_array, class_index, layer_name='top_conv'):
    """
    Generates Grad-CAM++ heatmap for a specific class.
    Args:
        model: tf.keras.Model
        img_array: Preprocessed input image (1, 224, 224, 3)
        class_index: Target class index to generate the explanation for.
        layer_name: The last convolutional layer name.
    Returns:
        heatmap: 2D numpy array [0, 1]
    """
    grad_model = tf.keras.models.Model(
        [model.inputs], 
        [model.get_layer(layer_name).output, model.output[0]] # index 0 is damage_type
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        loss = predictions[:, class_index]

    # First derivative
    grads = tape.gradient(loss, conv_outputs)
    
    # Grad-CAM++ formulas
    # 2nd derivative: (just squaring the grads for ReLU activation as approximation)
    first_derivative = tf.exp(loss)[0] * grads
    second_derivative = tf.exp(loss)[0] * grads * grads
    third_derivative = tf.exp(loss)[0] * grads * grads * grads

    global_sum = tf.reduce_sum(conv_outputs, axis=(0, 1, 2))
    
    alpha_num = second_derivative
    alpha_denom = second_derivative * 2.0 + third_derivative * global_sum
    # Add epsilon to prevent division by zero
    alpha_denom = tf.where(alpha_denom != 0.0, alpha_denom, tf.ones_like(alpha_denom))
    
    alphas = alpha_num / alpha_denom
    
    weights = tf.maximum(first_derivative, 0.0)
    alpha_normalization_constant = tf.reduce_sum(alphas, axis=(0,1))
    alphas /= alpha_normalization_constant
    
    deep_linearization_weights = tf.reduce_sum(weights * alphas, axis=(0, 1))

    heatmap = tf.reduce_sum(tf.multiply(deep_linearization_weights, conv_outputs[0]), axis=-1)
    
    # ReLU on heatmap
    heatmap = tf.maximum(heatmap, 0)
    
    # Normalize
    heatmap /= tf.reduce_max(heatmap) + tf.keras.backend.epsilon()
    
    return heatmap.numpy()
