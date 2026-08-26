"""
Layer 5 — The Caravanserai (open API): documented, open endpoints so any
scholar can replicate our numbers from the same pinned tables without asking
permission. All compute is deterministic; no AI runs at runtime.
"""
from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services import calendars as calendars_svc
from app.services import crescent as crescent_svc
from app.services import panchanga as panchanga_svc
from app.services import periods as periods_svc
from app.services import qanun as qanun_svc
from app.services import sky_engine
from app.services import tribunal as tribunal_svc
from app.services import zij as zij_svc

router = APIRouter(prefix="/api/v1")


def _parse_timestamp(timestamp_ms_utc: Optional[int]) -> int:
    if timestamp_ms_utc is None:
        return int(time.time() * 1000)
    return timestamp_ms_utc


@router.get("/zij/manifest")
def zij_manifest() -> dict:
    return zij_svc.manifest()


@router.get("/zij/row")
def zij_row(timestamp_ms_utc: Optional[int] = Query(default=None)) -> dict:
    return zij_svc.zij_row(_parse_timestamp(timestamp_ms_utc))


@router.get("/sky")
def sky(
    timestamp_ms_utc: Optional[int] = Query(default=None),
    lat: Optional[float] = Query(default=None, ge=-90, le=90),
    lon: Optional[float] = Query(default=None, ge=-180, le=180),
    elev_m: float = Query(default=0.0, ge=-430, le=9000),
) -> dict:
    """The full record for one instant: zij row + cited factors (+ calendars)."""
    ms = _parse_timestamp(timestamp_ms_utc)
    row = zij_svc.zij_row(ms)
    return {
        "zij": row,
        "qanun": qanun_svc.factors_payload(row, lat, lon, elev_m),
        "calendars": calendars_svc.all_calendars(row["jd"]),
    }


@router.get("/calendars")
def calendars(timestamp_ms_utc: Optional[int] = Query(default=None)) -> dict:
    jd = sky_engine.julian_day(_parse_timestamp(timestamp_ms_utc))
    return calendars_svc.all_calendars(jd)


@router.get("/crescent")
def crescent(
    timestamp_ms_utc: Optional[int] = Query(default=None),
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    elev_m: float = Query(default=0.0, ge=-430, le=9000),
) -> dict:
    ms = _parse_timestamp(timestamp_ms_utc)
    result = crescent_svc.visibility(ms, lat, lon, elev_m)
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return result


@router.get("/tribunal")
def tribunal() -> dict:
    return tribunal_svc.ledger()


@router.get("/now")
def now_strip(
    lat: float = Query(default=28.6139, ge=-90, le=90),
    lon: float = Query(default=77.2090, ge=-180, le=180),
    elev_m: float = Query(default=216.0, ge=-430, le=9000),
) -> dict:
    """The live moment: panchanga, hora, muhurtas, calendars — the daily strip."""
    ms = int(time.time() * 1000)
    payload = panchanga_svc.now_strip(ms, lat, lon, elev_m)
    payload["calendars"] = calendars_svc.all_calendars(sky_engine.julian_day(ms))
    return payload


@router.get("/report/day")
def report_day(
    timestamp_ms_utc: Optional[int] = Query(default=None),
    lat: float = Query(default=28.6139, ge=-90, le=90),
    lon: float = Query(default=77.2090, ge=-180, le=180),
    elev_m: float = Query(default=216.0, ge=-430, le=9000),
) -> dict:
    return periods_svc.report_day(_parse_timestamp(timestamp_ms_utc), lat, lon, elev_m)


@router.get("/report/week")
def report_week(
    timestamp_ms_utc: Optional[int] = Query(default=None),
    lat: float = Query(default=28.6139, ge=-90, le=90),
    lon: float = Query(default=77.2090, ge=-180, le=180),
    elev_m: float = Query(default=216.0, ge=-430, le=9000),
) -> dict:
    return periods_svc.report_week(_parse_timestamp(timestamp_ms_utc), lat, lon, elev_m)


@router.get("/report/month")
def report_month(
    timestamp_ms_utc: Optional[int] = Query(default=None),
    lat: float = Query(default=28.6139, ge=-90, le=90),
    lon: float = Query(default=77.2090, ge=-180, le=180),
    elev_m: float = Query(default=216.0, ge=-430, le=9000),
) -> dict:
    return periods_svc.report_month(_parse_timestamp(timestamp_ms_utc), lat, lon, elev_m)


@router.get("/report/year")
def report_year(
    timestamp_ms_utc: Optional[int] = Query(default=None),
    lat: float = Query(default=28.6139, ge=-90, le=90),
    lon: float = Query(default=77.2090, ge=-180, le=180),
    elev_m: float = Query(default=216.0, ge=-430, le=9000),
) -> dict:
    return periods_svc.report_year(_parse_timestamp(timestamp_ms_utc), lat, lon, elev_m)
