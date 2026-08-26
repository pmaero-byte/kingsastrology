"""
The period reports: this day, this week, this month, this year.

Every event is found by scanning the zīj itself — sign ingresses, lunations,
saṅkrāntis, retrograde turns — so the reports can never drift from the sky
record. Eclipse hints are [measured geometry]: Moon's ecliptic latitude at a
lunation tells us whether an eclipse is likely; it is an indicator, not a
map, and is labelled as such.
"""
from __future__ import annotations

from typing import Any

from app.services import panchanga
from app.services import sky_engine

ENGINE_VERSION = "periods-1.0.0"
DAY = 86_400_000

SIGN_NAMES = [s[0] for s in sky_engine.SIGNS]


def _sidereal(moon_t: float, sun_t: float, jd: float) -> tuple[float, float]:
    aya = sky_engine.ayanamsa(jd)
    return sky_engine.wrap360(moon_t - aya), sky_engine.wrap360(sun_t - aya)


def _refine_crossing(start_ms: int, end_ms: int, value_fn, boundary: float) -> int:
    """Bisect to the moment value_fn crosses `boundary` (mod-360-aware)."""
    lo, hi = start_ms, end_ms
    for _ in range(30):
        mid = (lo + hi) // 2
        v = value_fn(mid)
        # walk the shorter arc from lo to mid to decide which side we are on
        v_lo = value_fn(lo)
        delta = (v - v_lo + 540.0) % 360.0 - 180.0
        target = (value_fn(lo) - boundary + 540.0) % 360.0 - 180.0
        if delta * target < 0 or abs(delta) > 180:
            hi = mid
        else:
            lo = mid
        if hi - lo < 60_000:
            break
    return (lo + hi) // 2


