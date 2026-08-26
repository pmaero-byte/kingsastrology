from __future__ import annotations

import unittest


class CalendarAnchorTests(unittest.TestCase):
    def setUp(self) -> None:
        from app.services import calendars as cal

        self.cal = cal

    def test_gregorian_jd_roundtrip_epoch(self) -> None:
        # JD 2451545.0 == 2000-01-01 12:00 UT (Gregorian); the converter
        # returns the noon-based Julian day of the date.
        self.assertAlmostEqual(self.cal.jd_from_gregorian(2000, 1, 1), 2451545.0, places=4)
        self.assertEqual(self.cal.gregorian_from_jd(2451545.0), (2000, 1, 1))

    def test_julian_calendar_oct_1582(self) -> None:
        # Julian calendar: 1582-10-05 (Julian) == 1582-10-15 (Gregorian).
        jd = self.cal.jd_from_gregorian(1582, 10, 15)
        self.assertEqual(self.cal.julian_calendar_from_jd(jd), (1582, 10, 5))

    def test_hijri_epoch_anchor(self) -> None:
        # 1 Muharram 1 AH == JD 1948440.5 (tabular epoch, 16 July 622 CE).
        h = self.cal.hijri_from_jd(1948440.5)
        self.assertEqual((h["year"], h["month"], h["day"]), (1, 1, 1))

    def test_kali_epoch_anchor(self) -> None:
        k = self.cal.kali_from_jd(588465.5)
        self.assertEqual(k["ahargana_days"], 0.0)

    def test_saka_new_year_2000(self) -> None:
        # Chaitra 1, Śaka 1922 == 21 March 2000 (Gregorian leap year → 21 March).
        jd = self.cal.jd_from_gregorian(2000, 3, 21)
        s = self.cal.saka_from_jd(jd)
        self.assertEqual((s["year"], s["month"], s["day"]), (1922, 1, 1))

    def test_jalali_known_pair(self) -> None:
        # Nowruz 2026 (astronomical 20/21 Mar) — tabular Birashk: 1 Farvardin 1405.
        jd = self.cal.jd_from_gregorian(2026, 3, 21)
        j = self.cal.jalali_from_jd(jd)
        self.assertIn((j["year"], j["month"], j["day"]), [(1405, 1, 1), (1404, 12, 30)])
        self.assertEqual(j["yazdgirdi_year"], j["year"] + 1301)

    def test_vikram_year_direction(self) -> None:
        v = self.cal.vikram_samvat(self.cal.jd_from_gregorian(2026, 8, 26))
        self.assertEqual(v["year"], 2083)
        v2 = self.cal.vikram_samvat(self.cal.jd_from_gregorian(2026, 1, 10))
        self.assertEqual(v2["year"], 2082)


if __name__ == "__main__":
    unittest.main()
