"""
Repository System Health & Import Verification Script.
"""

import sys
import io
from pathlib import Path

# Fix Windows console UTF-8 output encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def check():
    """Validates that all core modules, utilities, and constants load correctly."""
    from src.constants import CLASSES, SEVERITIES, LOCATIONS
    from app.utils.cost_mapping import estimate_cost, get_claim_triage_info

    print("✅ Core ML constants loaded successfully!")
    print(f"   Classes ({len(CLASSES)}): {CLASSES}")
    print(f"   Severities ({len(SEVERITIES)}): {SEVERITIES}")
    print(f"   Locations ({len(LOCATIONS)}): {LOCATIONS}")

    triage = get_claim_triage_info("dent", "severe")
    print(f"✅ Triage Engine functional! Dent (Severe) -> Cost: {triage['cost']}, Time: {triage['time']}, Priority: {triage['priority']}")

    print("\n🎉 Repository System Health Verification Passed!")


if __name__ == "__main__":
    check()
