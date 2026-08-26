"""
The daily almanac (pañcāṅga) and time-of-day divisions.

Two kinds of knowledge live here, never mixed:

  [measured]  tithi, nakshatra (+ pada), yoga, karana, elongations, rise/set
              moments, sign transitions — all derived from the validated
              zīj engine.
  [convention] hora (planetary hours), Rahu Kaal, Abhijit & Brahma muhurta —
              traditional timing conventions of general use. These are
              clearly labelled as convention, not Brihat Jataka doctrine,
              and assert nothing about fortune.
"""
from __future__ import annotations

import math
from typing import Any

from app.services import sky_engine

ENGINE_VERSION = "panchanga-1.0.0"
DAY = 86_400_000

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi",
]
PAKSHA_ENDS = {14: "Purnima", 29: "Amavasya"}

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
] * 3

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
]

MOVABLE_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]

VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
VARA_NAMES = ["Ravivara", "Somavara", "Mangalavara", "Budhavara",
              "Guruvara", "Shukravara", "Shanivara"]

CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Rahu Kaal: which 1-indexed eighth of daylight is ruled by Rahu, per weekday.
RAHU_KAAL_PART = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}


def _elongation(ms: int) -> float:
    ml, _, _ = sky_engine.moon_ecliptic(ms)
    sl = sky_engine.sun_ecliptic(ms)
    return (ml - sl) % 360.0