def scan_events(ms_start: int, ms_end: int, step_ms: int = 1_800_000,
                retro_planets: tuple[str, ...] = ("Mercury", "Venus", "Mars")) -> list[dict[str, Any]]:
    """Scan the sky record for events in [ms_start, ms_end)."""
    events: list[dict[str, Any]] = []

    t = ms_start
    prev = sky_engine.fast_longitudes(t)
    prev_jd = sky_engine.julian_day(t)
    prev_moon_s, prev_sun_s = _sidereal(prev["Moon"], prev["Sun"], prev_jd)
    prev_signs = {k: int(sky_engine.wrap360(v - sky_engine.ayanamsa(prev_jd)) // 30)
                  for k, v in prev.items()}
    prev_elong = (prev["Moon"] - prev["Sun"]) % 360.0
    prev_retro = _retro_flags(t, retro_planets)

    while t + step_ms <= ms_end:
        t += step_ms
        cur = sky_engine.fast_longitudes(t)
        jd = sky_engine.julian_day(t)
        moon_s, sun_s = _sidereal(cur["Moon"], cur["Sun"], jd)
        cur_signs = {k: int(sky_engine.wrap360(v - sky_engine.ayanamsa(jd)) // 30)
                     for k, v in cur.items()}
        elong = (cur["Moon"] - cur["Sun"]) % 360.0

        for name in cur_signs:
            if cur_signs[name] != prev_signs[name] and name in ("Moon", "Sun", "Jupiter", "Saturn"):
                at = _refine_crossing(
                    t - step_ms, t,
                    lambda m, n=name: sky_engine.wrap360(
                        sky_engine.fast_longitudes(m)[n] - sky_engine.ayanamsa(sky_engine.julian_day(m))),
                    (cur_signs[name] % 12) * 30.0,
                )
                events.append({
                    "kind": f"{name.lower()}_ingress" if name != "Sun" else "sankranti",
                    "at": at,
                    "body": name,
                    "value": SIGN_NAMES[cur_signs[name]],
                })

        if prev_elong > elong:  # wrapped 360→0: new moon
            events.append(_lunation_event(t, "new_moon", step_ms))
        elif prev_elong < 180.0 <= elong:  # crossed opposition: full moon
            events.append(_lunation_event(t, "full_moon", step_ms))

        cur_retro = _retro_flags(t, retro_planets)
        for name in retro_planets:
            if cur_retro[name] != prev_retro[name]:
                events.append({
                    "kind": "retrograde" if cur_retro[name] else "direct",
                    "at": t,
                    "body": name,
                    "value": "R" if cur_retro[name] else "",
                })

        prev, prev_jd = cur, jd
        prev_moon_s, prev_sun_s = moon_s, sun_s
        prev_signs, prev_elong, prev_retro = cur_signs, elong, cur_retro

    return sorted(events, key=lambda e: e["at"])


def _retro_flags(ms: int, planets: tuple[str, ...]) -> dict[str, bool]:
    fwd = sky_engine.fast_longitudes(ms + 43_200_000)
    bwd = sky_engine.fast_longitudes(ms - 43_200_000)
    flags = {}
    for name in planets:
        delta = (fwd[name] - bwd[name] + 540.0) % 360.0 - 180.0
        flags[name] = delta < 0
    return flags


def _lunation_event(near_ms: int, kind: str, step_ms: int) -> dict[str, Any]:
    at = _refine_crossing(
        near_ms - step_ms, near_ms,
        lambda m: (sky_engine.fast_longitudes(m)["Moon"] - sky_engine.fast_longitudes(m)["Sun"]) % 360.0,
        0.0 if kind == "new_moon" else 180.0,
    )
    m_lon, m_lat, _ = sky_engine.moon_ecliptic(at)
    # Kind-aware geometric bands (degrees of lunar latitude):
    #   lunar eclipse (full moon): umbral/penumbral contact ~1.0 / ~1.55
    #   solar eclipse (new moon):  partial possible ~1.0 / ~1.6
    likely, possible = (1.0, 1.6) if kind == "new_moon" else (1.0, 1.55)
    if abs(m_lat) < likely:
        hint = "likely"
    elif abs(m_lat) < possible:
        hint = "possible"
    else:
        hint = "unlikely"
    return {
        "kind": kind,
        "at": at,
        "body": "Moon",
        "value": kind.replace("_", " ").title(),
        "eclipse_hint": {"tier": "measured", "moon_latitude_deg": round(m_lat, 3),
                         "indicator": hint,
                         "note": "geometric indicator from the Moon's latitude at the "
                                 "lunation — not an eclipse map"},
    }


# ------------------------------------------------------------------ reports

def report_day(ms_utc: int, lat: float, lon: float, elev_m: float = 0.0) -> dict[str, Any]:
    day_start = ms_utc - ms_utc % DAY
    return {
        "period": "day",
        "day_start_ms_utc": day_start,
        "now": panchanga.now_strip(ms_utc, lat, lon, elev_m),
        "transitions": panchanga.day_transitions(day_start),
        "provenance": {"engine": ENGINE_VERSION, "runtime_ai": False},
    }


def report_week(ms_utc: int, lat: float, lon: float, elev_m: float = 0.0) -> dict[str, Any]:
    day_start = ms_utc - ms_utc % DAY
    weekday = panchanga.weekday_index(sky_engine.julian_day(day_start))
    week_start = day_start - weekday * DAY
    days = []
    for i in range(7):
        d = week_start + i * DAY + 12 * 3_600_000  # judge each day at noon UT
        row = sky_engine.compute_sky(d)
        wd = panchanga.weekday_index(row.jd)
        days.append({
            "date_ms_utc": week_start + i * DAY,
            "vara": panchanga.VARA_NAMES[wd],
            "lord": panchanga.VARA_LORDS[wd],
            "moon_sign": row.bodies["Moon"]["sign"]["sanskrit"],
            "moon_nakshatra": row.bodies["Moon"]["nakshatra"],
            "tithi": panchanga.tithi_of((row.bodies["Moon"]["lon_t"] - row.bodies["Sun"]["lon_t"]) % 360.0)["label"],
        })
    return {
        "period": "week",
        "week_start_ms_utc": week_start,
        "days": days,
        "events": scan_events(week_start, week_start + 7 * DAY),
        "provenance": {"engine": ENGINE_VERSION, "runtime_ai": False},
    }


def report_month(ms_utc: int, lat: float, lon: float, elev_m: float = 0.0) -> dict[str, Any]:
    day_start = ms_utc - ms_utc % DAY
    month_start = day_start - 14 * DAY
    events = scan_events(month_start, month_start + 30 * DAY, step_ms=3_600_000,
                         retro_planets=("Mercury", "Venus", "Mars"))
    return {
        "period": "month",
        "window_ms_utc": [month_start, month_start + 30 * DAY],
        "events": events,
        "lunations": [e for e in events if e["kind"] in ("new_moon", "full_moon")],
        "sankrantis": [e for e in events if e["kind"] == "sankranti"],
        "provenance": {"engine": ENGINE_VERSION, "runtime_ai": False},
    }


def report_year(ms_utc: int, lat: float, lon: float, elev_m: float = 0.0) -> dict[str, Any]:
    day_start = ms_utc - ms_utc % DAY
    year_start = day_start - 180 * DAY
    year_end = day_start + 185 * DAY
    events = scan_events(year_start, year_end, step_ms=6 * 3_600_000,
                         retro_planets=("Mercury", "Jupiter", "Saturn"))
    row = sky_engine.compute_sky(ms_utc)
    return {
        "period": "year",
        "window_ms_utc": [year_start, year_end],
        "year_lords": {
            "note": "Jupiter changes sign roughly yearly, Saturn slowly — the "
                    "slow grahas colour the year [measured positions]",
            "jupiter_sign": row.bodies["Jupiter"]["sign"]["sanskrit"],
            "saturn_sign": row.bodies["Saturn"]["sign"]["sanskrit"],
            "rahu_sign": row.bodies["Rahu"]["sign"]["sanskrit"],
        },
        "sankrantis": [e for e in events if e["kind"] == "sankranti"],
        "ingresses": [e for e in events if e["kind"].endswith("_ingress")
                      and e["body"] in ("Jupiter", "Saturn")],
        "lunations": [e for e in events if e["kind"] in ("new_moon", "full_moon")],
        "retrograde_turns": [e for e in events if e["kind"] in ("retrograde", "direct")],
        "provenance": {"engine": ENGINE_VERSION, "runtime_ai": False},
    }
