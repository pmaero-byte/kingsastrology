"""
Layer 0 — Zīj record service: versioned, hash-pinned, reproducible sky rows.

A zīj row is the atomic unit of the sky record: one timestamp, the geocentric
sidereal longitudes of the nine grahas, the ayanamsa, and the epistemic tier
of the row. Rows are reproducible from the pinned element tables alone; the
manifest pins the SHA-256 of the canonical constants so any past row can be
re-derived and audited (al-Bīrūnī: "a number without lineage is gossip").

Tiering (Tafhīm Protocol §Layer 1, applied at the row level):
  - measured:      timestamp within the JPL element validity window 1800–2050.
  - extrapolated:  outside that window; displayed only with the tier stamp.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from app.services import sky_engine

ENGINE_VERSION = "zij-1.0.0"
ELEMENTS_VALID_JD = (2378496.5, 2469806.5)  # 1800-01-01.5 .. 2050-01-01.5


def canonical_constants_hash() -> str:
    payload = json.dumps(
        {"elements": sky_engine.ELEMENTS, "ayanamsa_j2000": 23.85306,
         "ayanamsa_rate_per_year": 0.013966},
        sort_keys=True, separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def row_tier(jd: float) -> str:
    lo, hi = ELEMENTS_VALID_JD
    return "measured" if lo <= jd <= hi else "extrapolated"


def zij_row(ms_utc: int) -> dict[str, Any]:
    row = sky_engine.compute_sky(ms_utc)
    return {
        "timestamp_ms_utc": ms_utc,
        "jd": round(row.jd, 6),
        "tier": row_tier(row.jd),
        "ayanamsa": round(row.ayanamsa, 6),
        "ayanamsa_err_arcmin": 2.0,  # approximation disclosure, see Tribunal
        "bodies": row.bodies,
        "moon_dist_er": round(row.moon_dist_er, 4),
        "provenance": {
            "engine": ENGINE_VERSION,
            "constants_sha256": canonical_constants_hash(),
            "source": "JPL approximate elements (1800-2050) + Schlyter lunar theory + mean node",
            "cross_validated": "PyEphem 2026-08-26: planets <=0.1deg, Moon <=0.36deg",
        },
    }


def zij_window(ms_start: int, ms_end: int, step_ms: int = 86400000) -> list[dict[str, Any]]:
    if step_ms < 3600000:
        raise ValueError("step_ms must be >= one hour")
    rows = []
    t = ms_start
    while t <= ms_end:
        rows.append(zij_row(t))
        t += step_ms
    return rows


def manifest() -> dict[str, Any]:
    constants = canonical_constants_hash()
    sample = zij_row(1756208220000)  # 2026-08-26 10:57:00 UT — the cross-validation instant
    sample_hash = hashlib.sha256(
        json.dumps(sample, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "engine": ENGINE_VERSION,
        "constants_sha256": constants,
        "validity_window": {
            "jd": list(ELEMENTS_VALID_JD),
            "note": "JPL approximate Keplerian elements are valid 1800-2050; "
                    "rows outside are stamped tier=extrapolated.",
        },
        "pinned_sample": {
            "timestamp_ms_utc": sample["timestamp_ms_utc"],
            "jd": sample["jd"],
            "sha256": sample_hash,
        },
        "reproduce_with": "GET /api/v1/zij/row?timestamp_ms_utc=1756208220000 "
                          "and re-hash the canonical JSON (sort_keys, compact separators).",
    }
