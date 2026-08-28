from __future__ import annotations

import unittest
from pathlib import Path

from app.services.rule_loader import RuleRepository


ROOT = Path(__file__).resolve().parents[2]


class RuleLoaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = RuleRepository(ROOT / "rules")

    def test_repository_loads_only_chapters_8_to_20(self) -> None:
        self.assertGreaterEqual(min(self.repository.chapters), 8)
        self.assertLessEqual(max(self.repository.chapters), 20)
        self.assertTrue(set(range(1, 8)).isdisjoint(self.repository.chapters))

    def test_scope_reports_existing_draft_rule_corpus_and_missing_chapter_20(self) -> None:
        scope = self.repository.scope()

        self.assertEqual(scope.loaded_chapters, list(range(8, 21)))
        self.assertEqual(scope.missing_chapters, [])
        self.assertGreaterEqual(scope.total_rules, 290)
        # M3: the first scholar-reviewed rules are frozen (19 as of 2026-08-29).
        self.assertEqual(scope.verified_rules, 19)
        self.assertEqual(scope.draft_rules, scope.total_rules - 19)
        self.assertEqual(len(self.repository.list_rules()), scope.total_rules)

    def test_legacy_chapter_mismatches_are_reported_as_warnings(self) -> None:
        scope = self.repository.scope()

        self.assertTrue(any("ch08_dasa.md" in warning for warning in scope.warnings))
        # The "Ch 4" mislabeling was corrected to each file's own chapter by
        # the scholar review; citation warnings must be gone.
        self.assertFalse(any("citation" in warning for warning in scope.warnings))
        # Rule-id prefixes were normalized in the files themselves.
        self.assertFalse(any("normalized legacy rule id" in warning for warning in scope.warnings))

    def test_can_filter_rules_by_chapter_and_classification(self) -> None:
        strength_rules = self.repository.list_rules(chapter=12, classification="strength")

        self.assertTrue(strength_rules)
        self.assertTrue(all(rule.chapter == 12 for rule in strength_rules))
        self.assertTrue(all(rule.classification == "strength" for rule in strength_rules))


if __name__ == "__main__":
    unittest.main()
