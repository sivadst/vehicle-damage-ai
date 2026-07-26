import streamlit as st
import numpy as np
import time
import random
import cv2
from io import BytesIO
from PIL import Image
import plotly.graph_objects as go
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from app.components.style import inject_custom_css
from app.utils.model_loader import load_cached_model, load_knn_index
from app.utils.image_processing import preprocess_image, overlay_heatmap
from app.utils.gradcam_plusplus import apply_gradcam_plusplus
from app.utils.cost_mapping import estimate_cost
from app.components.report_generator import generate_pdf_report
from src.constants import CLASSES, SEVERITIES, LOCATIONS

# Ensure executor is available globally or per session
if 'executor' not in st.session_state:
    st.session_state.executor = ThreadPoolExecutor(max_workers=3)

# Define mock functions for demo mode
def mock_predict():
    """Generates realistic mock predictions for demo purposes."""
    dt = random.choices(CLASSES, weights=[0.05, 0.3, 0.4, 0.1, 0.05, 0.1], k=1)[0]
    sev = random.choices(SEVERITIES, weights=[0.2, 0.6, 0.2], k=1)[0]
    loc = random.choices(LOCATIONS, weights=[0.3, 0.2, 0.3, 0.05, 0.1, 0.05], k=1)[0]
    
    return {
        "damage_type": {"label": dt, "confidence": random.uniform(0.75, 0.96)},
        "severity": {"label": sev, "confidence": random.uniform(0.65, 0.92)},
        "location": {"label": loc, "confidence": random.uniform(0.50, 0.88)}
    }

def mock_gradcam(img_array):
    """Generates a fake heatmap focused on the lower center."""
    h, w = img_array.shape[0], img_array.shape[1]
    heatmap = np.zeros((h, w), dtype=np.float32)
    center_y, center_x = int(h * 0.7), int(w * 0.5)
    radius = int(min(h, w) * 0.3)
    
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
    
    mask = dist_from_center <= radius
    heatmap[mask] = 1 - (dist_from_center[mask] / radius)
    return heatmap

