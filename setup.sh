#!/bin/bash
echo "Setting up Vehicle Damage AI Environment..."

# Install dependencies
pip install -r requirements.txt

# Run synthetic data generation if we don't have enough images (just a quick check on the 'dent' folder)
if [ ! -d "data/synthetic/dent" ] || [ $(ls data/synthetic/dent | wc -l) -eq 0 ]; then
    echo "Generating synthetic dataset..."
    python src/data_pipeline.py
else
    echo "Synthetic dataset already found."
fi

# Run the training script (in 1-epoch mode to generate mock weights)
echo "Generating initial weights..."
python -m src.train --demo-mode

echo "Generating KNN index..."
python -m src.feature_extractor

echo "Setup complete! Run 'streamlit run app/main.py' to launch the app."
