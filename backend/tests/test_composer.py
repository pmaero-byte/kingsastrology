from __future__ import annotations

import unittest
from pathlib import Path

from app.services.composer import compose_reading
from app.services.rule_loader import RuleRepository


ROOT = Path(__file__).resolve().parents[2]


class ComposerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = RuleRepository(ROOT / "rules")

    def test_composer_rejects_draft_rules_for_production(self) -> None:
        with self.assertRaises(ValueError):
            compose_reading(self.repository, ["R-12.3"])

    def test_composer_can_build_development_preview_from_draft_rules(self) -> None:
        reading = compose_reading(self.repository, ["R-12.3"], allow_draft=True)

        self.assertFalse(reading["provenance"]["runtime_ai"])
        self.assertEqual(reading["artifact_status"], "draft_preview")
        self.assertEqual(reading["sections"][0]["id"], "your_strengths")
        self.assertEqual(reading["sections"][0]["claims"][0]["rule_id"], "R-12.3")


if __name__ == "__main__":
    unittest.main()
