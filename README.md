<p align="center">
  <img src="app/assets/logo.png" alt="Vehicle Damage AI Logo" width="120"/>
</p>

<h1 align="center">🚗 Vehicle Damage AI</h1>

<p align="center">
  <strong>Production-Grade Automated Vehicle Damage Assessment System</strong><br/>
  <em>Powered by Multi-Task Deep Learning & Explainable AI</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/TensorFlow-2.16+-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" alt="TensorFlow"/>
  <img src="https://img.shields.io/badge/Streamlit-1.36+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/OpenCV-4.9+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV"/>
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-blue?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/Deployment-Docker%20|%20Cloud%20Run%20|%20Streamlit%20Cloud-purple?style=flat-square" alt="Deploy"/>
</p>

<p align="center">
  <a href="https://vehicle-damage.streamlit.app"><img src="https://img.shields.io/badge/🚀_Live_Demo-vehicle--damage.streamlit.app-FF4B4B?style=for-the-badge" alt="Live Demo"/></a>
</p>

<p align="center">
  <strong>👉 <a href="https://vehicle-damage.streamlit.app">Try the Live Demo</a> 👈</strong>
</p>

---

## 🎯 The Problem

> Traditional vehicle insurance claims require **2-3 days** of manual inspection by human adjusters — a slow, expensive, and inconsistent process that frustrates both insurers and policyholders.

## 💡 The Solution

**Vehicle Damage AI** replaces the manual inspection bottleneck with a **5-second automated triage** system. Upload a vehicle image, and the AI instantly:

| Capability | Description |
|:--|:--|
| 🔍 **Damage Detection** | Classifies damage into 6 categories (scratch, dent, broken glass, broken lamp, crushed panel, no damage) |
| 📊 **Severity Assessment** | Rates severity as Minor, Moderate, or Severe with confidence scoring |
| 📍 **Location Mapping** | Identifies damage location (front, rear, side, roof, multiple) |
| 🧠 **Visual Explainability** | Generates Grad-CAM++ heatmaps showing *exactly* which pixels drove the decision |
| 💰 **Cost Estimation** | Provides instant repair cost ranges based on damage type × severity matrix |
| 📄 **PDF Reporting** | One-click professional assessment reports for claims processing |

---

### 🛡️ Image Quality & Safety Gatekeeper
Automated pre-inference image verification analyzing sharpness via **Laplacian variance** ($\sigma^2$), exposure level via luminance histograms, and minimum resolution checks before executing model inference.

### 🏗️ Multi-Task Learning Architecture
A single EfficientNet-B3 backbone with shared feature extraction branching into three specialized classification heads — achieving **3× parameter efficiency** compared to training separate models.

### 🧠 Explainable AI (Grad-CAM++) & Opacity Blending
Insurance adjusters don't trust black boxes. Our Grad-CAM++ engine generates spatial attention heatmaps with interactive opacity blending ($0.1 \rightarrow 0.9$), proving *why* predictions were made.

### ⏱️ Automated Claims Triage & Priority Scoring
Computes cost ranges, labor duration estimates (business days), and triage priorities (`P1 - Critical`, `P2 - Standard`, `P3 - Routine`).

### ⚡ Commercial SaaS UI & Session History
- Glassmorphism design with responsive CSS variables & glowing status pills
- Confidence threshold slider with automatic human-in-the-loop escalation
- Session claims history tracking and comparison
- `ThreadPoolExecutor` non-blocking PDF evidence report generation
- `@st.cache_resource` single-load model caching

### 🟡 Demo Mode
Fully functional mock-inference mode for instant demonstrations — no GPU, no dataset, no waiting. Toggle it off to run real model inference.

---

## 🏛️ Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT WEB APPLICATION                     │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Upload   │  │  Grad-CAM++  │  │  Results  │  │ PDF Report │  │
│  │  Module   │  │  Heatmaps    │  │  Display  │  │ Generator  │  │
│  └────┬─────┘  └──────┬───────┘  └────┬─────┘  └─────┬──────┘  │
│       │               │               │              │          │
│  ─────┴───────────────┴───────────────┴──────────────┴────────  │
│                    IMAGE PROCESSING PIPELINE                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               MULTI-TASK EFFICIENTNET-B3 MODEL                  │
│                                                                 │
│              ┌─────────────────────────────┐                    │
│              │  EfficientNet-B3 Backbone   │                    │
│              │   (ImageNet Pre-trained)    │                    │
│              │   50% Frozen Layers         │                    │
│              └─────────────┬───────────────┘                    │
│                            │                                    │
│              ┌─────────────┼───────────────┐                    │
│              ▼             ▼               ▼                    │
│        ┌──────────┐  ┌──────────┐  ┌──────────────┐            │
│        │ Damage   │  │ Severity │  │   Location   │            │
│        │ Type     │  │ Head     │  │    Head      │            │
│        │ Head     │  │ 128→3   │  │   128→5     │            │
│        │ 256→6   │  │          │  │              │            │
│        └──────────┘  └──────────┘  └──────────────┘            │
│                                                                 │
│  Loss: Categorical CE  │  Weights: 1.0 / 0.8 / 0.5            │
│  Optimizer: Adam (1e-4) │  Focal Loss: Available               │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SYNTHETIC DATA PIPELINE                       │
│  OpenCV-generated damage patterns over procedural car geometry  │
│  800+ images │ 6 classes │ 3 severities │ 5 locations          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|:--|:--|:--|
| **Deep Learning** | TensorFlow 2.16+, Keras | Model training & inference |
| **Backbone** | EfficientNet-B3 | Feature extraction (ImageNet transfer learning) |
| **Computer Vision** | OpenCV 4.9+ | Image processing, synthetic data generation |
| **Explainability** | Grad-CAM++ | Attention heatmap visualization |
| **Frontend** | Streamlit 1.36+ | Interactive web UI with custom CSS |
| **Visualization** | Plotly, Matplotlib, Seaborn | Charts, confusion matrices |
| **Reporting** | FPDF2 | Professional PDF assessment reports |
| **ML Utilities** | Scikit-Learn, NumPy, Pandas | Data splits, KNN retrieval, preprocessing |
| **Containerization** | Docker, Docker Compose | Production deployment |

