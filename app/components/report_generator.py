"""
Insurance Claim PDF Report Generator.

Compiles AI assessment results, triage metrics, and Grad-CAM++ evidence heatmaps
into a formatted PDF document.
"""

import datetime
import os
import random
import tempfile
from typing import Dict, Any, Optional
from fpdf import FPDF


def generate_pdf_report(
    image_path_or_bytes: Any,
    heatmap_bytes: bytes,
    results: Dict[str, Dict[str, Any]],
    cost_estimate: str,
    triage_info: Optional[Dict[str, str]] = None,
    claim_id: Optional[str] = None
) -> bytes:
    """Generates a PDF assessment report for insurance claim processing.

    Args:
        image_path_or_bytes: Original input image or path.
        heatmap_bytes (bytes): Grad-CAM++ attention heatmap JPEG bytes.
        results (Dict): Model prediction results dictionary.
        cost_estimate (str): Formatted cost range.
        triage_info (Dict, optional): Labor time and priority dictionary.
        claim_id (str, optional): Unique claim reference identifier.

    Returns:
        bytes: Compiled PDF file bytes.
    """
    if claim_id is None:
        claim_id = f"CLM-{datetime.datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    if triage_info is None:
        triage_info = {"cost": cost_estimate, "time": "1-3 Business Days", "priority": "P2 - Standard"}

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 1. Header Banner
    pdf.set_font("Helvetica", 'B', 18)
    pdf.set_text_color(31, 119, 180) # Primary Blue
    pdf.cell(190, 10, "AUTOMATED VEHICLE DAMAGE ASSESSMENT", 0, 1, 'C')

    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(190, 6, "AI Claims Inspection & Visual Evidence Report", 0, 1, 'C')
    pdf.cell(190, 6, f"Claim ID: {claim_id}  |  Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", 0, 1, 'C')
    pdf.ln(8)

    # Divider Line
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    # 2. Executive Summary Block
    pdf.set_font("Helvetica", 'B', 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(190, 8, "1. Assessment Summary & Triage", 0, 1, 'L')
    pdf.ln(2)

    severity_label = results['severity']['label'].lower()
    risk_level = "CRITICAL (High Risk)" if severity_label == 'severe' else "MODERATE (Medium Risk)" if severity_level == 'moderate' else "LOW (Routine)"

    summary_text = (
        f"Primary Damage Type: {results['damage_type']['label'].replace('_', ' ').title()} "
        f"({results['damage_type']['confidence']*100:.1f}% confidence)\n"
        f"Severity Rating:     {results['severity']['label'].title()} "
        f"({results['severity']['confidence']*100:.1f}% confidence)\n"
        f"Impact Location:     {results['location']['label'].title()} "
        f"({results['location']['confidence']*100:.1f}% confidence)\n"
        f"Estimated Cost:      {cost_estimate}\n"
        f"Estimated Labor Time:{triage_info.get('time', 'N/A')}\n"
        f"Triage Priority:     {triage_info.get('priority', 'P2 - Standard')}\n"
        f"Action Required:     {'Escalate to Adjuster' if severity_label == 'severe' else 'Standard Auto-Triage'}"
    )

    pdf.set_font("Courier", '', 10)
    pdf.set_fill_color(245, 247, 250)
    pdf.multi_cell(190, 6, summary_text, fill=True, border=1)
    pdf.ln(8)

    # 3. Explainability & Evidence Heatmap
    pdf.set_font("Helvetica", 'B', 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(190, 8, "2. Explainable AI Evidence (Grad-CAM++ Heatmap)", 0, 1, 'L')
    pdf.set_font("Helvetica", 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(190, 6, "Highlighted regions show image pixel activations driving the neural network classification.", 0, 1, 'L')
    pdf.ln(4)

    # Save heatmap bytes to temporary file for PDF inclusion
    tmp_heat_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_heat:
            tmp_heat.write(heatmap_bytes)
            tmp_heat_path = tmp_heat.name

        pdf.image(tmp_heat_path, x=10, y=pdf.get_y(), w=110)
    except Exception as e:
        pdf.set_font("Helvetica", '', 10)
        pdf.cell(190, 10, f"[Heatmap Evidence Unavailable: {e}]", 0, 1, 'L')

    # Footer note
    pdf.set_y(-25)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(190, 5, "Confidential - Vehicle Damage AI Automated Claims Assessment System", 0, 1, 'C')
    pdf.cell(190, 5, "This AI report provides automated triage guidance and does not replace final legal adjuster signature.", 0, 1, 'C')

    # Cleanup temp evidence file
    if tmp_heat_path and os.path.exists(tmp_heat_path):
        try:
            os.remove(tmp_heat_path)
        except OSError:
            pass

    return bytes(pdf.output())
