"""
Amendment III — The restored crescent: topocentric new-month visibility.

Computes, for an observer (lat, lon, elevation) and an evening:

  [measured]    sunset (refraction + horizon dip from elevation), Moon/Sun
                topocentric altitudes and azimuths (lunar parallax applied),
                geocentric elongation (ARCL), altitude difference (ARCV),
                relative azimuth (ΔA), Moon age, illumination fraction,
                moonset and the moonset−sunset lag.
  [hypothesis]  the visibility CLASS, from Yallop's (1997) q-criterion as
                commonly implemented. The raw numbers above are the deliverable;
                the class is a statistical fit whose implementation is pending
                scholarly verification — see the Tribunal ledger entry.

This module never declares a religious ruling; it reports observables and one
labelled criterion so fasting communities can decide with the numbers.
"""
from __future__ import annotations

import math
from typing import Any

from app.services import sky_engine

ENGINE_VERSION = "crescent-1.0.0"
SUNSET_ALT_DEG = -0.833  # upper limb with standard refraction
EARTH_RADIUS_KM = 6371.0088
AU_KM = 149597870.7


def _horizon_deg(elev_m: float) -> float:
    """Effective sunset altitude: refraction + horizon dip (1.76·√h arcmin)."""
    return SUNSET_ALT_DEG - (1.76 * math.sqrt(max(elev_m, 0.0))) / 60.0


def _sun_alt_fn(lat: float, lon: float, horizon: float):
    def fn(ms: int) -> float:
        jd = sky_engine.julian_day(ms)
        ra, dec = sky_engine.ecliptic_to_equatorial(sky_engine.sun_ecliptic(ms), 0.0)
        alt, _ = sky_engine.altaz(ra, dec, jd, lat, lon)
        return sky_engine.refraction_corrected(alt) - horizon
    return fn


def _moon_alt_fn(lat: float, lon: float, horizon: float):
    def fn(ms: int) -> float:
        jd = sky_engine.julian_day(ms)
        lon_t, lat_t, dist_er = sky_engine.moon_ecliptic(ms)
        ra, dec = sky_engine.ecliptic_to_equatorial(lon_t, lat_t)
        alt, _ = sky_engine.altaz(ra, dec, jd, lat, lon)
        alt = sky_engine.topocentric_alt(alt, dist_er)
        return sky_engine.refraction_corrected(alt) - horizon
    return fn


def _moon_state(ms: int, lat: float, lon: float, horizon: float) -> dict[str, float]:
    jd = sky_engine.julian_day(ms)
    m_lon, m_lat, dist_er = sky_engine.moon_ecliptic(ms)
    s_lon = sky_engine.sun_ecliptic(ms)
    m_ra, m_dec = sky_engine.ecliptic_to_equatorial(m_lon, m_lat)
    s_ra, s_dec = sky_engine.ecliptic_to_equatorial(s_lon, 0.0)
    m_alt, m_az = sky_engine.altaz(m_ra, m_dec, jd, lat, lon)
    s_alt, s_az = sky_engine.altaz(s_ra, s_dec, jd, lat, lon)
    m_alt = sky_engine.refraction_corrected(sky_engine.topocentric_alt(m_alt, dist_er))
    s_alt = sky_engine.refraction_corrected(s_alt)
    daz = abs((m_az - s_az + 180.0) % 360.0 - 180.0)
    arcl = math.degrees(math.acos(max(-1.0, min(1.0, math.cos(math.radians(m_lat)) *
                                                   math.cos(math.radians(m_lon - s_lon))))))
    return {
        "moon_alt": m_alt, "sun_alt": s_alt, "moon_az": m_az, "sun_az": s_az,
        "d_az": daz, "arcl": arcl, "arcv": abs(m_alt - s_alt),
        "illumination": (1.0 - math.cos(math.radians(arcl))) / 2.0,
        "dist_er": dist_er,
    }