---

## 📁 Project Structure

```text
vehicle_damage_detection/
│
├── app/                              # 🖥️  Streamlit Application
│   ├── __init__.py
│   ├── main.py                       # Application entry point
│   ├── assets/
│   │   └── logo.png                  # Application logo
│   ├── components/
│   │   ├── __init__.py
│   │   ├── style.py                  # Custom CSS (glassmorphism, animations)
│   │   └── report_generator.py       # PDF report generation (FPDF2)
│   └── utils/
│       ├── __init__.py
│       ├── cost_mapping.py           # Damage type × severity cost matrix
│       ├── gradcam_plusplus.py        # Grad-CAM++ implementation
│       ├── image_processing.py       # Preprocessing & heatmap overlay
│       ├── logo_generator.py         # Programmatic logo generation
│       └── model_loader.py           # Cached model & KNN index loading
│
├── src/                              # 🧠 ML Pipeline
│   ├── __init__.py
│   ├── model.py                      # Multi-head EfficientNet-B3 architecture
│   ├── train.py                      # Training loop with callbacks
│   ├── evaluate.py                   # Metrics & confusion matrices
│   ├── data_pipeline.py              # Synthetic dataset generator
│   └── feature_extractor.py          # KNN feature extraction & indexing
│
├── data/
│   └── synthetic/                    # Generated training data
│       ├── metadata.csv              # Image labels & paths
│       └── SYNTHETIC_DATA_NOTE.md    # Dataset documentation
│
├── models/                           # Saved model weights (.h5)
├── outputs/                          # Training logs & confusion matrices
│
├── .streamlit/
│   └── config.toml                   # Streamlit production configuration
│
├── Dockerfile                        # Production container
├── docker-compose.yml                # Container orchestration
├── .dockerignore                     # Docker build exclusions
├── Procfile                          # Cloud platform deployment
├── runtime.txt                       # Python version specification
├── requirements.txt                  # Pinned dependencies
├── setup.sh                          # Linux/macOS setup script
├── setup.bat                         # Windows setup script
├── run_checks.py                     # Import validation
├── .gitignore                        # Git exclusions
├── LICENSE                           # MIT License
├── DEPLOYMENT_GUIDE.md               # Deployment strategies & interview Q&A
├── INTERVIEW_CHEATSHEET.md           # Technical interview preparation
└── README.md                         # ← You are here
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **pip** (included with Python)
- **Git** ([Download](https://git-scm.com/downloads))

### Option 1: Local Setup (Recommended)

<details>
<summary><strong>🪟 Windows</strong></summary>

```powershell
# Clone the repository
git clone https://github.com/sivadst/vehicle-damage-ai.git
cd vehicle-damage-ai

# Run the automated setup
setup.bat
```
</details>

<details>
<summary><strong>🐧 Linux / 🍎 macOS</strong></summary>

```bash
# Clone the repository
git clone https://github.com/sivadst/vehicle-damage-ai.git
cd vehicle-damage-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Run the automated setup
bash setup.sh
```
</details>

Then launch the app:
```bash
streamlit run app/main.py
```

Open your browser at **http://localhost:8501** 🎉

### Option 2: Docker (Zero Config)

```bash
# Clone and run
git clone https://github.com/sivadst/vehicle-damage-ai.git
cd vehicle-damage-ai

# Build and launch
docker-compose up --build

