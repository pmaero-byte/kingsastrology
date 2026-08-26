"""
Layer 1 — The Qānūn: deterministic factor engine over a Zīj row.

Every factor carries its epistemic tier and its citation, so nothing the
engine says can float free of its source:

  tier="measured"   — geometric/astronomical fact (angles, elongations, altitudes)
  tier="doctrine"   — a classical rule, cited to the project rule-base (rule id
                      + chapter/verse of the Brihat Jataka rule files)
  tier="hypothesis" — under trial; never asserted as verdict

No factor here is an astrological verdict. Factors feed the cited reading
pipeline (composer + tone-gate + ethics), which alone may render counsel.
"""
from __future__ import annotations

from typing import Any

from app.services import sky_engine

ENGINE_VERSION = "qanun-1.0.0"

# R-1.6 — Sign lords.
SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

# R-1.13 — Exaltation signs and degrees of deepest exaltation.
EXALTATION = {
    "Sun": ("Aries", 10.0), "Moon": ("Taurus", 3.0), "Mars": ("Capricorn", 28.0),
    "Mercury": ("Virgo", 15.0), "Jupiter": ("Cancer", 5.0),
    "Venus": ("Pisces", 27.0), "Saturn": ("Libra", 20.0),
}

# R-2.21 — Naisargika bala: each stronger than the one before.
NAISARGIKA_ORDER = ["Saturn", "Mars", "Mercury", "Jupiter", "Venus", "Moon", "Sun"]

# R-2.21 — Kala bala: sect strength by day/night.
NIGHT_STRONG = {"Moon", "Mars", "Saturn"}
DAY_STRONG = {"Sun", "Jupiter", "Venus"}
BOTH_STRONG = {"Mercury"}

SEVEN = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


