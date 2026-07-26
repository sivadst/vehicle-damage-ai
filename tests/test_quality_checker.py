"""
Unit tests for Image Quality Gatekeeper module.
"""

import unittest
import numpy as np
from app.utils.quality_checker import assess_image_quality, ImageQualityResult


class TestQualityChecker(unittest.TestCase):
    """Test suite for quality_checker functions and metrics."""

    def test_sharp_image_assessment(self):
        """Tests quality assessment on a sharp image array."""
        # Create a sharp checkerboard pattern
        sharp_img = np.zeros((300, 300, 3), dtype=np.uint8)
        sharp_img[::20, ::20] = 255
        
        result = assess_image_quality(sharp_img)
        self.assertIsInstance(result, ImageQualityResult)
        self.assertGreater(result.blur_score, 0)
        self.assertEqual(result.resolution, (300, 300))

    def test_dark_image_assessment(self):
        """Tests under-exposure detection on a black image."""
        dark_img = np.zeros((300, 300, 3), dtype=np.uint8)
        result = assess_image_quality(dark_img)
        self.assertTrue(result.is_dark)
        self.assertIn("under-exposed", result.warnings[0])

    def test_resolution_check(self):
        """Tests low resolution warning triggering."""
        small_img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        result = assess_image_quality(small_img, min_resolution=(224, 224))
        self.assertFalse(result.is_valid)


if __name__ == "__main__":
    unittest.main()
