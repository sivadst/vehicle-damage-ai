"""
Vehicle Damage Cost & Triage Estimation Module.

Provides deterministic mapping and heuristic estimation for:
- Estimated repair cost range (USD)
- Estimated labor time (business days)
- Claims processing priority level (P1 Critical to P3 Routine)
"""

from typing import Dict, Any, Tuple

# Comprehensive cost, time, and priority lookup table
TRIAGE_MATRIX: Dict[str, Dict[str, Dict[str, str]]] = {
    "no_damage": {
        "minor": {"cost": "$0", "time": "N/A", "priority": "P3 - Auto-Approve"},
        "moderate": {"cost": "$0", "time": "N/A", "priority": "P3 - Auto-Approve"},
        "severe": {"cost": "$0", "time": "N/A", "priority": "P3 - Auto-Approve"}
    },
    "scratch": {
        "minor": {"cost": "$100 - $300", "time": "1 Business Day", "priority": "P3 - Routine"},
        "moderate": {"cost": "$300 - $800", "time": "1 - 2 Business Days", "priority": "P3 - Routine"},
        "severe": {"cost": "$800 - $1,500", "time": "2 - 3 Business Days", "priority": "P2 - Standard"}
    },
    "dent": {
        "minor": {"cost": "$200 - $500", "time": "1 Business Day", "priority": "P3 - Routine"},
        "moderate": {"cost": "$500 - $1,200", "time": "2 - 3 Business Days", "priority": "P2 - Standard"},
        "severe": {"cost": "$1,200 - $3,000", "time": "3 - 5 Business Days", "priority": "P2 - Standard"}
    },
    "broken_glass": {
        "minor": {"cost": "$150 - $400", "time": "Same Day (Mobile)", "priority": "P3 - Routine"},
        "moderate": {"cost": "$400 - $800", "time": "1 Business Day", "priority": "P2 - Standard"},
        "severe": {"cost": "$800 - $1,500", "time": "1 - 2 Business Days", "priority": "P1 - Expedited"}
    },
    "broken_lamp": {
        "minor": {"cost": "$100 - $300", "time": "Same Day", "priority": "P3 - Routine"},
        "moderate": {"cost": "$300 - $800", "time": "1 Business Day", "priority": "P2 - Standard"},
        "severe": {"cost": "$800 - $1,200", "time": "1 - 2 Business Days", "priority": "P2 - Standard"}
    },
    "crushed_panel": {
        "minor": {"cost": "$1,000 - $2,500", "time": "3 - 5 Business Days", "priority": "P2 - Standard"},
        "moderate": {"cost": "$2,500 - $5,000", "time": "5 - 8 Business Days", "priority": "P1 - Expedited"},
        "severe": {"cost": "$5,000+", "time": "10+ Business Days", "priority": "P1 - Critical Review"}
    }
}


def estimate_cost(damage_type: str, severity: str) -> str:
    """Returns estimated repair cost string for given damage type and severity.

    Args:
        damage_type (str): Category of damage (e.g. 'scratch', 'dent').
        severity (str): Severity rating ('minor', 'moderate', 'severe').

    Returns:
        str: Cost range in USD.
    """
    return TRIAGE_MATRIX.get(damage_type, {}).get(severity, {}).get("cost", "Unknown")


def get_claim_triage_info(damage_type: str, severity: str) -> Dict[str, str]:
    """Retrieves complete triage metadata including cost, repair time, and priority.

    Args:
        damage_type (str): Category of damage.
        severity (str): Severity level.

    Returns:
        Dict[str, str]: Dictionary containing 'cost', 'time', and 'priority'.
    """
    default_info = {"cost": "Unknown", "time": "TBD", "priority": "P2 - Standard"}
    return TRIAGE_MATRIX.get(damage_type, {}).get(severity, default_info)
