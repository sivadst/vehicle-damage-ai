"""
Automated Vehicle Damage Assessment AI Application.

Production Streamlit web application for:
- Automated vehicle damage classification (6 categories)
- Damage severity rating & impact location mapping
- Image quality & safety gatekeeping (blur, brightness, resolution checks)
- Explainable AI visual evidence (Grad-CAM++) with interactive opacity blending
- Claims triage estimation (cost range, labor time, priority scoring)
- Automated PDF report compilation & download
"""

import sys
from pathlib import Path

# Add project root directory to sys.path for Streamlit Cloud deployment
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import datetime
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Tuple

import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import streamlit as st

from app.components.report_generator import generate_pdf_report
from app.components.style import inject_custom_css
from app.utils.cost_mapping import estimate_cost, get_claim_triage_info
from app.utils.gradcam_plusplus import apply_gradcam_plusplus
from app.utils.image_processing import overlay_heatmap, preprocess_image
from app.utils.model_loader import load_cached_model, load_knn_index
from app.utils.quality_checker import assess_image_quality, ImageQualityResult
from src.constants import CLASSES, LOCATIONS, SEVERITIES

# Ensure executor is available globally in session state
if 'executor' not in st.session_state:
    st.session_state.executor = ThreadPoolExecutor(max_workers=3)

# Initialize prediction history tracking in session state
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []


def mock_predict() -> Dict[str, Dict[str, Any]]:
    """Generates realistic simulated prediction metrics for demonstration mode.

    Returns:
        Dict: Structured predictions for damage_type, severity, and location.
    """
    dt = random.choices(CLASSES, weights=[0.05, 0.3, 0.4, 0.1, 0.05, 0.1], k=1)[0]
    sev = random.choices(SEVERITIES, weights=[0.2, 0.6, 0.2], k=1)[0]
    loc = random.choices(LOCATIONS, weights=[0.3, 0.2, 0.3, 0.05, 0.1, 0.05], k=1)[0]

    return {
        "damage_type": {"label": dt, "confidence": float(random.uniform(0.78, 0.96))},
        "severity": {"label": sev, "confidence": float(random.uniform(0.70, 0.94))},
        "location": {"label": loc, "confidence": float(random.uniform(0.65, 0.90))}
    }


def mock_gradcam(img_array: np.ndarray) -> np.ndarray:
    """Generates a synthetic heatmap focused on damaged vehicle regions.

    Args:
        img_array (np.ndarray): Original image array.

    Returns:
        np.ndarray: 2D normalized heatmap [0, 1].
    """
    h, w = img_array.shape[:2]
    heatmap = np.zeros((h, w), dtype=np.float32)
    center_y, center_x = int(h * 0.65), int(w * 0.5)
    radius = int(min(h, w) * 0.28)

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)

    mask = dist_from_center <= radius
    heatmap[mask] = 1.0 - (dist_from_center[mask] / radius)
    return heatmap


def build_confidence_chart(results: Dict[str, Dict[str, Any]]) -> go.Figure:
    """Builds a horizontal bar chart displaying prediction confidence scores.

    Args:
        results (Dict): Model prediction results dictionary.

    Returns:
        go.Figure: Configured Plotly figure object.
    """
    fig = go.Figure(
        go.Bar(
            x=[
                results['damage_type']['confidence'],
                results['severity']['confidence'],
                results['location']['confidence']
            ],
            y=['Damage Type', 'Severity', 'Location'],
            orientation='h',
            marker=dict(color=['#2b6cb0', '#dd6b20', '#38a169']),
            text=[
                f"{results['damage_type']['confidence'] * 100:.1f}%",
                f"{results['severity']['confidence'] * 100:.1f}%",
                f"{results['location']['confidence'] * 100:.1f}%"
            ],
            textposition='auto'
        )
    )
    fig.update_layout(
        title="Neural Network Prediction Confidence Breakdown",
        xaxis=dict(title='Confidence Score', range=[0, 1], tickformat='.0%'),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=0, r=0, t=35, b=0),
        height=220,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig


