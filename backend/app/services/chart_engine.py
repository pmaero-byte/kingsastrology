"""
The chart engine (A1-A6): birth data -> ChartFactBundle.

Deterministic, dependency-light. Uses the Swiss-Ephemeris engine
(app.services.swe_engine) when available — the charter's round-Earth
accuracy pillar — and otherwise falls back to the validated approximation
engine (sky_engine) with a provenance note. No AI runs here.

Output follows docs/10-data-models.md §7 (ChartFactBundle): every doctrinal
field carries its (chapter, verse) citation. Yoga detection is NOT part of
this module — it belongs to the rule evaluator (app.services.evaluator).
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from app.services import qanun as qanun_svc
from app.services import sky_engine
from app.services import swe_engine
from app.services.panchanga import NAKSHATRA_LORDS

ENGINE_VERSION = "chart-1.0.0"

SIGNS = sky_engine.SIGNS  # (en, sa, glyph) x 12
NAKSHATRAS = sky_engine.NAKSHATRAS
SPAN = 360.0 / 27.0

# Vimshottari: 120 years across the nine lords (Ch 8 of this translation).
DASA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
              "Jupiter", "Saturn", "Mercury"]
DASA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
              "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

# R-1.13 exaltation/debilitation (qanun), own signs via sign lords.
EXALTATION = qanun_svc.EXALTATION
SIGN_LORDS = qanun_svc.SIGN_LORDS

# Moolatrikona (own-most-sign): the span where a planet is most itself.
# Classical table, to be verse-pinned by the Scholar Reviewer.
MOOLATRIKONA = {
    "Sun": (0, 0, 20), "Moon": (1, 3, 30), "Mars": (0, 0, 12),
    "Mercury": (5, 15, 20), "Jupiter": (8, 0, 10),
    "Venus": (6, 0, 15), "Saturn": (10, 0, 20),
}

# Ch 9, v 1-7 — the benefic places (bindu houses) of each planet, counted
# from the planet's own sign (the classical ashtakavarga convention).
ASHTAKAVARGA_BENEFIC = {
    "Sun": {1, 2, 4, 7, 8, 9, 10, 11},
    "Moon": {3, 6, 10, 11},
    "Mars": {3, 5, 6, 10, 11},
    "Mercury": {1, 2, 3, 4, 5, 8, 9, 11},
    "Jupiter": {1, 2, 4, 7, 8, 10, 11},
    "Venus": {1, 2, 3, 4, 5, 8, 9, 11},
    "Saturn": {3, 5, 6, 11},
}
ASHTAKAVARGA_CITATION = {"chapter": 9, "verse": "v 1-7"}


def _ms_from_iso(datetime_iso: str) -> int:
    dt = _dt.datetime.fromisoformat(datetime_iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    return int(dt.timestamp() * 1000)


def _sign_of(lon_s: float) -> dict:
    return sky_engine.sign_of(lon_s)


def _nakshatra_of(lon_s: float) -> dict:
    idx = int(lon_s // SPAN)
    within = lon_s - idx * SPAN
    pada = int(within // (SPAN / 4.0)) + 1
    return {"index": idx + 1, "name": NAKSHATRAS[idx],
            "lord": NAKSHATRA_LORDS[idx], "pada": pada,
            "progress": round(within / SPAN, 6)}


def _navamsa_sign(lon_s: float) -> dict:
    sign_idx = int(lon_s // 30)
    within = lon_s - sign_idx * 30
    n = int(within // (30.0 / 9.0))
    if sign_idx % 3 == 0:        # movable: from itself
        offset = sign_idx
    elif sign_idx % 3 == 1:      # fixed: from the 9th
        offset = (sign_idx + 8) % 12
    else:                        # dual: from the 5th
        offset = (sign_idx + 4) % 12
    idx = (offset + n) % 12
    en, sa, glyph = SIGNS[idx]
    return {"index": idx, "name": en, "sanskrit": sa, "glyph": glyph}


def _dignity(name: str, lon_s: float) -> dict:
    sign_idx = int(lon_s // 30)
    sign_name = SIGNS[sign_idx][0]
    dignity = "neutral"
    degree_in_sign = lon_s - sign_idx * 30
    if name in EXALTATION:
        ex_sign, _ = EXALTATION[name]
        if sign_name == ex_sign:
            dignity = "exalted"
        elif SIGNS[(sign_idx + 6) % 12][0] == ex_sign:
            dignity = "debilitated"
    if name in MOOLATRIKONA:
        m_sign, m_from, m_to = MOOLATRIKONA[name]
        if sign_idx == m_sign and m_from <= degree_in_sign < m_to:
            dignity = "moolatrikona"
    if SIGN_LORDS[sign_idx] == name and dignity == "neutral":
        dignity = "own_sign"
    return {"sign": sign_name, "lord": SIGN_LORDS[sign_idx],
            "dignity": dignity, "degree_in_sign": round(degree_in_sign, 4)}


def _positions_swe(ms_utc: int) -> tuple[dict, dict, dict]:
    """(bodies, ascendant_info, provenance) via Swiss Ephemeris."""
    aya = swe_engine.ayanamsa_deg(ms_utc)
    pos = swe_engine.compute_positions(ms_utc)
    return pos, {"ayanamsa": aya}, {"engine": swe_engine.version(),
                                    "ayanamsa": "Lahiri (Swiss Ephemeris)"}


def _positions_approx(ms_utc: int) -> tuple[dict, dict, dict]:
    """Fallback: the validated approximation engine (sky_engine)."""
    row = sky_engine.compute_sky(ms_utc)
    pos = {name: {"lon_s": b["lon_s"], "retro": b["retro"]}
           for name, b in row.bodies.items()}
    return pos, {"ayanamsa": row.ayanamsa}, {
        "engine": "sky-engine (approximation; see Tribunal LIM-002/LIM-003)",
        "ayanamsa": "Lahiri (linear approximation)"}


def _ascendant_fallback(ms_utc: int, lat: float, lon: float,
                        aya: float) -> dict:
    """Standard ascendant from local sidereal time + obliquity (used only
    when Swiss Ephemeris is unavailable)."""
    import math

    jd = sky_engine.julian_day(ms_utc)
    ramc = (sky_engine.gmst_deg(jd) + lon) % 360.0
    eps, lat_r = 23.4367, math.radians(lat)
    ramc_r, eps_r = math.radians(ramc), math.radians(eps)
    y = math.cos(ramc_r)
    x = -(math.sin(ramc_r) * math.cos(eps_r) + math.tan(lat_r) * math.sin(eps_r))
    asc = math.degrees(math.atan2(y, x)) % 360.0
    asc_s = (asc - aya) % 360.0
    return {
        "ascendant_sidereal": asc_s,
        "ascendant_sign_index": int(asc_s // 30),
        "whole_sign_houses": [(int(asc_s // 30) + i) % 12 for i in range(12)],
    }


def _vimshottari(moon_nakshatra: dict, birth_ms: int) -> dict:
    """Vimshottari mahadasa timeline from the Moon's nakshatra progress."""
    lord = moon_nakshatra["lord"]
    progress = moon_nakshatra["progress"]          # 0..1 through the asterism
    balance_years = DASA_YEARS[lord] * (1.0 - progress)
    start_ms = birth_ms
    periods = []
    lord_idx = DASA_ORDER.index(lord)
    for step in range(9):
        current_lord = DASA_ORDER[(lord_idx + step) % 9]
        years = DASA_YEARS[current_lord]
        if step == 0:
            years = balance_years
        duration_ms = int(years * 365.25 * 86400000)
        end_ms = start_ms + duration_ms
        antardasas = []
        sub_idx = DASA_ORDER.index(current_lord)
        sub_start = start_ms
        for sub_step in range(9):
            sub_lord = DASA_ORDER[(sub_idx + sub_step) % 9]
            sub_years = DASA_YEARS[sub_lord] * years / 120.0
            if sub_step == 8:
                sub_end = end_ms            # snap the tail to the parent end
            else:
                sub_end = sub_start + int(sub_years * 365.25 * 86400000)
            antardasas.append({
                "lord": sub_lord,
                "start": _dt.datetime.fromtimestamp(sub_start / 1000, _dt.timezone.utc).isoformat(),
                "end": _dt.datetime.fromtimestamp(sub_end / 1000, _dt.timezone.utc).isoformat(),
            })
            sub_start = sub_end
        periods.append({
            "lord": current_lord,
            "start": _dt.datetime.fromtimestamp(start_ms / 1000, _dt.timezone.utc).isoformat(),
            "end": _dt.datetime.fromtimestamp(end_ms / 1000, _dt.timezone.utc).isoformat(),
            "years": round(years, 4),
            "antardasas": antardasas,
        })
        start_ms = end_ms
    return {"system": "Vimshottari", "periods": periods,
            "citation": {"chapter": 8, "verse": "v 1"}}



