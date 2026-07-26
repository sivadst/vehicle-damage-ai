import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization, Input
from tensorflow.keras.models import Model
import tensorflow.keras.backend as K

def build_multitask_model(input_shape=(224, 224, 3), num_damage_classes=6, num_severity_classes=3, num_location_classes=5, learning_rate=1e-4):
    """
    Builds a Multi-Task EfficientNet-B3 model for Damage Type, Severity, and Location classification.
    
    Args:
        input_shape (tuple): Shape of the input images.
        num_damage_classes (int): Number of damage type classes.
        num_severity_classes (int): Number of severity classes.
        num_location_classes (int): Number of location classes.
        learning_rate (float): Initial learning rate for Adam optimizer.
        
    Returns:
        Model: Compiled Keras model.
    """
    
    # Input Layer
    inputs = Input(shape=input_shape, name="input_image")
    
    # Backbone
    base_model = EfficientNetB3(
        include_top=False, 
        weights='imagenet', 
        input_tensor=inputs
    )
    
    # Freeze the first half of the base model to preserve general features
    for layer in base_model.layers[:len(base_model.layers) // 2]:
        layer.trainable = False

    # Extract features
    x = base_model.output
    x = GlobalAveragePooling2D(name='global_average_pooling')(x)
    x = BatchNormalization()(x)
    
    # Branch 1: Damage Type Head (Focal Loss will be used during compile if desired, using categorical for now)
    d = Dense(256, activation='relu', name='damage_dense_1')(x)
    d = Dropout(0.4)(d)
    damage_output = Dense(num_damage_classes, activation='softmax', name='damage_type')(d)
    
    # Branch 2: Severity Head
    s = Dense(128, activation='relu', name='severity_dense_1')(x)
    s = Dropout(0.3)(s)
    severity_output = Dense(num_severity_classes, activation='softmax', name='severity')(s)
    
    # Branch 3: Location Head
    l = Dense(128, activation='relu', name='location_dense_1')(x)
    l = Dropout(0.3)(l)
    location_output = Dense(num_location_classes, activation='softmax', name='location')(l)
    
    # Combine Model
    model = Model(inputs=inputs, outputs=[damage_output, severity_output, location_output], name="VehicleDamageAI")
    
    # We will use Categorical Crossentropy for now, but in a real training loop, Focal Loss is often injected via custom loss functions.
    # We add class weights during model.fit to handle imbalance.
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss={
            'damage_type': 'categorical_crossentropy',
            'severity': 'categorical_crossentropy',
            'location': 'categorical_crossentropy'
        },
        loss_weights={
            'damage_type': 1.0,
            'severity': 0.8,
            'location': 0.5
        },
        metrics={
            'damage_type': ['accuracy'],
            'severity': ['accuracy'],
            'location': ['accuracy']
        }
    )
    
    return model

# Focal Loss Implementation for later use if needed
class FocalLoss(tf.keras.losses.Loss):
    def __init__(self, gamma=2.0, alpha=0.25, **kwargs):
        super(FocalLoss, self).__init__(**kwargs)
        self.gamma = gamma
        self.alpha = alpha

    def call(self, y_true, y_pred):
        y_pred = K.clip(y_pred, K.epsilon(), 1.0 - K.epsilon())
        cross_entropy = -y_true * K.log(y_pred)
        weight = self.alpha * K.pow(1 - y_pred, self.gamma)
        loss = weight * cross_entropy
        return K.sum(loss, axis=1)

if __name__ == "__main__":
    # Test model building
    model = build_multitask_model()
    model.summary()