def _find_conjunction_age(ms: int) -> float:
    """Hours since the most recent Sun–Moon conjunction (elongation crossed 0)."""
    step = 3600_000.0  # 1 h

    def elong(m: int) -> float:
        ml, _, _ = sky_engine.moon_ecliptic(m)
        sl = sky_engine.sun_ecliptic(m)
        return (ml - sl) % 360.0

    elong_ms = elong(ms)
    t = ms
    prev = elong_ms
    for _ in range(480):  # up to 20 days back — a full lunation is 29.5 days
        t -= step
        cur = elong(t)
        if cur > prev:  # wrapped through 360→0: conjunction between t and t+step
            frac = (360.0 - cur) / (prev - cur + 360.0)
            conjunction = t + frac * step
            return (ms - conjunction) / 3600000.0
        prev = cur
    if elong_ms > 180.0:
        # Pre-conjunction: the waning Moon is still behind the Sun. Find the
        # UPCOMING conjunction and report a negative age.
        t = ms
        prev = elong_ms
        for _ in range(72):
            t_prev = t
            t += step
            cur = elong(t)
            if cur < prev:  # wrapped forward through 360→0
                frac = (360.0 - prev) / (cur - prev + 360.0)
                conjunction = t_prev + frac * step
                return (ms - conjunction) / 3600000.0
            prev = cur
    return float("nan")


def _bracket_descending(fn, ms_start: int, ms_end: int, step_ms: int = 1_800_000):
    """Scan for a descending zero crossing of fn, then return the bracket."""
    t = ms_start
    prev = fn(t)
    while t + step_ms <= ms_end:
        nxt = t + step_ms
        val = fn(nxt)
        if prev > 0.0 >= val:
            return t, nxt
        t, prev = nxt, val
    return None


def visibility(ms_utc: int, lat: float, lon: float, elev_m: float = 0.0) -> dict[str, Any]:
    horizon = _horizon_deg(elev_m)
    sun_fn = _sun_alt_fn(lat, lon, horizon)
    bracket = _bracket_descending(sun_fn, ms_utc, ms_utc + 86_400_000)
    sunset = sky_engine.find_event(*bracket, sun_fn, 0.0, rising=False) if bracket else None
    if sunset is None:
        return {"error": "no sunset found in the 24 h after the given instant",
                "provenance": {"engine": ENGINE_VERSION}}

    state = _moon_state(sunset, lat, lon, horizon)
    moon_bracket = _bracket_descending(_moon_alt_fn(lat, lon, horizon), sunset, sunset + 43_200_000)
    moonset = (sky_engine.find_event(*moon_bracket, _moon_alt_fn(lat, lon, horizon), 0.0, rising=False)
               if moon_bracket else None)

    # Yallop (1997) q-criterion, as commonly implemented — tiered hypothesis.
    delta_a_crit = -0.13666 * state["arcv"] + 14.1667
    q = (state["arcl"] - delta_a_crit) / 10.0
    if q >= 0.25:
        band, band_note = "A", "crescent visible to the naked eye"
    elif q >= -0.25:
        band, band_note = "B", "visible to the naked eye under perfect conditions"
    elif q >= -4.0:
        band, band_note = "C", "visible to the naked eye may be difficult; optical aid likely needed"
    elif q >= -6.0:
        band, band_note = "D", "optical aid necessary"
    else:
        band, band_note = "F", "not visible even with optical aid"

    age_h = _find_conjunction_age(sunset)
    return {
        "observer": {"lat": lat, "lon": lon, "elev_m": elev_m,
                     "horizon_alt_deg": round(horizon, 4)},
        "sunset_ms_utc": sunset,
        "at_sunset": {
            "moon_alt_deg": round(state["moon_alt"], 3),
            "sun_alt_deg": round(state["sun_alt"], 3),
            "moon_azimuth_deg": round(state["moon_az"], 2),
            "sun_azimuth_deg": round(state["sun_az"], 2),
            "relative_azimuth_deg": round(state["d_az"], 3),
            "elongation_arcl_deg": round(state["arcl"], 3),
            "altitude_diff_arcv_deg": round(state["arcv"], 3),
            "illumination_fraction": round(state["illumination"], 5),
            "moon_age_hours": round(age_h, 2),
        },
        "moonset": {
            "ms_utc": moonset,
            "lag_minutes": None if moonset is None else round((moonset - sunset) / 60000.0, 1),
        },
        "yallop_q": {
            "tier": "hypothesis",
            "q": round(q, 3),
            "band": band,
            "band_note": band_note,
            "criterion": "q = (ARCL − (−0.13666·ARCV + 14.1667)) / 10 — Yallop (1997) "
                         "as commonly implemented; implementation pending scholarly "
                         "verification (see Tribunal).",
        },
        "disclaimer": "Observables are computed; the class is one labelled criterion. "
                      "This is not a religious ruling.",
        "provenance": {"engine": ENGINE_VERSION, "runtime_ai": False,
                       "parallax": "lunar topocentric parallax applied; "
                                   "Bennett refraction; horizon dip 1.76·√h"},
    }