def build_confidence_chart(results):
    fig = go.Figure(go.Bar(
        x=[results['damage_type']['confidence'], results['severity']['confidence'], results['location']['confidence']],
        y=['Damage Type', 'Severity', 'Location'],
        orientation='h',
        marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ))
    fig.update_layout(
        title="Prediction Confidence",
        xaxis=dict(title='Confidence', range=[0, 1], tickformat='.0%'),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=0, r=0, t=30, b=0),
        height=200,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def main():
    st.set_page_config(page_title="Vehicle Damage AI", page_icon="🚗", layout="wide")
    inject_custom_css()
    
    # Sidebar
    with st.sidebar:
        st.image("app/assets/logo.png", width=150)
        st.title("Settings")
        demo_mode = st.toggle("🟡 Demo Mode (Mock Inference)", value=True, help="Use simulated predictions to avoid loading the full ML model.")
        conf_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.70, help="Flags predictions below this threshold for human review.")
        
        st.divider()
        st.subheader("Interview Explainability")
        show_architecture = st.checkbox("Show Model Architecture")
        
        st.divider()
        st.caption("v1.0.0 | Production Ready")
        
    # Main content
    st.title("🚗 Automated Vehicle Damage Assessment")
    st.markdown("Upload a vehicle image to instantly classify damage, assess severity, and generate a repair estimate.")
    
    if demo_mode:
        st.warning("🟡 **Demo Mode Active**: Using lightweight simulated inference for immediate demonstration.")
        
    uploaded_file = st.file_uploader("Upload Vehicle Image (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.subheader("Uploaded Image")
            display_img, model_input = preprocess_image(uploaded_file)
            st.image(display_img, use_container_width=True)
            
            analyze_btn = st.button("🔍 Analyze Damage", use_container_width=True)
            
        if analyze_btn:
            with col2:
                # 1. Processing State
                status_text = st.empty()
                progress_bar = st.progress(0)
                
                status_text.text("⚙️ Loading model...")
                progress_bar.progress(20)
                
                if not demo_mode:
                    model = load_cached_model()
                    if model is None:
                        st.stop()
                time.sleep(0.3)
                
                status_text.text("🔍 Analyzing damage patterns...")
                progress_bar.progress(50)
                
                if demo_mode:
                    results = mock_predict()
                    time.sleep(0.5)
                else:
                    preds = model.predict(model_input)
                    dt_idx = np.argmax(preds[0][0])
                    sev_idx = np.argmax(preds[1][0])
                    loc_idx = np.argmax(preds[2][0])
                    
                    results = {
                        "damage_type": {"label": CLASSES[dt_idx], "confidence": float(preds[0][0][dt_idx])},
                        "severity": {"label": SEVERITIES[sev_idx], "confidence": float(preds[1][0][sev_idx])},
                        "location": {"label": LOCATIONS[loc_idx], "confidence": float(preds[2][0][loc_idx])}
                    }
                
                status_text.text("🧠 Generating explainability heatmap...")
                progress_bar.progress(80)
                
                if demo_mode:
                    heatmap = mock_gradcam(display_img)
                    time.sleep(0.4)
                else:
                    dt_idx = CLASSES.index(results['damage_type']['label'])
                    heatmap = apply_gradcam_plusplus(model, model_input, dt_idx)
                
                superimposed, colored_heatmap = overlay_heatmap(display_img, heatmap)
                
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                
                # 2. Results Display
                st.subheader("Assessment Results")
                
                # Risk Badge
                sev_label = results['severity']['label'].lower()
                badge_class = "badge-minor" if sev_label == "minor" else "badge-moderate" if sev_label == "moderate" else "badge-severe"
                risk_text = "🟢 Approve (Low Risk)" if sev_label == "minor" else "🟡 Review (Medium Risk)" if sev_label == "moderate" else "🔴 Escalate (High Risk)"
                
                st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
                
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                metrics_col1.metric("Damage Type", results['damage_type']['label'].replace("_", " ").title())
                metrics_col2.metric("Severity", results['severity']['label'].title())
                metrics_col3.metric("Location", results['location']['label'].title())
                
                st.markdown(f'<span class="badge {badge_class}">{risk_text}</span>', unsafe_allow_html=True)
                
                # Check threshold
                if any(r['confidence'] < conf_threshold for r in results.values()):
                    st.warning(f"⚠️ Confidence below threshold ({conf_threshold*100:.0f}%). Human review required.")
                    
                cost = estimate_cost(results['damage_type']['label'], results['severity']['label'])
                st.success(f"**Estimated Repair Cost:** {cost}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 3. Explainability
                st.subheader("Model Explainability (Grad-CAM++)")
                cam_col1, cam_col2 = st.columns(2)
                cam_col1.image(superimposed, caption="Attention Overlay", use_container_width=True)
                cam_col2.image(colored_heatmap, caption="Heatmap Only", use_container_width=True)
                
                with st.expander("Why This Prediction?"):
                    st.write(f"The AI focused on the highlighted regions (red/yellow) to determine the damage type is **{results['damage_type']['label'].replace('_', ' ')}**.")
                    st.plotly_chart(build_confidence_chart(results), use_container_width=True)
                    
                    if demo_mode:
                        st.info("Similar cases from database (Mock Data):")
                        sim_cols = st.columns(3)
                        sim_cols[0].image("app/assets/logo.png", caption="Case 1 (0.89)")
                        sim_cols[1].image("app/assets/logo.png", caption="Case 2 (0.84)")
                        sim_cols[2].image("app/assets/logo.png", caption="Case 3 (0.81)")
                    else:
                        knn, meta = load_knn_index()
                        if knn is not None:
                            # In reality, we'd extract features here. Mocking the UI part of it for brevity if not demo mode.
                            st.info("KNN Retrieval requires live feature extraction.")
                            
                # 4. Report Generation
                # Use threading to generate PDF without blocking
                with st.spinner("Preparing PDF Report..."):
                    img_bytes = cv2.imencode('.jpg', cv2.cvtColor(colored_heatmap, cv2.COLOR_BGR2RGB))[1].tobytes()
                    future = st.session_state.executor.submit(generate_pdf_report, None, img_bytes, results, cost)
                    pdf_bytes = future.result(timeout=15)
                    
                st.download_button(
                    label="📄 Download Assessment Report (PDF)",
                    data=pdf_bytes,
                    file_name="Vehicle_Damage_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
    if show_architecture:
        st.divider()
        st.subheader("Technical Architecture Deep Dive")
        st.markdown("""
        **Model Backbone:** EfficientNet-B3 (Transfer Learning from ImageNet)\n
        **Why EfficientNet?** It offers an optimal balance of accuracy and parameter efficiency compared to ResNet.
        
        **Multi-Task Head:**
        - **Branch 1:** Damage Type (6 classes) - Uses Focal Loss to handle extreme class imbalances.
        - **Branch 2:** Severity (3 classes)
        - **Branch 3:** Location (5 classes)
        
        *Shared visual features between tasks reduce overall inference time and parameter count compared to three distinct models.*
        """)

if __name__ == "__main__":
    main()
