"""Regression checks for decision-critical package rejection gates (synthetic data)."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "compare_packages", Path(__file__).parents[1] / "scripts/compare_packages.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PackageGuardTests(unittest.TestCase):
    def base(self):
        positions = ["GK"] * 2 + ["DEF"] * 5 + ["MID"] * 5 + ["FWD"] * 3
        return {
            "squad": [{"id": i, "position": p, "team": i, "sell_price": 50}
                      for i, p in enumerate(positions)],
            "bank": 2, "free_transfers": 2,
            "rules": {"hit_cost": 4, "max_per_club": 3},
            "packages": [{
                "id": "synthetic_only", "transfers": [{
                    "out": 7, "in": {"id": 20, "position": "MID",
                                    "team": 20, "buy_price": 50}}],
                "gross_xp_gain": None}]}

    def assert_rejected(self, data, error):
        result = module.compare(data)[1]
        self.assertFalse(result["feasible"])
        self.assertIn(error, result["errors"])
        self.assertIsNone(result["bank_after"])
        self.assertIsNone(result["net_xp_gain_vs_roll"])

    def test_forecast_without_source_cannot_produce_net_gain(self):
        data = self.base()
        data["packages"][0]["gross_xp_gain"] = 4
        self.assert_rejected(data, "forecast_source_missing")

    def test_fourth_player_from_club_is_rejected(self):
        data = self.base()
        for player in data["squad"][:3]:
            player["team"] = 99
        data["packages"][0]["transfers"][0]["in"]["team"] = 99
        self.assert_rejected(data, "club_limit_exceeded")

    def test_position_change_cannot_create_illegal_squad(self):
        data = self.base()
        data["packages"][0]["transfers"][0]["in"]["position"] = "FWD"
        self.assert_rejected(data, "invalid_squad_positions")

if __name__ == "__main__":
    unittest.main()
