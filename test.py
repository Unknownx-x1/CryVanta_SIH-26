import unittest

from risk_engine import calculate_risk, highest_risk


class RiskEngineTest(unittest.TestCase):
    def test_calculate_risk_contract_enums(self):
        self.assertEqual(calculate_risk(1500), "LOW")
        self.assertEqual(calculate_risk(900), "MEDIUM")
        self.assertEqual(calculate_risk(300), "HIGH")
        self.assertEqual(calculate_risk(100), "CRITICAL")

    def test_highest_risk(self):
        self.assertEqual(highest_risk(["LOW", "HIGH", "MEDIUM"]), "HIGH")
        self.assertEqual(highest_risk([]), "LOW")


if __name__ == "__main__":
    unittest.main()