def _sign_index(lon_s: float) -> int:
    return int(sky_engine.wrap360(lon_s) // 30)


def _wrap180(d: float) -> float:
    return (d + 540.0) % 360.0 - 180.0


def _factor(name: str, tier: str, citation: dict, value: Any, note: str = "") -> dict:
    return {"factor": name, "tier": tier, "citation": citation, "value": value, "note": note}


def sun_altitude(row: dict, lat: float, lon: float, elev_m: float = 0.0) -> float:
    """Geocentric apparent altitude of the Sun for the observer [measured]."""
    ra, dec = sky_engine.ecliptic_to_equatorial(row["bodies"]["Sun"]["lon_t"], 0.0)
    alt, _ = sky_engine.altaz(ra, dec, row["jd"], lat, lon)
    dist_er = row["bodies"]["Sun"]["dist_au"] * 149597870.7 / 6371.0088
    return sky_engine.refraction_corrected(sky_engine.topocentric_alt(alt, dist_er))


def factors(row: dict, lat: float | None = None, lon: float | None = None,
            elev_m: float = 0.0) -> list[dict]:
    out: list[dict] = []
    bodies = row["bodies"]

    # ---- paksha (lunar fortnight) — elongation geometry + R-2.21 pairing ----
    elong = (bodies["Moon"]["lon_t"] - bodies["Sun"]["lon_t"]) % 360.0
    paksha = "Sukla (waxing)" if elong < 180.0 else "Krishna (waning)"
    out.append(_factor(
        "paksha", "measured",
        {"kind": "geometry", "detail": "Moon−Sun elongation"},
        {"elongation_deg": round(elong, 3), "paksha": paksha},
        "Benefics gain strength in Sukla, malefics in Krishna — see kala_bala_sect.",
    ))
    out.append(_factor(
        "kala_bala_paksha", "doctrine",
        {"rule_id": "R-2.21", "chapter": 2, "verse": "v 21 (Kala bala)"},
        {"paksha": paksha,
         "strengthened": (["Jupiter", "Venus", "Mercury*"] if elong < 180.0
                          else ["Saturn", "Mars", "Sun", "Mercury*"]),
         "note_mercury": "Mercury is mutable per R-2.5 — see natural_nature."},
        "Malefics strong in the waning Moon; benefics in the waxing Moon.",
    ))

    # ---- sect (day/night strength), requires an observer ----
    if lat is not None and lon is not None:
        alt = sun_altitude(row, lat, lon, elev_m)
        is_day = alt > 0.0
        sect = "day" if is_day else "night"
        strong = sorted(NIGHT_STRONG if not is_day else DAY_STRONG | BOTH_STRONG)
        out.append(_factor(
            "kala_bala_sect", "doctrine",
            {"rule_id": "R-2.21", "chapter": 2, "verse": "v 21 (Kala bala)"},
            {"sect": sect, "sun_altitude_deg": round(alt, 3),
             "strong_now": strong, "mercury_note": "strong by both day and night"},
            f"Sun {'above' if is_day else 'below'} the horizon at the observer.",
        ))

    # ---- dignity (R-1.13 + R-1.6) ----
    dignities = {}
    for name in SEVEN:
        lon_s = bodies[name]["lon_s"]
        sidx = _sign_index(lon_s)
        sign_name = sky_engine.SIGNS[sidx][0]
        lord = SIGN_LORDS[sidx]
        entry: dict[str, Any] = {"sign": sign_name, "lord": lord, "dignity": "neutral"}
        if name in EXALTATION:
            ex_sign, ex_deg = EXALTATION[name]
            if sign_name == ex_sign:
                entry["dignity"] = "exalted"
                entry["deg_from_deep_exaltation"] = round(abs(_wrap180(bodies[name]["lon_s"] % 30.0 - ex_deg)), 3)
            elif sky_engine.SIGNS[(sidx + 6) % 12][0] == ex_sign:
                entry["dignity"] = "debilitated"
        elif sign_name == lord and name in ("Sun", "Moon"):
            entry["dignity"] = "own sign"
        if lord == name:
            entry["dignity"] = "own sign" if entry["dignity"] == "neutral" else entry["dignity"]
        dignities[name] = entry
    out.append(_factor(
        "dignity", "doctrine",
        {"rule_id": "R-1.13 + R-1.6", "chapter": 1, "verse": "v 13 + v 6"},
        dignities,
        "Exaltation/depression signs and degrees per the canon; own-sign via sign lords.",
    ))

    # ---- natural nature (R-2.5), with measured conjunction test ----
    malefic_fixed = {"Sun", "Mars", "Saturn"}
    moon_waxing = elong < 180.0
    mercury_malefic = any(
        _sign_index(bodies["Mercury"]["lon_s"]) == _sign_index(bodies[m]["lon_s"])
        for m in malefic_fixed
    )
    nature = {}
    for name in SEVEN:
        if name == "Mercury":
            nature[name] = "malefic (conjunct malefic)" if mercury_malefic else "benefic (mutable)"
        elif name == "Moon":
            nature[name] = "benefic (waxing)" if moon_waxing else "malefic (waning)"
        else:
            nature[name] = "malefic" if name in malefic_fixed else "benefic"
    out.append(_factor(
        "natural_nature", "doctrine",
        {"rule_id": "R-2.5", "chapter": 2, "verse": "v 5"},
        nature,
        "Mercury turns with its company; the Moon with its paksha (measured above).",
    ))

    # ---- naisargika rank (R-2.21) ----
    out.append(_factor(
        "naisargika_rank", "doctrine",
        {"rule_id": "R-2.21", "chapter": 2, "verse": "v 21 (Naisargika bala)"},
        {name: i + 1 for i, name in enumerate(NAISARGIKA_ORDER)},
        "Rank 1 = naturally strongest (Saturn), 7 = weakest (Sun).",
    ))

    # ---- drishti (R-2.13) — sign-based sight with 15° orb on house middles ----
    chords = []
    for a_name in SEVEN:
        a_lon = bodies[a_name]["lon_s"]
        a_mid = _sign_index(a_lon) * 30.0 + 15.0
        for b_name in SEVEN:
            if a_name == b_name:
                continue
            b_lon = bodies[b_name]["lon_s"]
            k = (_sign_index(b_lon) - _sign_index(a_lon)) % 12 + 1
            strength = 0.0
            if k == 7:
                strength = 1.0
            elif k in (4, 8):
                strength = 1.0 if (a_name == "Mars") else 0.75
            elif k in (5, 9):
                strength = 1.0 if (a_name == "Jupiter") else 0.5
            elif k in (3, 10):
                strength = 1.0 if (a_name == "Saturn") else 0.25
            if strength <= 0.0:
                continue
            middle = a_mid + (k - 1) * 30.0
            orb = abs(_wrap180(b_lon - middle))
            if orb > 15.0:
                continue
            chords.append({
                "from": a_name, "to": b_name, "house": k,
                "strength": strength, "orb_deg": round(orb, 3),
                "full_sight_special": (a_name, k) in [("Saturn", 3), ("Saturn", 10),
                                                       ("Jupiter", 5), ("Jupiter", 9),
                                                       ("Mars", 4), ("Mars", 8)],
            })
    out.append(_factor(
        "drishti", "doctrine",
        {"rule_id": "R-2.13", "chapter": 2, "verse": "v 13"},
        chords,
        "¼ sight on 3rd/10th, ½ on 5th/9th, ¾ on 4th/8th, full on 7th; "
        "Saturn/Jupiter/Mars specials carry full sight. 15° orb about house middles. "
        "Rahu/Ketu are not part of the R-2.13 table and are excluded.",
    ))

    # ---- Sun separation [measured] — raw geometry, no combustion verdict ----
    seps = {
        name: round(abs(_wrap180(bodies[name]["lon_t"] - bodies["Sun"]["lon_t"])), 3)
        for name in SEVEN if name != "Sun"
    }
    out.append(_factor(
        "sun_separation", "measured",
        {"kind": "geometry", "detail": "angular separation from the Sun"},
        seps,
        "Raw geometry only. This rule-base carries no combustion doctrine; "
        "nothing here is an interpretation.",
    ))

    # ---- dispositor (R-1.6) ----
    out.append(_factor(
        "dispositor", "doctrine",
        {"rule_id": "R-1.6", "chapter": 1, "verse": "v 6"},
        {name: SIGN_LORDS[_sign_index(bodies[name]["lon_s"])] for name in SEVEN},
        "Lord of the sign each graha occupies.",
    ))

    return out


def factors_payload(row: dict, lat: float | None = None, lon: float | None = None,
                    elev_m: float = 0.0) -> dict:
    return {
        "tier_legend": {
            "measured": "geometric/astronomical fact",
            "doctrine": "classical rule, cited to the rule-base",
            "hypothesis": "under trial — never a verdict",
        },
        "factors": factors(row, lat, lon, elev_m),
        "provenance": {
            "engine": ENGINE_VERSION,
            "zij_engine": row["provenance"]["engine"],
            "constants_sha256": row["provenance"]["constants_sha256"],
            "runtime_ai": False,
        },
    }
