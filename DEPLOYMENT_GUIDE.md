# 🚀 Deployment Guide & Interview Q&A

This document covers how to deploy the Vehicle Damage AI application in a production environment and provides a cheat sheet for technical interviews.

## 📦 1. Deployment Strategies

### Local One-Command Launch
The simplest way to get the project running locally:
```bash
# Installs dependencies, generates data, creates mock weights
bash setup.sh

# Starts the Streamlit server
streamlit run app/main.py
```

### Docker Deployment
Containerize the application for consistent execution across environments.

**Create a `Dockerfile` (Example):**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build and Run:**
```bash
docker build -t vehicle-damage-ai .
docker run -p 8501:8501 vehicle-damage-ai
```

### Google Cloud Run Deployment
Deploy the containerized app as a serverless microservice.

```bash
# 1. Build and tag the image for Google Container Registry (GCR)
docker build -t gcr.io/[PROJECT_ID]/vehicle-damage-ai .

# 2. Push to GCR
docker push gcr.io/[PROJECT_ID]/vehicle-damage-ai

# 3. Deploy to Cloud Run
gcloud run deploy vehicle-damage-ai \
  --image gcr.io/[PROJECT_ID]/vehicle-damage-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi
```

---

## 🎙️ 2. Project Walkthrough for Interviewers

If you are presenting this project in an interview, here are 10 likely Questions and suggested Answers.

### Q1: Why did you choose EfficientNet over ResNet or VGG?
**Answer:** "EfficientNet uses a compound scaling method that balances network depth, width, and resolution. This allowed me to achieve higher accuracy with significantly fewer parameters than ResNet50, leading to faster inference times which is crucial for a real-time web application."

### Q2: Why build a Multi-Task model instead of three separate models?
**Answer:** "Training three separate models for Damage, Severity, and Location would require 3x the parameters, 3x the memory, and 3x the inference time. Because all three tasks rely on the same foundational visual features (like edges and textures of the car body), a shared backbone is highly efficient. It also creates a regularization effect where learning one task helps the others."

### Q3: How do you handle severe class imbalance? (e.g., lots of minor scratches, few crushed panels)
**Answer:** "In a production training scenario, I utilize two main strategies: 1) Strategic Data Augmentation using OpenCV (heavy rotations and perspective warps on the minority classes) and 2) Custom Loss Functions. I implemented a Focal Loss architecture which dynamically scales down the loss contribution from easy, well-classified examples (like 'no damage') and focuses the optimizer on the hard, rare examples (like 'crushed panel')."

### Q4: Why is Grad-CAM++ important here?
**Answer:** "In the insurance industry, purely 'black box' AI is heavily scrutinized. Adjusters won't blindly trust an automated approval or denial. By using Grad-CAM++, the app explicitly highlights the exact pixels (the damaged bumper, the cracked windshield) that drove the model's decision, bridging the gap between AI prediction and human verification."

### Q5: Why not use an object detection model like YOLO?
**Answer:** "YOLO is excellent for localization (drawing bounding boxes), but for initial triage, classification speed is paramount. We primarily need to know *what* the damage is and *how bad* it is. By using an EfficientNet classifier paired with Grad-CAM++, we get both the classification and a heatmap for localization at a fraction of the computational cost of a dense YOLO architecture."

### Q6: How did you ensure the Streamlit app feels 'smooth' and production-ready?
**Answer:** "Streamlit is synchronous by default, which can cause the UI to freeze during heavy ML inference or PDF generation. I solved this by injecting custom CSS for visual polish, utilizing `@st.cache_resource` so the heavy EfficientNet model only loads once into memory, and executing background tasks (like the FPDF report generation) using Python's `concurrent.futures.ThreadPoolExecutor`."

### Q7: If I uploaded an image of a dog, what would happen?
**Answer:** "Currently, the model might try to force a prediction. In a full v2 production pipeline, I would add a lightweight binary classifier (Vehicle vs. Non-Vehicle) as a gatekeeper step before passing the image to the heavy damage assessment model."

### Q8: How would you scale this to handle 10,000 requests per minute?
**Answer:** "I would decouple the frontend and backend. The Streamlit app would be replaced by a React/Next.js frontend. The model inference would be wrapped in a FastAPI backend, deployed on a Kubernetes cluster with GPU nodes, and placed behind a load balancer. We could also quantize the EfficientNet model using TensorRT to vastly speed up throughput."

### Q9: What happens if the prediction confidence is very low?
**Answer:** "The application includes a Confidence Threshold slider. If the model's confidence for any head falls below that threshold (e.g., 70%), the UI explicitly flags the prediction as 'Requires Human Review' and routes it to a manual adjuster queue rather than auto-processing it."

### Q10: How do you determine the estimated repair cost?
**Answer:** "Currently, it uses a heuristic mapping matrix based on Damage Type and Severity. In a real-world scenario, we would replace this heuristic with a secondary ML model (like XGBoost) trained on historical claims data, predicting cost based on the visual features, make/model of the car, and geographic location."