def tithi_of(elong: float) -> dict[str, Any]:
    idx = int(elong // 12.0)  # 0..29
    paksha = "Shukla" if idx < 15 else "Krishna"
    within = idx % 15
    if idx in PAKSHA_ENDS:
        name = PAKSHA_ENDS[idx]
    else:
        name = TITHI_NAMES[within]
    return {
        "index": idx + 1,
        "paksha": paksha,
        "name": name,
        "label": f"{paksha} {name}",
        "progress": round((elong - idx * 12.0) / 12.0, 4),
    }


def nakshatra_of_full(ms: int) -> dict[str, Any]:
    lon_s = sky_engine.wrap360(sky_engine.moon_ecliptic(ms)[0] - sky_engine.ayanamsa(sky_engine.julian_day(ms)))
    span = 360.0 / 27.0
    idx = int(lon_s // span)
    within = lon_s - idx * span
    pada = int(within // (span / 4.0)) + 1
    return {
        "index": idx + 1,
        "name": sky_engine.NAKSHATRAS[idx],
        "lord": NAKSHATRA_LORDS[idx],
        "pada": pada,
        "progress": round(within / span, 4),
    }


def yoga_of(ms: int) -> dict[str, Any]:
    ml, _, _ = sky_engine.moon_ecliptic(ms)
    sl = sky_engine.sun_ecliptic(ms)
    lon_s = sky_engine.wrap360(ml - sky_engine.ayanamsa(sky_engine.julian_day(ms))) \
        + sky_engine.wrap360(sl - sky_engine.ayanamsa(sky_engine.julian_day(ms)))
    idx = int(lon_s // (360.0 / 27.0)) % 27
    return {"index": idx + 1, "name": YOGA_NAMES[idx]}


def karana_of(elong: float) -> dict[str, Any]:
    n = int(elong // 6.0) + 1  # 1..60
    if n == 1:
        name = "Kimstughna"
    elif n >= 58:
        name = ("Shakuni", "Chatushpada", "Naga")[min(n - 58, 2)]
    else:
        name = MOVABLE_KARANAS[(n - 2) % 7]
    return {"index": n, "name": name}


def weekday_index(jd: float) -> int:
    return int(jd + 1.5) % 7


# ------------------------------------------------------------------ rise/set

def _sun_alt_fn(lat: float, lon: float, horizon: float):
    def fn(ms: int) -> float:
        ra, dec = sky_engine.ecliptic_to_equatorial(sky_engine.sun_ecliptic(ms), 0.0)
        alt, _ = sky_engine.altaz(ra, dec, sky_engine.julian_day(ms), lat, lon)
        return sky_engine.refraction_corrected(alt) - horizon
    return fn


def _moon_alt_fn(lat: float, lon: float):
    def fn(ms: int) -> float:
        m_lon, m_lat, dist_er = sky_engine.moon_ecliptic(ms)
        ra, dec = sky_engine.ecliptic_to_equatorial(m_lon, m_lat)
        alt, _ = sky_engine.altaz(ra, dec, sky_engine.julian_day(ms), lat, lon)
        return sky_engine.refraction_corrected(sky_engine.topocentric_alt(alt, dist_er))
    return fn


def _bracket(fn, ms_start: int, ms_end: int, rising: bool, step_ms: int = 1_800_000):
    t, prev = ms_start, fn(ms_start)
    while t + step_ms <= ms_end:
        nxt = t + step_ms
        val = fn(nxt)
        if (rising and prev <= 0.0 < val) or (not rising and prev > 0.0 >= val):
            return t, nxt
        t, prev = nxt, val
    return None


def _crossing(fn, lo: int, hi: int, target: float = 0.0) -> int | None:
    f_lo, f_hi = fn(lo) - target, fn(hi) - target
    if f_lo * f_hi > 0:
        return None
    for _ in range(40):
        mid = (lo + hi) // 2
        f_mid = fn(mid) - target
        if f_lo * f_mid <= 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
        if hi - lo < 2000:
            break
    return (lo + hi) // 2


def _latest_bracket(fn, ms: int, rising: bool, lookback_ms: int = 30 * 3_600_000):
    """Last crossing bracket at or before `ms` (scan forward, keep the last)."""
    found = None
    t = ms - lookback_ms
    prev = fn(t)
    step = 1_800_000
    while t + step <= ms + 3_600_000:
        nxt = t + step
        val = fn(nxt)
        if (rising and prev <= 0.0 < val) or (not rising and prev > 0.0 >= val):
            found = (t, nxt)
        t, prev = nxt, val
    return found


def rise_set(ms_utc: int, lat: float, lon: float, elev_m: float = 0.0) -> dict[str, Any]:
    """The solar day containing (or most recently containing) `ms_utc`:
    most recent sunrise, then the first sunset after it. Moon events are the
    nearest of each kind around the instant."""
    horizon = -0.833 - (1.76 * math.sqrt(max(elev_m, 0.0))) / 60.0
    sun = _sun_alt_fn(lat, lon, horizon)
    out: dict[str, Any] = {"sunrise": None, "sunset": None, "moonrise": None, "moonset": None}

    br = _latest_bracket(sun, ms_utc, rising=True)
    sunrise = _crossing(sun, *br) if br else None
    if sunrise is not None:
        out["sunrise"] = sunrise
        set_br = _bracket(sun, sunrise, sunrise + DAY, rising=False)
        out["sunset"] = _crossing(sun, *set_br) if set_br else None

    moon = _moon_alt_fn(lat, lon)
    for label, rising in (("moonrise", True), ("moonset", False)):
        br = _latest_bracket(moon, ms_utc, rising=rising)
        out[label] = _crossing(moon, *br) if br else None
    return out


# --------------------------------------------------------------- hora & muhurta

def horas(ms_utc: int, lat: float, lon: float) -> dict[str, Any]:
    """Planetary hours [convention]: Chaldean sequence from the day lord,
    12 daylight + 12 night divisions."""
    rises = rise_set(ms_utc, lat, lon)
    sunrise, sunset = rises["sunrise"], rises["sunset"]
    if sunrise is None or sunset is None:
        return {"convention": "hora", "error": "sun did not rise and set in this window"}
    weekday = weekday_index(sky_engine.julian_day(sunrise))
    day_lord = VARA_LORDS[weekday]
    start = CHALDEAN.index(day_lord)

    def hora_at(t: int) -> tuple[str, int, int]:
        if sunrise <= t < sunset:
            span = (sunset - sunrise) // 12
            n = min((t - sunrise) // span, 11)
            seg_start = sunrise + n * span
        elif t >= sunset:
            # Evening night: from tonight's sunset to tomorrow's sunrise.
            night_start, night_end = sunset, sunrise + DAY
            span = (night_end - night_start) // 12
            n = 12 + min((t - night_start) // span, 11)
            seg_start = night_start + (n - 12) * span
        else:
            # Pre-dawn: the ongoing night began at yesterday's sunset.
            night_start, night_end = sunset - DAY, sunrise
            span = (night_end - night_start) // 12
            n = 12 + min((t - night_start) // span, 11)
            seg_start = night_start + (n - 12) * span
        planet = CHALDEAN[(start + n) % 7]
        return planet, int(seg_start), int(seg_start + span)

    now_planet, seg_start, seg_end = hora_at(ms_utc)
    return {
        "convention": "hora (planetary hours) — traditional timing convention",
        "tier": "convention",
        "day_lord": day_lord,
        "current": {"lord": now_planet, "starts": seg_start, "ends": seg_end},
        "sequence_today": [CHALDEAN[(start + n) % 7] for n in range(24)],
    }


def muhurtas(ms_utc: int, lat: float, lon: float) -> dict[str, Any]:
    rises = rise_set(ms_utc, lat, lon)
    sunrise, sunset = rises["sunrise"], rises["sunset"]
    if sunrise is None or sunset is None:
        return {"error": "no sunrise/sunset"}
    day_span = sunset - sunrise
    abhijit_start = sunrise + int(day_span * 7 / 15)
    abhijit_end = sunrise + int(day_span * 8 / 15)
    brahma_start = sunrise - 96 * 60_000
    brahma_end = sunrise - 48 * 60_000
    return {
        "convention": "muhurta windows — traditional timing convention",
        "tier": "convention",
        "brahma": {"starts": brahma_start, "ends": brahma_end},
        "abhijit": {"starts": abhijit_start, "ends": abhijit_end},
    }


def rahu_kaal(ms_utc: int, lat: float, lon: float) -> dict[str, Any]:
    rises = rise_set(ms_utc, lat, lon)
    sunrise, sunset = rises["sunrise"], rises["sunset"]
    if sunrise is None or sunset is None:
        return {"error": "no sunrise/sunset"}
    weekday = weekday_index(sky_engine.julian_day(sunrise))
    part = RAHU_KAAL_PART[weekday]
    span = (sunset - sunrise) // 8
    return {
        "convention": "Rahu Kaal — traditional timing convention",
        "tier": "convention",
        "part": part,
        "starts": int(sunrise + (part - 1) * span),
        "ends": int(sunrise + part * span),
    }


# ------------------------------------------------------------------- assembly

def now_strip(ms_utc: int, lat: float, lon: float, elev_m: float = 0.0) -> dict[str, Any]:
    """The live 'this moment' payload: what a returning visitor consumes first."""
    elong = _elongation(ms_utc)
    nak = nakshatra_of_full(ms_utc)
    row = sky_engine.compute_sky(ms_utc)
    return {
        "timestamp_ms_utc": ms_utc,
        "jd": round(row.jd, 5),
        "tithi": tithi_of(elong),
        "nakshatra": nak,
        "yoga": yoga_of(ms_utc),
        "karana": karana_of(elong),
        "vara": {"index": weekday_index(row.jd), "name": VARA_NAMES[weekday_index(row.jd)],
                 "lord": VARA_LORDS[weekday_index(row.jd)]},
        "sun_sign": row.bodies["Sun"]["sign"],
        "moon_sign": row.bodies["Moon"]["sign"],
        "rise_set": rise_set(ms_utc, lat, lon, elev_m),
        "hora": horas(ms_utc, lat, lon),
        "muhurtas": muhurtas(ms_utc, lat, lon),
        "rahu_kaal": rahu_kaal(ms_utc, lat, lon),
        "calendars": None,  # filled by the route (calendars.all_calendars)
        "provenance": {"engine": ENGINE_VERSION, "runtime_ai": False,
                       "conventions_note": "hora/muhurta/Rahu-Kaal are traditional "
                                           "conventions (general framing), not Brihat "
                                           "Jataka doctrine; all positions are measured."},
    }


def day_transitions(ms_utc: int) -> list[dict[str, Any]]:
    """Every panchanga hand that moves during the UTC day [measured]."""
    events: list[dict[str, Any]] = []
    step = 600_000  # 10 min
    start = ms_utc - ms_utc % 86_400_000
    prev_e, prev_n = _elongation(start), nakshatra_of_full(start)["index"]
    t = start + step
    while t < start + 86_400_000:
        e, n = _elongation(t), nakshatra_of_full(t)["index"]
        if e // 12 != prev_e // 12:
            events.append({"kind": "tithi", "at": t, "value": tithi_of(e)["label"]})
        if n != prev_n:
            events.append({"kind": "nakshatra", "at": t, "value": nakshatra_of_full(t)["name"]})
        prev_e, prev_n = e, n
        t += step
    return events
