"""
Layer 0 — Swiss-Ephemeris engine (A1): true geocentric computation.

Replaces the approximation caveats of sky_engine.py (Tribunal LIM-002/LIM-003)
for served chart facts. Swiss Ephemeris is the charter's round-Earth accuracy
pillar (docs/05 §2.1): geocentric positions, selectable ayanamsa (Lahiri
default), true ascendant and houses.

The pyswisseph package (imports as `swisseph`) is optional at runtime: it is
not in the base requirements (PEP-668 environments install it project-locally):

    python3 -m pip install --target ./vendor pyswisseph

If unavailable, this module reports `available=False` and the chart engine
falls back to the validated approximation engine with a provenance note.
"""
from __future__ import annotations

import sys
from pathlib import Path

ENGINE_VERSION = "swe-1.0.0"
_VENDOR_DIR = Path(__file__).resolve().parents[2] / "vendor"

try:
    import swisseph as _swe  # type: ignore
except ImportError:
    try:
        sys.path.insert(0, str(_VENDOR_DIR))
        import swisseph as _swe  # type: ignore
    except ImportError:
        _swe = None

SIDM_LAHIRI = getattr(_swe, "SIDM_LAHIRI", 1)
SUN = 0
MOON = 1
MERCURY = 2
VENUS = 3
MARS = 4
JUPITER = 5
SATURN = 6
RAHU = 11
KETU = 12
_BODIES = {"Sun": SUN, "Moon": MOON, "Mercury": MERCURY, "Venus": VENUS,
           "Mars": MARS, "Jupiter": JUPITER, "Saturn": SATURN}


def available() -> bool:
    return _swe is not None


def version() -> str:
    return ENGINE_VERSION if _swe is None else f"swe-{_swe.version}"


def julian_day_ut(ms_utc: int) -> float:
    return ms_utc / 86400000.0 + 2440587.5


def ayanamsa_deg(ms_utc: int) -> float:
    if _swe is None:
        raise RuntimeError("swisseph is not available")
    _swe.set_sid_mode(SIDM_LAHIRI)
    return _swe.get_ayanamsa_ut(julian_day_ut(ms_utc))


def _sidereal(lon_tropical: float, aya: float) -> float:
    return (lon_tropical - aya) % 360.0


def compute_positions(ms_utc: int) -> dict:
    """The nine grahas: sidereal longitudes, speeds, retrograde flags.

    Returns {name: {lon_t, lon_s, speed_t, retro, err_arcmin}} or raises
    RuntimeError when swisseph is unavailable."""
    if _swe is None:
        raise RuntimeError("swisseph is not available")
    jd = julian_day_ut(ms_utc)
    aya = ayanamsa_deg(ms_utc)
    out: dict = {}
    for name, body_id in _BODIES.items():
        pos, _flags = _swe.calc_ut(jd, body_id, _swe.FLG_SPEED)
        lon_t, lat, dist, lon_speed, lat_speed, dist_speed = pos
        out[name] = {
            "lon_t": lon_t,
            "lon_s": _sidereal(lon_t, aya),
            "speed_t": lon_speed,
            "retro": lon_speed < 0 and name not in ("Sun", "Moon"),
        }
    # Mean lunar node (Rahu); Ketu = +180°.
    rahu_t = _swe.calc_ut(jd, RAHU)[0][0]
    out["Rahu"] = {"lon_t": rahu_t, "lon_s": _sidereal(rahu_t, aya),
                   "speed_t": 0.0, "retro": True}
    out["Ketu"] = {"lon_t": (rahu_t + 180.0) % 360.0,
                   "lon_s": _sidereal(rahu_t + 180.0, aya),
                   "speed_t": 0.0, "retro": True}
    return out


def ascendant_and_houses(ms_utc: int, lat: float, lon: float) -> dict:
    """Ascendant (true, geocentric) and the 12 house cusps, sidereal.
    Whole-sign houses (the translation's convention) are derived from the
    ascendant sign; the Placidus cusps are included for scholar use."""
    if _swe is None:
        raise RuntimeError("swisseph is not available")
    jd = julian_day_ut(ms_utc)
    aya = ayanamsa_deg(ms_utc)
    cusps, ascmc = _swe.houses(jd, lat, lon, b"P")
    asc_t = ascmc[0]
    mc_t = ascmc[1]
    asc_s = _sidereal(asc_t, aya)
    mc_s = _sidereal(mc_t, aya)
    asc_sign = int(asc_s // 30)
    return {
        "ascendant_tropical": asc_t,
        "ascendant_sidereal": asc_s,
        "midheaven_tropical": mc_t,
        "midheaven_sidereal": mc_s,
        "ascendant_sign_index": asc_sign,
        "whole_sign_houses": [(asc_sign + i) % 12 for i in range(12)],
        "placidus_cusps_sidereal": [_sidereal(c, aya) for c in cusps[:12]],
    }


def compare_to_approximation(ms_utc: int) -> dict:
    """Cross-check the Swiss-Ephemeris engine against the validated
    approximation engine (sky_engine). For tests and the Tribunal."""
    from app.services import sky_engine

    if _swe is None:
        return {"available": False}
    swe_pos = compute_positions(ms_utc)
    approx = sky_engine.compute_sky(ms_utc)
    deltas = {}
    for name in _BODIES:
        d = abs((swe_pos[name]["lon_s"] - approx.bodies[name]["lon_s"] + 540.0) % 360.0 - 180.0)
        deltas[name] = round(d, 6)
    d_rahu = abs((swe_pos["Rahu"]["lon_s"] - approx.bodies["Rahu"]["lon_s"] + 540.0) % 360.0 - 180.0)
    deltas["Rahu"] = round(d_rahu, 6)
    deltas["Ketu"] = round(d_rahu, 6)
    return {
        "available": True,
        "worst_delta_deg": max(deltas.values()),
        "deltas_deg": deltas,
        "engine": version(),
        "note": "sky_engine is the fast visual layer; swe is the source of "
                "truth for served chart facts.",
    }
