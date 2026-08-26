from __future__ import annotations

import unittest

from app.services import qanun
from app.services import zij


def synthetic_row() -> dict:
    """A hand-built zīj row: Sun exalted in Aries, Moon in Libra (its debility),
    Saturn in Aries — so every dignity branch and the Saturn special drishti
    can be checked without depending on the ephemeris."""
    def body(lon_s: float) -> dict:
        return {
            "lon_t": lon_s + 24.0, "lon_s": lon_s, "dist_au": 1.0,
            "retro": False, "sign": {}, "nakshatra": "",
        }

    return {
        "jd": 2451545.0,
        "ayanamsa": 24.0,
        "bodies": {
            "Sun": body(5.0),        # Aries — exalted (R-1.13)
            "Moon": body(215.0),     # Scorpio — debilitated (7th from Taurus)
            "Mercury": body(200.0),  # Libra
            "Venus": body(40.0),     # Taurus — own sign
            "Mars": body(5.0),       # Aries — own sign (lord)
            "Jupiter": body(320.0),  # Aquarius
            "Saturn": body(10.0),    # Aries
        },
        "rahu_lon_s": 0.0, "ketu_lon_s": 180.0, "moon_dist_er": 60.0,
        "provenance": {"engine": "test", "constants_sha256": "x"},
    }


class QanunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = qanun.factors_payload(synthetic_row(), lat=28.6, lon=77.2)
        self.by_name = {f["factor"]: f for f in self.payload["factors"]}

    def test_every_factor_has_tier_and_citation(self) -> None:
        for f in self.payload["factors"]:
            self.assertIn(f["tier"], ("measured", "doctrine", "hypothesis"), f["factor"])
            self.assertTrue(f["citation"], f["factor"])

    def test_dignity_exaltation_and_debility(self) -> None:
        dign = self.by_name["dignity"]["value"]
        self.assertEqual(dign["Sun"]["dignity"], "exalted")
        self.assertEqual(dign["Moon"]["dignity"], "debilitated")
        self.assertEqual(dign["Venus"]["dignity"], "own sign")
        self.assertEqual(dign["Mercury"]["dignity"], "neutral")

    def test_drishti_saturn_full_sight_and_orb(self) -> None:
        chords = self.by_name["drishti"]["value"]
        # Moon is 8 houses from the Sun (Aries -> Scorpio): three-quarter sight.
        sun_to_moon = [c for c in chords if c["from"] == "Sun" and c["to"] == "Moon"]
        self.assertTrue(any(c["house"] == 8 and c["strength"] == 0.75 for c in sun_to_moon))
        # Mars's special: full sight on the 4th & 8th (R-2.13).
        mars_to_moon = [c for c in chords if c["from"] == "Mars" and c["to"] == "Moon"]
        self.assertTrue(any(
            c["house"] == 8 and c["strength"] == 1.0 and c["full_sight_special"]
            for c in mars_to_moon
        ))
        # No chord exceeds the 15-degree orb rule.
        self.assertTrue(all(c["orb_deg"] <= 15.0 for c in chords))
        # Rahu/Ketu never appear (R-2.13 covers the seven only).
        names = {c["from"] for c in chords} | {c["to"] for c in chords}
        self.assertNotIn("Rahu", names)
        self.assertNotIn("Ketu", names)

    def test_paksha_geometry(self) -> None:
        paksha = self.by_name["paksha"]["value"]
        self.assertEqual(paksha["paksha"], "Krishna (waning)")  # 180 < elong < 360

    def test_sect_requires_observer_and_reports_altitude(self) -> None:
        self.assertIn("kala_bala_sect", self.by_name)
        sect = self.by_name["kala_bala_sect"]
        self.assertEqual(sect["tier"], "doctrine")
        self.assertIn("sun_altitude_deg", sect["value"])

    def test_no_factor_asserts_a_verdict(self) -> None:
        # The engine reports placements and strengths only: no factor may be
        # named or worded as a prediction/verdict.
        banned = ("verdict", "will be", "prediction", "doom", "death")
        for f in self.payload["factors"]:
            blob = (f["factor"] + " " + f.get("note", "")).lower()
            for word in banned:
                self.assertNotIn(word, blob)


class ZijTests(unittest.TestCase):
    def test_row_is_tiered_and_provenanced(self) -> None:
        row = zij.zij_row(1787741820000)  # 2026-08-26 — inside the valid window
        self.assertEqual(row["tier"], "measured")
        self.assertIn("constants_sha256", row["provenance"])
        self.assertIn("err_arcmin", row["bodies"]["Moon"])

    def test_outside_window_is_extrapolated(self) -> None:
        row = zij.zij_row(4102444800000)  # 2100-01-01 — beyond 2050
        self.assertEqual(row["tier"], "extrapolated")

    def test_manifest_pins_constants_and_sample(self) -> None:
        m = zij.manifest()
        self.assertEqual(m["engine"], zij.ENGINE_VERSION)
        self.assertEqual(len(m["constants_sha256"]), 64)
        self.assertEqual(len(m["pinned_sample"]["sha256"]), 64)

    def test_window_rows_are_stable(self) -> None:
        a = zij.zij_row(1787741820000)
        b = zij.zij_row(1787741820000)
        self.assertEqual(a["bodies"]["Sun"]["lon_s"], b["bodies"]["Sun"]["lon_s"])


if __name__ == "__main__":
    unittest.main()
