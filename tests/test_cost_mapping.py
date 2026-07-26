"""
Unit tests for Cost & Triage Estimation module.
"""

import unittest
from app.utils.cost_mapping import estimate_cost, get_claim_triage_info


class TestCostMapping(unittest.TestCase):
    """Test suite for cost mapping and triage logic."""

    def test_estimate_cost_valid(self):
        """Tests cost range lookup for valid damage type and severity."""
        cost = estimate_cost("dent", "severe")
        self.assertEqual(cost, "$1,200 - $3,000")

    def test_estimate_cost_unknown(self):
        """Tests cost range lookup fallback for invalid inputs."""
        cost = estimate_cost("unknown_type", "minor")
        self.assertEqual(cost, "Unknown")

    def test_get_claim_triage_info(self):
        """Tests detailed triage dictionary retrieval."""
        triage = get_claim_triage_info("crushed_panel", "severe")
        self.assertIn("cost", triage)
        self.assertIn("time", triage)
        self.assertIn("priority", triage)
        self.assertEqual(triage["priority"], "P1 - Critical Review")


if __name__ == "__main__":
    unittest.main()
