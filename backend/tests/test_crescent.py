from __future__ import annotations

import math
import unittest
from datetime import datetime, timezone

from app.services import crescent
from app.services import sky_engine


def ms(y: int, m: int, d: int) -> int:
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


DELHI = (28.6139, 77.2090, 216.0)


class CrescentTests(unittest.TestCase):
    def test_raw_observables_in_physical_ranges(self) -> None:
        result = crescent.visibility(ms(2026, 9, 12), *DELHI)
        s = result["at_sunset"]
        self.assertTrue(-90 <= s["moon_alt_deg"] <= 90)
        self.assertTrue(0 <= s["relative_azimuth_deg"] <= 180)
        self.assertTrue(0 <= s["elongation_arcl_deg"] <= 180)
        self.assertTrue(0 <= s["illumination_fraction"] <= 1)
        self.assertGreater(s["moon_age_hours"], 24)  # Sep 12 evening: ~34h old

    def test_visibility_class_grows_over_new_moon(self) -> None:
        # Around the Sep 2026 new moon: q must increase night over night.
        q11 = crescent.visibility(ms(2026, 9, 11), *DELHI)["yallop_q"]["q"]
        q12 = crescent.visibility(ms(2026, 9, 12), *DELHI)["yallop_q"]["q"]
        q13 = crescent.visibility(ms(2026, 9, 13), *DELHI)["yallop_q"]["q"]
        self.assertLess(q11, q12)
        self.assertLess(q12, q13)
        self.assertLess(q11, 0)   # 10h crescent: not naked-eye
        self.assertGreater(q13, 0.25)

    def test_pre_conjunction_age_is_negative(self) -> None:
        result = crescent.visibility(ms(2026, 9, 10), *DELHI)
        self.assertLess(result["at_sunset"]["moon_age_hours"], 0)

    def test_classification_is_tiered_hypothesis(self) -> None:
        result = crescent.visibility(ms(2026, 9, 12), *DELHI)
        self.assertEqual(result["yallop_q"]["tier"], "hypothesis")
        self.assertIn("not a religious ruling", result["disclaimer"])


class ObservatoryMathTests(unittest.TestCase):
    def test_gmst_known_value(self) -> None:
        # GMST at 2000-01-01 12:00 UT ≈ 280.46 deg (caput of the standard formula).
        g = sky_engine.gmst_deg(2451545.0)
        self.assertAlmostEqual(g, 280.46, delta=0.05)

    def test_altaz_sun_at_noon_equator_equinox(self) -> None:
        # Sun near zenith at the equator at the 2000 equinox ~ noon local.
        ms_eq = int(datetime(2000, 3, 20, 12, 0, tzinfo=timezone.utc).timestamp() * 1000)
        lon_t = sky_engine.sun_ecliptic(ms_eq)
        ra, dec = sky_engine.ecliptic_to_equatorial(lon_t, 0.0)
        jd = sky_engine.julian_day(ms_eq)
        alt, _az = sky_engine.altaz(ra, dec, jd, 0.0, 0.0)
        self.assertGreater(alt, 85.0 if abs(dec) < 1.5 else alt)  # near-zenith sanity
        self.assertTrue(-1.5 < dec < 1.5)  # equinox declination ~0

    def test_topocentric_parallax_dips_altitude(self) -> None:
        # Equatorial horizontal parallax ~0.95 deg, scaled by cos(altitude).
        dipped = sky_engine.topocentric_alt(30.0, 60.27)  # mean lunar distance
        self.assertAlmostEqual(dipped, 30.0 - 0.95 * math.cos(math.radians(30.0)), delta=0.05)

    def test_find_event_bisection(self) -> None:
        fn = lambda t: (t - 5_000) / 1_000.0  # crosses 0 at t=5000
        found = sky_engine.find_event(0, 10_000, fn, 0.0, rising=True)
        self.assertIsNotNone(found)
        self.assertTrue(abs(found - 5_000) < 2_100)


if __name__ == "__main__":
    unittest.main()
