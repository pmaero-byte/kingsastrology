"""
Amendment II — One timestamp, many calendars (Tafhīm Protocol §IV).

Every converter states its algorithm and its error. Calendar arithmetic is
[measured]; where a tabular calendar can disagree with an observational one
by a day, that is printed, not hidden.
"""
from __future__ import annotations

import math
from typing import Any

from app.services import sky_engine

ENGINE_VERSION = "calendars-1.0.0"


def jd_from_gregorian(y: int, m: int, d: int) -> float:
    """Julian day at noon UT for a proleptic Gregorian date (Fliegel-Van Flandern)."""
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


def gregorian_from_jd(jd: float) -> tuple[int, int, int]:
    """Proleptic Gregorian calendar date of the Julian day (at noon)."""
    z = int(jd + 0.5)
    f = jd + 0.5 - z
    alpha = int((z - 1867216.25) / 36524.25)
    a = z + 1 + alpha - alpha // 4
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day = b - d - int(30.6001 * e)
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    return year, month, day


def julian_calendar_from_jd(jd: float) -> tuple[int, int, int]:
    """Julian-calendar date of a Julian day."""
    c = jd + 32082.5
    d = c % 1.0
    c = int(c)
    a = (4 * c + 3) // 1461
    b = c - (1461 * a) // 4
    e = (5 * b + 2) // 153
    day = b - (153 * e + 2) // 5 + 1
    month = e + 3 if e < 10 else e - 9
    year = a - 4800 + (0 if month > 2 else 1)
    return year, month, day


# --------------------------------------------------------------- Hijrī (tabular)

HIJRI_EPOCH_JD = 1948440.5  # 1 Muharram 1 AH (civil tabular, 16 July 622 CE Julian)
HIJRI_MONTHS = ["Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani", "Jumada al-Ula",
                "Jumada al-Akhirah", "Rajab", "Shaban", "Ramadan", "Shawwal",
                "Dhu al-Qadah", "Dhu al-Hijjah"]


def _hijri_leap(year: int) -> bool:
    # 30-year cycle; leap years 2,5,7,10,13,16,18,21,24,26,29.
    return (11 * year + 3) % 30 in (2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29)


def hijri_from_jd(jd: float) -> dict[str, Any]:
    days = math.floor(jd - HIJRI_EPOCH_JD)  # days since 1 Muharram 1 AH
    year = (30 * days // 10631) + 1
    rem = days - (10631 * (year - 1)) // 30
    month = 1
    while month <= 12:
        length = 30 if _hijri_leap(year) and month == 12 else 29
        if rem < length:
            break
        rem -= length
        month += 1
    return {
        "era": "Hijrī (tabular, civil)",
        "year": int(year), "month": int(month), "day": int(rem) + 1,
        "month_name": HIJRI_MONTHS[int(month) - 1],
        "algorithm": "tabular 30-year cycle, epoch JD 1948440.5",
        "err": "±1 day vs local moon-sighting; use /api/v1/crescent for the criterion",
    }


# ------------------------------------------------- Solar Hijri / Jalali (Birashk)

JALALI_MONTHS = ["Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar",
                 "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"]


def jalali_from_jd(jd: float) -> dict[str, Any]:
    gy, gm, gd = gregorian_from_jd(jd)
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (355666 + 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100
            + (gy2 + 399) // 400 + gd + g_d_m[gm - 1])
    jy = -1595 + 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    leap = (jy % 33) in (1, 5, 9, 13, 17, 22, 26, 30)
    month_lengths = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29 if not leap else 30]
    jm = 1
    for length in month_lengths:
        if days < length:
            break
        days -= length
        jm += 1
    return {
        "era": "Solar Hijrī (Jalālī)",
        "year": int(jy), "month": int(jm), "day": int(days) + 1,
        "month_name": JALALI_MONTHS[int(jm) - 1],
        "algorithm": "Birashk tabular (2820-year cycle)",
        "err": "±1 day vs the astronomical equinox calendar in some years",
        "yazdgirdi_year": int(jy) + 1301,
    }


# ------------------------------------------------------------- Vikram Saṃvat

def vikram_samvat(jd: float) -> dict[str, Any]:
    y, m, d = gregorian_from_jd(jd)
    # Solar-year convention: the count increments at Mesha saṅkrānti (~14 April).
    vs = y + 57 if (m, d) >= (4, 14) else y + 56
    return {
        "era": "Vikram Saṃvat (solar-year convention)",
        "year": vs,
        "algorithm": "Gregorian year + 57/56, increment ≈ 14 April (Mesha saṅkrānti)",
        "err": "approximate: the true saṅkrānti moment varies ±1 day; "
               "lunar-month Vikram reckoning not implemented",
    }


# --------------------------------------------------------------- Śaka (official)

SAKA_MONTHS = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
               "Ashwin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"]


def saka_from_jd(jd: float) -> dict[str, Any]:
    gy, _, _ = gregorian_from_jd(jd)
    # Śaka new year: Chaitra 1 = 22 March (21 March in a Gregorian leap year,
    # when Chaitra carries 31 days).
    leap = (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0
    new_year_jd = jd_from_gregorian(gy, 3, 21 if leap else 22)
    if jd < new_year_jd:
        gy -= 1
        leap = (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0
        new_year_jd = jd_from_gregorian(gy, 3, 21 if leap else 22)
    days = int(jd - new_year_jd)
    lengths = [31 if leap else 30] + [31] * 5 + [30] * 6
    month = 1
    for length in lengths:
        if days < length:
            break
        days -= length
        month += 1
    return {
        "era": "Śaka (Indian civil)",
        "year": gy - 78, "month": month, "day": days + 1,
        "month_name": SAKA_MONTHS[month - 1],
        "algorithm": "Indian reform calendar, Chaitra 1 = 22/23 March",
        "err": "exact within its own convention (no observation)",
    }


# ------------------------------------------------------------- Kali-yuga count

KALI_EPOCH_JD = 588465.5  # midnight of 17/18 Feb 3102 BCE (Julian), the classical epoch


def kali_from_jd(jd: float) -> dict[str, Any]:
    ahargana = jd - KALI_EPOCH_JD
    return {
        "era": "Kali-yuga (classical epoch)",
        "ahargana_days": round(ahargana, 1),
        "year_approx": int(ahargana // 365.25) + 1,
        "algorithm": "ahargana = JD − 588465.5; year ≈ ahargana/365.25 (mean-year, "
                     "no saṅkrānti precision)",
        "err": "day-count exact for the classical epoch; year count approximate",
    }


# ------------------------------------------------------------------- assembly

def all_calendars(jd: float) -> dict[str, Any]:
    gy, gm, gd = gregorian_from_jd(jd)
    jy, jm, jdj = julian_calendar_from_jd(jd)
    return {
        "jd": round(jd, 5),
        "gregorian": {"year": gy, "month": gm, "day": gd},
        "julian_calendar": {"year": jy, "month": jm, "day": jdj},
        "hijri": hijri_from_jd(jd),
        "jalali": jalali_from_jd(jd),
        "vikram_samvat": vikram_samvat(jd),
        "saka": saka_from_jd(jd),
        "kali": kali_from_jd(jd),
        "provenance": {"engine": ENGINE_VERSION, "runtime_ai": False},
    }
