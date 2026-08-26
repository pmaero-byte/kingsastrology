from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.services.review_store import ReviewStore


class ReviewStoreTests(unittest.TestCase):
    def test_save_and_reload_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reviews.json"
            store = ReviewStore(path)

            saved = store.save(
                "R-12.3",
                decision="approved",
                comments="Faithful to the verse.",
                improvements="Ready after scholar sign-off.",
                reviewer="Reviewer",
            )
            reloaded = ReviewStore(path).get("R-12.3")

            self.assertEqual(saved.decision, "approved")
            self.assertEqual(reloaded.comments, "Faithful to the verse.")
            self.assertEqual(reloaded.improvements, "Ready after scholar sign-off.")
            self.assertEqual(reloaded.reviewer, "Reviewer")

    def test_summary_counts_unreviewed_missing_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ReviewStore(Path(tmp) / "reviews.json")
            store.save(
                "R-12.3",
                decision="needs_improvement",
                comments="Needs condition cleanup.",
                improvements="Clarify precedence.",
                reviewer="Reviewer",
            )

            summary = store.summary(["R-12.3", "R-12.4"])

            self.assertEqual(summary["needs_improvement"], 1)
            self.assertEqual(summary["unreviewed"], 1)


if __name__ == "__main__":
    unittest.main()
