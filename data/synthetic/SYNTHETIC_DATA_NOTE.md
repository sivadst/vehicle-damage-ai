# Synthetic Data Note

This folder contains **synthetically generated data** using OpenCV. 

It was created specifically for demonstration and testing purposes in environments where downloading massive, authenticated real-world datasets (like from Kaggle or proprietary insurance databases) is not feasible or authorized.

The data generation script (`src/data_pipeline.py`) overlays procedural damage textures (scratches, dents, shattered glass, crushed panels) onto mock vehicle base images.

## Production Note
In a real production environment, this dataset would be replaced by high-quality, human-annotated vehicle damage images from insurance claims or body shop databases. 

The pipeline architecture (training, focal loss, Grad-CAM++, Streamlit UI) remains exactly the same; only the raw input source changes.
