from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.services.brief import daily_brief


def ms(y: int, m: int, d: int, h: int = 12) -> int:
    return int(datetime(y, m, d, h, tzinfo=timezone.utc).timestamp() * 1000)


DELHI = (28.6139, 77.2090, 216.0)


class DailyBriefTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ts = ms(2026, 8, 27)

    def test_all_three_languages_render(self) -> None:
        for lang in ("en", "hi", "ar"):
            b = daily_brief(self.ts, *DELHI, lang)
            self.assertEqual(b["lang"], lang)
            self.assertEqual(len(b["lines"]), 4)
            for line in b["lines"]:
                self.assertTrue(line["text"].strip(), f"{lang} empty line")

    def test_every_line_is_tiered(self) -> None:
        b = daily_brief(self.ts, *DELHI)
        tiers = [line["tier"] for line in b["lines"]]
        self.assertIn("measured", tiers)
        self.assertIn("convention", tiers)

    def test_determinism_same_instant_same_words(self) -> None:
        a = daily_brief(self.ts, *DELHI, "hi")
        b = daily_brief(self.ts, *DELHI, "hi")
        self.assertEqual(a, b)

    def test_no_flattery_no_predictions(self) -> None:
        banned = ["will be great", "good luck", "bad day", "avoid everything",
                  "you should", "success awaits", "doom", "great fortune"]
        for lang in ("en", "hi", "ar"):
            b = daily_brief(self.ts, *DELHI, lang)
            blob = " ".join(l["text"] for l in b["lines"]) + b["tomorrow"]["text"]
            for phrase in banned:
                self.assertNotIn(phrase, blob.lower(), f"{lang}: {phrase}")

    def test_skill_statement_present_and_honest(self) -> None:
        b = daily_brief(self.ts, *DELHI)
        self.assertIn("predicts nothing", b["skill_statement"])
        self.assertFalse(b["provenance"]["runtime_ai"])

    def test_tomorrow_is_measured_and_differs(self) -> None:
        b = daily_brief(self.ts, *DELHI)
        self.assertEqual(b["tomorrow"]["tier"], "measured")
        t_today = b["facts"]["tithi"]["label"]
        self.assertIn("Tomorrow", b["tomorrow"]["en"])

    def test_unknown_language_falls_back_to_english(self) -> None:
        b = daily_brief(self.ts, *DELHI, "fr")
        self.assertEqual(b["lang"], "en")

    def test_facts_block_exposes_machinery(self) -> None:
        b = daily_brief(self.ts, *DELHI)
        for limb in ("tithi", "nakshatra", "yoga", "karana", "sun_sign", "moon_sign"):
            self.assertIn(limb, b["facts"])


if __name__ == "__main__":
    unittest.main()
