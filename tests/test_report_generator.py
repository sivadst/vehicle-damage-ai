"""
Unit tests for PDF Report Generator module.
"""

import unittest
import cv2
import numpy as np
from app.components.report_generator import generate_pdf_report


class TestReportGenerator(unittest.TestCase):
    """Test suite for PDF report compilation."""

    def test_generate_pdf_report(self):
        """Tests end-to-end PDF byte generation without exceptions."""
        dummy_heatmap = np.zeros((100, 100, 3), dtype=np.uint8)
        heatmap_bytes = cv2.imencode('.jpg', dummy_heatmap)[1].tobytes()

        results = {
            "damage_type": {"label": "scratch", "confidence": 0.92},
            "severity": {"label": "minor", "confidence": 0.88},
            "location": {"label": "side", "confidence": 0.85}
        }

        pdf_bytes = generate_pdf_report(
            image_path_or_bytes=None,
            heatmap_bytes=heatmap_bytes,
            results=results,
            cost_estimate="$100 - $300"
        )

        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 0)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
