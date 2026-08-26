from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.services import panchanga
from app.services import periods


def ms(y: int, m: int, d: int, h: int = 12, mi: int = 0) -> int:
    return int(datetime(y, m, d, h, mi, tzinfo=timezone.utc).timestamp() * 1000)


DELHI = (28.6139, 77.2090, 216.0)


class PanchangaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = panchanga.now_strip(ms(2026, 8, 26, 12, 23), *DELHI)

    def test_panchanga_limb_structure(self) -> None:
        for limb in ("tithi", "nakshatra", "yoga", "karana"):
            self.assertIn(limb, self.now)
        self.assertEqual(self.now["tithi"]["label"], "Shukla Chaturdashi")
        self.assertEqual(self.now["nakshatra"]["name"], "Shravana")
        self.assertEqual(self.now["vara"]["lord"], "Mercury")  # Wednesday

    def test_tithi_names_cover_thirty(self) -> None:
        self.assertEqual(panchanga.tithi_of(0.0)["name"], "Pratipada")
        self.assertEqual(panchanga.tithi_of(6.0)["name"], "Pratipada")
        self.assertEqual(panchanga.tithi_of(168.0)["name"], "Purnima")
        self.assertEqual(panchanga.tithi_of(174.0)["name"], "Purnima")
        self.assertEqual(panchanga.tithi_of(180.0)["name"], "Pratipada")  # Krishna
        self.assertEqual(panchanga.tithi_of(354.0)["name"], "Amavasya")
        self.assertEqual(panchanga.tithi_of(90.0)["name"], "Ashtami")

    def test_karana_cycle(self) -> None:
        self.assertEqual(panchanga.karana_of(0.0)["name"], "Kimstughna")
        self.assertEqual(panchanga.karana_of(6.0)["name"], "Bava")
        self.assertEqual(panchanga.karana_of(12.0)["name"], "Balava")
        self.assertEqual(panchanga.karana_of(354.0)["name"], "Naga")

    def test_rise_set_pairs_one_solar_day(self) -> None:
        rs = self.now["rise_set"]
        self.assertIsNotNone(rs["sunrise"])
        self.assertIsNotNone(rs["sunset"])
        self.assertGreater(rs["sunset"], rs["sunrise"])
        self.assertLess(rs["sunset"] - rs["sunrise"], 14 * 3600_000)
        self.assertGreater(rs["sunset"] - rs["sunrise"], 9 * 3600_000)

    def test_muhurta_windows_are_ordered(self) -> None:
        m = self.now["muhurtas"]
        self.assertLess(m["brahma"]["ends"], m["brahma"]["starts"] + 48 * 60_000 + 1)
        self.assertLess(m["abhijit"]["starts"], m["abhijit"]["ends"])
        self.assertGreater(m["abhijit"]["starts"], self.now["rise_set"]["sunrise"])
        self.assertLess(m["abhijit"]["ends"], self.now["rise_set"]["sunset"])

    def test_rahu_kaal_inside_daylight(self) -> None:
        rk = self.now["rahu_kaal"]
        rs = self.now["rise_set"]
        self.assertGreaterEqual(rk["starts"], rs["sunrise"])
        self.assertLessEqual(rk["ends"], rs["sunset"])

    def test_conventions_are_labelled_not_doctrine(self) -> None:
        for block in (self.now["hora"], self.now["muhurtas"], self.now["rahu_kaal"]):
            self.assertEqual(block.get("tier"), "convention")
        self.assertIn("not Brihat", self.now["provenance"]["conventions_note"])

    def test_day_transitions_within_day(self) -> None:
        events = panchanga.day_transitions(ms(2026, 8, 26, 12))
        for e in events:
            self.assertIn(e["kind"], ("tithi", "nakshatra"))
            self.assertTrue(0 <= e["at"] % 86_400_000 < 86_400_000)


class PeriodTests(unittest.TestCase):
    def test_week_has_seven_days_and_events_sorted(self) -> None:
        w = periods.report_week(ms(2026, 8, 26), *DELHI)
        self.assertEqual(len(w["days"]), 7)
        self.assertEqual([d["lord"] for d in w["days"]],
                         ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"])
        ats = [e["at"] for e in w["events"]]
        self.assertEqual(ats, sorted(ats))

    def test_month_finds_real_august_2026_lunations(self) -> None:
        m = periods.report_month(ms(2026, 8, 26), *DELHI)
        kinds = [(e["kind"], e["eclipse_hint"]["indicator"]) for e in m["lunations"]]
        self.assertIn(("new_moon", "likely"), kinds)    # Aug 12 2026 total solar
        self.assertIn(("full_moon", "likely"), kinds)   # Aug 28 2026 total lunar

    def test_year_finds_2027_eclipse_season(self) -> None:
        y = periods.report_year(ms(2026, 8, 26), *DELHI)
        likely = [e for e in y["lunations"] if e["eclipse_hint"]["indicator"] == "likely"]
        self.assertGreaterEqual(len(likely), 2)  # Feb 2027 solar + Mar 2027 lunar
        self.assertTrue(all(e["body"] != "Moon" for e in y["ingresses"]))  # no Moon noise

    def test_events_carry_tiers(self) -> None:
        m = periods.report_month(ms(2026, 8, 26), *DELHI)
        for e in m["events"]:
            if "eclipse_hint" in e:
                self.assertEqual(e["eclipse_hint"]["tier"], "measured")


if __name__ == "__main__":
    unittest.main()