def main():
    """Main Streamlit Application Entrypoint."""
    st.set_page_config(
        page_title="Vehicle Damage AI - Enterprise Claims Assessment",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    inject_custom_css()

    # Sidebar Controls
    with st.sidebar:
        try:
            st.image("app/assets/logo.png", width=140)
        except Exception:
            pass

        st.title("Settings & Control")
        demo_mode = st.toggle(
            "🟡 Demo Mode (Mock Inference)",
            value=True,
            help="Simulate model inference without loading full TensorFlow neural net into memory."
        )
        conf_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.50,
            max_value=0.95,
            value=0.70,
            step=0.05,
            help="Automated triage flag threshold. Predictions below this level trigger human review."
        )

        st.divider()
        st.subheader("Explainability Settings")
        heatmap_opacity = st.slider(
            "Grad-CAM Opacity",
            min_value=0.1,
            max_value=0.9,
            value=0.45,
            step=0.05,
            help="Adjust Grad-CAM++ heatmap overlay blending transparency."
        )

        st.divider()
        show_architecture = st.checkbox("Show Model Architecture")
        st.caption("v1.2.0 | Production SaaS Edition")

    # Main Hero Title
    st.title("🚗 Automated Vehicle Damage AI")
    st.markdown(
        "Upload a vehicle inspection image for **instant multi-task classification**, "
        "Explainable AI heatmap evidence, and automated repair cost triage."
    )

    if demo_mode:
        st.warning("🟡 **Demo Mode Active**: Running lightweight simulated inference for high-speed demonstration.")

    # Image Upload Section
    uploaded_file = st.file_uploader(
        "Upload Vehicle Damage Photo (JPG/PNG)",
        type=['jpg', 'jpeg', 'png'],
        help="Supports vehicle damage photos up to 10MB."
    )

    if uploaded_file is not None:
        col_img, col_results = st.columns([1, 1.4])

        with col_img:
            st.subheader("📷 Input Image Analysis")
            display_img, model_input = preprocess_image(uploaded_file)
            st.image(display_img, use_container_width=True)

            # Image Quality Gatekeeper Assessment
            quality_res: ImageQualityResult = assess_image_quality(display_img)

            with st.expander("🔍 Image Quality Assessment", expanded=not quality_res.is_valid):
                q_col1, q_col2, q_col3 = st.columns(3)
                q_col1.metric("Resolution", f"{quality_res.resolution[0]}x{quality_res.resolution[1]}")
                q_col2.metric("Sharpness Score", f"{quality_res.blur_score:.1f}")
                q_col3.metric("Luminance", f"{quality_res.brightness_score:.1f}")

                if quality_res.warnings:
                    for warn in quality_res.warnings:
                        st.markdown(f'<div class="quality-banner">⚠️ {warn}</div>', unsafe_allow_html=True)
                else:
                    st.success("✅ Image quality is optimal for AI model inference.")

            analyze_btn = st.button("🔍 Run Damage Assessment", use_container_width=True)

        if analyze_btn:
            with col_results:
                status_text = st.empty()
                progress_bar = st.progress(0)

                # Step 1: Model Initialization
                status_text.text("⚙️ Initializing neural backbone...")
                progress_bar.progress(25)

                if not demo_mode:
                    model = load_cached_model()
                    if model is None:
                        st.stop()
                time.sleep(0.2)

                # Step 2: Multi-Task Classification
                status_text.text("🧠 Executing Multi-Task EfficientNet inference...")
                progress_bar.progress(55)

                if demo_mode:
                    results = mock_predict()
                    time.sleep(0.4)
                else:
                    preds = model.predict(model_input, verbose=0)
                    dt_idx = int(np.argmax(preds[0][0]))
                    sev_idx = int(np.argmax(preds[1][0]))
                    loc_idx = int(np.argmax(preds[2][0]))

                    results = {
                        "damage_type": {"label": CLASSES[dt_idx], "confidence": float(preds[0][0][dt_idx])},
                        "severity": {"label": SEVERITIES[sev_idx], "confidence": float(preds[1][0][sev_idx])},
                        "location": {"label": LOCATIONS[loc_idx], "confidence": float(preds[2][0][loc_idx])}
                    }

                # Step 3: Grad-CAM++ Visual Evidence Generation
                status_text.text("🔥 Computing Grad-CAM++ spatial attention maps...")
                progress_bar.progress(85)

                if demo_mode:
                    heatmap = mock_gradcam(display_img)
                    time.sleep(0.3)
                else:
                    dt_idx = CLASSES.index(results['damage_type']['label'])
                    heatmap = apply_gradcam_plusplus(model, model_input, dt_idx)

                superimposed, colored_heatmap = overlay_heatmap(display_img, heatmap, alpha=heatmap_opacity)

                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()

                # Results Presentation Block
                st.subheader("📊 Assessment & Claims Triage Results")

                sev_label = results['severity']['label'].lower()
                badge_class = "badge-minor" if sev_label == "minor" else "badge-moderate" if sev_label == "moderate" else "badge-severe"
                risk_text = "🟢 Auto-Approve (Low Risk)" if sev_label == "minor" else "🟡 Standard Triage (Medium Risk)" if sev_label == "moderate" else "🔴 Escalate (High Severity)"

                st.markdown('<div class="result-card">', unsafe_allow_html=True)

                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("Damage Type", results['damage_type']['label'].replace("_", " ").title())
                m_col2.metric("Severity Level", results['severity']['label'].title())
                m_col3.metric("Impact Location", results['location']['label'].title())

                st.markdown(f'<span class="badge {badge_class}">{risk_text}</span>', unsafe_allow_html=True)

                # Human Review Threshold Check
                low_conf_heads = [k for k, v in results.items() if v['confidence'] < conf_threshold]
                if low_conf_heads:
                    st.markdown(
                        f'<div class="escalation-banner">⚠️ <strong>Human Adjuster Review Required</strong>: '
                        f'Confidence for ({", ".join(low_conf_heads)}) is below target threshold ({conf_threshold * 100:.0f}%).</div>',
                        unsafe_allow_html=True
                    )

                # Triage Matrix Lookup
                triage_info = get_claim_triage_info(results['damage_type']['label'], results['severity']['label'])

                st.divider()
                t_col1, t_col2, t_col3 = st.columns(3)
                t_col1.metric("Estimated Cost", triage_info['cost'])
                t_col2.metric("Est. Labor Time", triage_info['time'])
                t_col3.metric("Priority Level", triage_info['priority'])

                st.markdown('</div>', unsafe_allow_html=True)

                # Session History Log
                st.session_state.prediction_history.append({
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "damage": results['damage_type']['label'].replace("_", " ").title(),
                    "severity": results['severity']['label'].title(),
                    "cost": triage_info['cost'],
                    "confidence": f"{results['damage_type']['confidence'] * 100:.0f}%"
                })

                # Tabs for Deep Dive & Report Generation
                tab_xai, tab_history = st.tabs(["🧠 Explainability & Charts", "📜 Session Claims History"])

                with tab_xai:
                    cam_c1, cam_c2 = st.columns(2)
                    cam_c1.image(superimposed, caption=f"Attention Overlay (Opacity: {heatmap_opacity:.2f})", use_container_width=True)
                    cam_c2.image(colored_heatmap, caption="Raw Grad-CAM++ Activation", use_container_width=True)

                    st.plotly_chart(build_confidence_chart(results), use_container_width=True)

                with tab_history:
                    if st.session_state.prediction_history:
                        df_hist = pd.DataFrame(st.session_state.prediction_history)
                        st.dataframe(df_hist, use_container_width=True)

                # PDF Report Download Button
                with st.spinner("Compiling PDF Claim Evidence Report..."):
                    img_bytes = cv2.imencode('.jpg', cv2.cvtColor(colored_heatmap, cv2.COLOR_BGR2RGB))[1].tobytes()
                    future = st.session_state.executor.submit(
                        generate_pdf_report,
                        None,
                        img_bytes,
                        results,
                        triage_info['cost'],
                        triage_info
                    )
                    pdf_bytes = future.result(timeout=15)

                st.download_button(
                    label="📄 Download Assessment Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"Damage_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

    if show_architecture:
        st.divider()
        st.subheader("Technical System Architecture")
        st.markdown("""
        **Model Backbone:** EfficientNet-B3 (Transfer Learning from ImageNet)  
        **Multi-Task Heads:**
        - **Branch 1:** Damage Type Classification (6 classes)
        - **Branch 2:** Severity Assessment (3 classes)
        - **Branch 3:** Location Prediction (5 classes)  

        **Explainability Engine:** Grad-CAM++ with 2nd/3rd order gradient linearization.
        """)


if __name__ == "__main__":
    main()
