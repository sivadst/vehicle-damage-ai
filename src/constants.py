# ========================================
# Vehicle Damage AI - Shared Constants
# ========================================
# Extracted so modules can import these without
# triggering heavy TensorFlow imports.

IMG_SIZE = (224, 224)

CLASSES = ["no_damage", "scratch", "dent", "broken_glass", "broken_lamp", "crushed_panel"]
SEVERITIES = ["minor", "moderate", "severe"]
LOCATIONS = ["front", "rear", "side", "roof", "multiple", "none"]
