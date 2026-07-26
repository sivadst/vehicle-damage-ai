"""
Image Quality and Safety Gatekeeper Module.

Provides automated pre-inference quality checks on uploaded vehicle images:
- Blur detection via Laplacian variance
- Exposure analysis (under/over exposure via luminance histogram)
- Resolution and aspect ratio validation
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image


@dataclass
class ImageQualityResult:
    """Structured container for image quality assessment metrics."""
    is_valid: bool
    blur_score: float
    brightness_score: float
    resolution: Tuple[int, int]
    warnings: List[str] = field(default_factory=list)

    @property
    def is_blurry(self) -> bool:
        return self.blur_score < 100.0

    @property
    def is_dark(self) -> bool:
        return self.brightness_score < 40.0

    @property
    def is_overexposed(self) -> bool:
        return self.brightness_score > 215.0


def assess_image_quality(
    image_input: np.ndarray,
    min_resolution: Tuple[int, int] = (224, 224),
    blur_threshold: float = 100.0,
    min_brightness: float = 40.0,
    max_brightness: float = 215.0
) -> ImageQualityResult:
    """Performs non-intrusive computer vision quality checks on an image array.

    Args:
        image_input (np.ndarray): Input RGB image array (H, W, C).
        min_resolution (Tuple[int, int]): Minimum acceptable (width, height).
        blur_threshold (float): Variance threshold below which image is flagged as blurry.
        min_brightness (float): Minimum mean luminance.
        max_brightness (float): Maximum mean luminance.

    Returns:
        ImageQualityResult: Detailed quality evaluation object with warning messages.
    """
    warnings: List[str] = []
    height, width = image_input.shape[:2]

    # 1. Resolution Check
    if width < min_resolution[0] or height < min_resolution[1]:
        warnings.append(
            f"Low resolution ({width}x{height}). Minimum recommended is {min_resolution[0]}x{min_resolution[1]}."
        )

    # Convert to grayscale for frequency & lighting analysis
    if len(image_input.shape) == 3 and image_input.shape[2] == 3:
        gray = cv2.cvtColor(image_input, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_input

    # 2. Blur Detection (Laplacian Variance)
    # Higher variance indicates sharp edges; lower variance indicates blur.
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if blur_score < blur_threshold:
        warnings.append(f"Image appears blurry (sharpness score: {blur_score:.1f} / {blur_threshold}).")

    # 3. Exposure / Brightness Check
    brightness_score = float(np.mean(gray))
    if brightness_score < min_brightness:
        warnings.append(f"Image is under-exposed/dark (luminance: {brightness_score:.1f}).")
    elif brightness_score > max_brightness:
        warnings.append(f"Image is over-exposed/washed out (luminance: {brightness_score:.1f}).")

    # Image is considered valid for AI analysis if no critical quality warnings exist
    is_valid = len(warnings) == 0

    return ImageQualityResult(
        is_valid=is_valid,
        blur_score=round(blur_score, 2),
        brightness_score=round(brightness_score, 2),
        resolution=(width, height),
        warnings=warnings
    )
