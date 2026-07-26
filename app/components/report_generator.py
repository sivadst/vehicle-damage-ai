import streamlit as st
import base64
import datetime
from io import BytesIO
from fpdf import FPDF
from pathlib import Path
import json

def generate_pdf_report(image_path_or_bytes, heatmap_bytes, results, cost_estimate):
    """Generates a professional PDF report for the insurance claim."""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "Automated Vehicle Damage Assessment Report", 0, 1, 'C')
    
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(190, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    pdf.ln(10)
    
    # Save temp images for PDF
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_heat:
        tmp_heat.write(heatmap_bytes)
        tmp_heat_path = tmp_heat.name
        
    # Content
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "Assessment Summary", 0, 1, 'L')
    pdf.set_font("Arial", '', 11)
    
    # Determine risk level based on severity
    severity_level = results['severity']['label'].lower()
    risk = "HIGH" if severity_level == 'severe' else "MEDIUM" if severity_level == 'moderate' else "LOW"
    
    # Summary block
    summary_text = (
        f"Primary Damage Detected: {results['damage_type']['label'].replace('_', ' ').title()}\n"
        f"Confidence Score: {results['damage_type']['confidence']*100:.1f}%\n"
        f"Severity: {results['severity']['label'].title()} ({results['severity']['confidence']*100:.1f}%)\n"
        f"Estimated Location: {results['location']['label'].title()} ({results['location']['confidence']*100:.1f}%)\n"
        f"Estimated Repair Cost: {cost_estimate}\n"
        f"Action Required: {'Immediate Adjuster Review' if risk == 'HIGH' else 'Standard Triage'}"
    )
    pdf.multi_cell(190, 8, summary_text)
    pdf.ln(10)
    
    # Heatmap Image (The core evidence)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "AI Attention Heatmap (Evidence)", 0, 1, 'L')
    pdf.image(tmp_heat_path, x=10, y=pdf.get_y(), w=90)
    
    # Cleanup
    import os
    try:
        os.remove(tmp_heat_path)
    except:
        pass
        
    return pdf.output(dest="S").encode("latin-1")