# Or manually:
docker build -t vehicle-damage-ai .
docker run -p 8501:8501 vehicle-damage-ai
```

Open **http://localhost:8501** 🐳

---

## 📖 Usage Guide

### 1. Upload an Image
Drag and drop or click to upload a vehicle photo (JPG/PNG, max 10MB).

### 2. Analyze Damage
Click **🔍 Analyze Damage** to start the AI assessment pipeline.

### 3. Review Results
The system displays:
- **Damage Type** — What kind of damage was detected
- **Severity Level** — Minor / Moderate / Severe with risk badge
- **Location** — Where on the vehicle the damage is located
- **Confidence Scores** — Per-head prediction confidence
- **Repair Cost Estimate** — Based on damage × severity matrix

### 4. Examine Explainability
Review the **Grad-CAM++ heatmap** to see exactly which image regions the AI focused on. Red/yellow areas indicate high attention.

### 5. Download Report
Click **📄 Download Assessment Report** to generate a professional PDF summarizing all findings.

### 6. Configure Settings
Use the **sidebar** to:
- Toggle **Demo Mode** (mock inference vs. real model)
- Adjust **Confidence Threshold** for human-review flagging
- View **Model Architecture** details

---

## ☁️ Deployment Options

### Streamlit Community Cloud (Free)
1. Push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → Select `app/main.py` → Deploy

### Google Cloud Run
```bash
# Build for GCR
docker build -t gcr.io/[PROJECT_ID]/vehicle-damage-ai .
docker push gcr.io/[PROJECT_ID]/vehicle-damage-ai

# Deploy
gcloud run deploy vehicle-damage-ai \
  --image gcr.io/[PROJECT_ID]/vehicle-damage-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi
```

### Railway / Render
Simply connect your GitHub repo — the `Procfile` and `runtime.txt` handle the rest automatically.

---

## 📊 Model Performance

### Training Configuration
| Parameter | Value |
|:--|:--|
| Backbone | EfficientNet-B3 (ImageNet) |
| Input Size | 224 × 224 × 3 |
| Batch Size | 32 |
| Epochs | 30 (with early stopping) |
| Optimizer | Adam (lr=1e-4) |
| Loss | Categorical Cross-Entropy |
| Loss Weights | Damage: 1.0, Severity: 0.8, Location: 0.5 |
| Callbacks | EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard |

### Target Metrics (Production Data)
| Task | Target F1-Score | Inference (CPU) | Inference (GPU) |
|:--|:--|:--|:--|
| Damage Type | >85% | <1.5s | <0.3s |
| Severity | >90% | — | — |
| Location | >80% | — | — |

### Model Size
~45 MB (EfficientNet-B3 is highly parameter-efficient via compound scaling)

---

## 🧪 Evaluation

Run the full evaluation suite to generate classification reports and confusion matrices:

```bash
python -m src.evaluate
```

**Outputs:**
- Precision, Recall, F1-Score per class (printed to console)
- `outputs/confusion_matrix_damage.png` — Damage type confusion matrix
- `outputs/confusion_matrix_severity.png` — Severity confusion matrix
- `outputs/logs/` — TensorBoard training logs

```bash
# View training curves in TensorBoard
tensorboard --logdir outputs/logs
```

---

## 🔧 Development & Testing

### System Health & Import Check
```bash
python run_checks.py
```

### Automated Unit Test Suite
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Training & Data Pipeline
```bash
# Generate synthetic dataset
python src/data_pipeline.py

# Train (full)
python -m src.train

# Train (demo mode — 1 epoch, tiny subset)
python -m src.train --demo-mode

# Build KNN index for similar case retrieval
python -m src.feature_extractor
```

---

## ⚠️ System Limitations & Production Considerations

Being open about system boundaries and model trade-offs is a core software engineering principle. Users and deployment teams should consider the following:

| Boundary / Limitation | Current Implementation | Production Roadmap / Mitigation |
|:---|:---|:---|
| **Classification vs. Segmentation** | Focuses on multi-task classification and Grad-CAM++ visual heatmaps rather than polygon mask segmentation. | Future v2 pipeline will incorporate Mask R-CNN / YOLOv8-seg for pixel-level damage area calculations ($\text{cm}^2$). |
| **Synthetic Dataset Constraints** | Uses procedural OpenCV synthesis for zero-licensing demonstration capabilities. | Model weights should be fine-tuned on real insurer historical claims photos for optimal domain generalizability. |
| **Heuristic Cost Mapping** | Repair ranges and labor durations are deterministic matrix lookups. | Production integration requires linking to real-time shop repair databases (e.g. CCC ONE, Mitchell, Audatex APIs). |
| **Compound Damage Handling** | Assigns single primary damage category per impact zone. | Multi-label classification heads can be activated to detect overlapping damage (e.g. dent + scratch on same door panel). |
| **Environmental Quality Dependency** | Low light or extreme mud/snow coverage flags warnings via the Quality Gatekeeper. | Pre-inference enhancement pipeline (CLAHE contrast equalization) and human adjuster review queues handle edge cases. |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**sivadst**

- GitHub: [@sivadst](https://github.com/sivadst)
- Email: mr.s.selvasiva.ds@gmail.com

---

<p align="center">
  <strong>⭐ If this project helped you, please give it a star! ⭐</strong>
</p>

<p align="center">
  <sub>Built with ❤️ using TensorFlow, Streamlit, and OpenCV</sub>
</p>