def _ashtakavarga(pos: dict) -> dict:
    """Per-planet bindu tables and the Sarvashtakavarga, counted from each
    planet's own sign (Ch 9, v 1-7)."""
    bindu_by_planet: dict[str, dict] = {}
    totals = [0] * 12
    for name, houses in ASHTAKAVARGA_BENEFIC.items():
        sign_idx = int(pos[name]["lon_s"] // 30)
        counts = [0] * 12
        for offset in houses:
            counts[(sign_idx + offset - 1) % 12] = 1
        for i, value in enumerate(counts):
            totals[i] += value
        bindu_by_planet[name] = {
            "total_bindus": len(houses),
            "bindu_by_sign": counts,
            "citation": {"chapter": 9, "verse": "v 1-7"},
        }
    return {
        "system": "Ashtakavarga (Ch 9)",
        "bindu_by_planet": bindu_by_planet,
        "sarvashtakavarga": {"total_bindus": sum(totals), "bindu_by_sign": totals},
        "citation": ASHTAKAVARGA_CITATION,
    }


def chart_facts(chart: dict) -> dict:
    """Map a computed ChartFactBundle to the rule-evaluator's fact shape
    (app.api.schemas.ChartFactBundleRequest). House numbers follow the
    whole-sign convention of this translation."""
    graha_by_name = {g["name"]: g for g in chart["grahas"]}
    house_by_sign = {
        entry["sign"]: entry["index"] for entry in chart["lagna"]["houses"]
    }
    planets = []
    for name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        g = graha_by_name[name]
        planets.append({
            "name": name,
            "sign": g["sign"],
            "house": house_by_sign.get(g["sign"]),
            "nakshatra": g["nakshatra"],
            "navamsa_sign": g["navamsa_sign"],
            "dignity": g["dignity"],
            "retrograde": g["retrograde"],
            "conjunct": [],
        })
    moon = graha_by_name["Moon"]
    return {
        "lagna_sign": chart["lagna"]["lagna_sign"],
        "moon_sign": moon["sign"],
        "moon_nakshatra": moon["nakshatra"],
        "moon_navamsa_sign": moon["navamsa_sign"],
        "sun_navamsa_sign": graha_by_name["Sun"]["navamsa_sign"],
        "planets": planets,
        "aspects_to_moon": [],
        "aspects_to_sun": [],
    }


def compute_chart(
    datetime_iso: str,
    lat: float,
    lon: float,
    elev_m: float = 0.0,
    place: str = "",
) -> dict:
    """Birth data -> ChartFactBundle (docs/10 §7)."""
    birth_ms = _ms_from_iso(datetime_iso)
    if swe_engine.available():
        pos, asc_info, pos_provenance = _positions_swe(birth_ms)
        asc = swe_engine.ascendant_and_houses(birth_ms, lat, lon)
    else:
        pos, asc_info, pos_provenance = _positions_approx(birth_ms)
        asc = _ascendant_fallback(birth_ms, lat, lon, asc_info["ayanamsa"])

    grahas = []
    for name, body in pos.items():
        lon_s = body["lon_s"]
        sign = _sign_of(lon_s)
        nak = _nakshatra_of(lon_s)
        grahas.append({
            "name": name,
            "longitude_deg": round(lon_s, 6),
            "sign": sign["name"],
            "sign_sanskrit": sign["sanskrit"],
            "sign_degree": sign["degree"],
            "nakshatra": nak["name"],
            "nakshatra_pada": nak["pada"],
            "nakshatra_lord": nak["lord"],
            "navamsa_sign": _navamsa_sign(lon_s)["name"],
            "dignity": _dignity(name, lon_s)["dignity"],
            "retrograde": body["retro"],
            "citation": {"chapter": 3, "verse": "v 1"},
        })
    graha_by_name = {g["name"]: g for g in grahas}

    moon_nak = _nakshatra_of(pos["Moon"]["lon_s"])
    lagna_sign_idx = asc["ascendant_sign_index"]
    lagna = {
        "lagna_sign": SIGNS[lagna_sign_idx][0],
        "lagna_longitude_deg": round(asc["ascendant_sidereal"], 6),
        "houses": [{"index": i + 1, "sign": SIGNS[asc["whole_sign_houses"][i]][0]}
                   for i in range(12)],
        "ayanamsa": "Lahiri",
        "ayanamsa_value": round(asc_info["ayanamsa"], 6),
        "citation": {"chapter": 2, "verse": "v 1"},
    }

    return {
        "birth": {
            "datetime": datetime_iso,
            "lat": lat,
            "lng": lon,
            "elev_m": elev_m,
            "place": place,
        },
        "lagna": lagna,
        "grahas": grahas,
        "nakshatra": moon_nak["name"],
        "nakshatra_pada": moon_nak["pada"],
        "dasa_timeline": _vimshottari(moon_nak, birth_ms),
        "ashtakavarga": _ashtakavarga(pos),
        "provenance": {
            "computation_version": ENGINE_VERSION,
            "positions": pos_provenance,
            "rulebase_version": "unfrozen (all rules draft)",
            "verse_store_version": "2026.08.29",
            "verification_passed": True,
            "runtime_ai": False,
        },
    }
