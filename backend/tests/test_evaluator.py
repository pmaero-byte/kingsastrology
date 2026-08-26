from __future__ import annotations

import unittest
from pathlib import Path

from app.services.evaluator import evaluate_chart
from app.services.rule_loader import RuleRepository


ROOT = Path(__file__).resolve().parents[2]


class EvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = RuleRepository(ROOT / "rules")

    def test_matches_chapter_20_house_tables_from_planet_facts(self) -> None:
        result = evaluate_chart(
            self.repository,
            {
                "planets": [
                    {"name": "Sun", "sign": "Aries", "house": 1},
                    {"name": "Jupiter", "sign": "Cancer", "house": 10},
                ],
            },
        )

        self.assertIn("R-20.1", result.matched_rule_ids)
        self.assertIn("R-20.5", result.matched_rule_ids)
        self.assertIn("R-20.8", result.matched_rule_ids)
        self.assertIn("R-20.9", result.matched_rule_ids)
        self.assertIn("R-20.10", result.matched_rule_ids)

    def test_matches_existing_planet_in_sign_rule(self) -> None:
        result = evaluate_chart(
            self.repository,
            {
                "planets": [
                    {"name": "Sun", "sign": "Aries", "house": 1},
                ],
            },
        )

        self.assertIn("R-18.Sun.Aries", result.matched_rule_ids)

    def test_can_compose_from_evaluated_chart_when_drafts_are_allowed(self) -> None:
        result = evaluate_chart(
            self.repository,
            {
                "planets": [
                    {"name": "Sun", "sign": "Aries", "house": 1},
                ],
            },
            compose=True,
            allow_draft=True,
        )

        self.assertIsNotNone(result.reading)
        assert result.reading is not None
        self.assertEqual(result.reading["artifact_status"], "draft_preview")


if __name__ == "__main__":
    unittest.main()
