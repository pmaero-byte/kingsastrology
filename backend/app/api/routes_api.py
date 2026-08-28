"""
Layer 5 — The Caravanserai (open API): documented, open endpoints so any
scholar can replicate our numbers from the same pinned tables without asking
permission. All compute is deterministic; no AI runs at runtime.
"""
from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request

from app.api.schemas import BirthDataRequest
from app.services import chart_engine

from app.services import calendars as calendars_svc
from app.services import crescent as crescent_svc
from app.services import brief as brief_svc
from app.services import panchanga as panchanga_svc
from app.services import periods as periods_svc
from app.services import qanun as qanun_svc
from app.services import sky_engine
from app.services import tribunal as tribunal_svc
from app.services import verse_store as verse_store_svc
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


@router.get("/brief")
def brief(
    lang: str = Query(default="en", pattern="^(en|hi|ar)$"),
    timestamp_ms_utc: Optional[int] = Query(default=None),
    lat: float = Query(default=28.6139, ge=-90, le=90),
    lon: float = Query(default=77.2090, ge=-180, le=180),
    elev_m: float = Query(default=216.0, ge=-430, le=9000),
) -> dict:
    """The Daily Brief: plain-language, tier-stamped, deterministic."""
    ms = _parse_timestamp(timestamp_ms_utc)
    return brief_svc.daily_brief(ms, lat, lon, elev_m, lang)


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


@router.post("/chart/compute")
def chart_compute(payload: BirthDataRequest) -> dict:
    """Birth data -> ChartFactBundle (A1-A6): positions, lagna, bhavas,
    nakshatra, Vimshottari dasa timeline, ashtakavarga. Deterministic; no
    AI; every doctrinal field cites (chapter, verse)."""
    if payload.ayanamsa.lower() not in ("lahiri",):
        raise HTTPException(status_code=422,
                            detail="Only Lahiri ayanamsa is supported at this version")
    try:
        return chart_engine.compute_chart(
            payload.datetime_iso,
            payload.lat,
            payload.lon,
            elev_m=payload.elev_m,
            place=payload.place,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/reading/mirror")
def reading_mirror(payload: BirthDataRequest, request: Request) -> dict:
    """The Mirror pipeline in one call: birth data -> computed chart ->
    deterministic rule evaluation -> composed one-way reading. No AI runs
    at runtime; draft rules are excluded unless allow_draft."""
    if payload.ayanamsa.lower() not in ("lahiri",):
        raise HTTPException(status_code=422,
                            detail="Only Lahiri ayanamsa is supported at this version")
    chart = chart_engine.compute_chart(
        payload.datetime_iso, payload.lat, payload.lon,
        elev_m=payload.elev_m, place=payload.place,
    )
    repository = request.app.state.rule_repository
    from app.services.composer import compose_reading
    from app.services.evaluator import evaluate_chart

    result = evaluate_chart(repository, chart_engine.chart_facts(chart),
                            include_static_rules=True, compose=False,
                            allow_draft=False)
    try:
        reading = compose_reading(repository, result.matched_rule_ids,
                                  allow_draft=False)
        withheld_reason = None
    except ValueError as exc:
        # The composer withholds the reading while the matched rules are
        # still draft (AGENTS.md §4: only verification_passed=true readings
        # are served). This is the M3 scholar-review gate, not an error.
        reading = None
        withheld_reason = (
            "Reading withheld — a human Scholar Reviewer must verify the "
            f"matched draft rules before a reading may be served: {exc}"
        )
    payload = {
        "chart": chart,
        "matched_rule_ids": result.matched_rule_ids,
        "matched_rule_count": len(result.matched_rules),
        "unsupported_rule_count": len(result.unsupported_rules),
        "reading": reading,
    }
    if reading is None:
        payload["reading_withheld"] = withheld_reason
    return payload


# ------------------------------------------------------------------ verse store

@router.get("/verse-store/manifest")
def verse_store_manifest() -> dict:
    """The Verse Store manifest: version, source, counts, policy."""
    return verse_store_svc.manifest()


@router.get("/verse-store/uncertain")
def verse_store_uncertain() -> dict:
    """Verses flagged for Scholar Reviewer clearance (OCR damage, ambiguous
    numbering, truncation). Nothing in this list is served as verified."""
    return {
        "count": len(verse_store_svc.uncertain()),
        "entries": verse_store_svc.uncertain(),
        "provenance": {"verse_store_version": verse_store_svc.version()},
    }


@router.get("/verse/{chapter}")
def verse_chapter(chapter: int) -> dict:
    """All verses of one chapter (the translation's own numbering)."""
    verses = verse_store_svc.verses_for_chapter(chapter)
    if not verses:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter} is not in the verse store")
    title = next(
        (ch["title"] for ch in verse_store_svc.chapter_index() if ch["chapter"] == chapter),
        "",
    )
    return {
        "chapter": chapter,
        "title": title,
        "verse_count": len(verses),
        "verses": verses,
        "provenance": {"verse_store_version": verse_store_svc.version()},
    }


@router.get("/verse/{chapter}/{verse_expr}")
def verse_lookup(chapter: int, verse_expr: str) -> dict:
    """One or more verses by the translation's numbering. verse_expr may be
    "5", a range "1-3", or a list "1, 4". Powers tap-to-verse."""
    verses = verse_store_svc.resolve(chapter, verse_expr)
    if not verses:
        raise HTTPException(
            status_code=404,
            detail=f"No verse {chapter}.{verse_expr} in the verse store",
        )
    return {
        "chapter": chapter,
        "requested": verse_expr,
        "verse_count": len(verses),
        "verses": verses,
        "provenance": {"verse_store_version": verse_store_svc.version()},
    }


@router.get("/citation-check")
def citation_check(request: Request) -> dict:
    """Every rule citation in the loaded rule-base, resolved against the
    Verse Store. The citation guardrail (AGENTS.md §4) is a build-time gate:
    unresolved citations must be fixed or the citing rule must not ship."""
    repository = request.app.state.rule_repository
    all_citations: list[dict] = []
    unresolved: list[dict] = []
    for rule in repository.list_rules():
        for citation in rule.citations:
            if citation.chapter is None:
                continue
            found = verse_store_svc.resolve(citation.chapter, citation.verse or "")
            entry = {
                "rule_id": rule.id,
                "raw": citation.raw,
                "chapter": citation.chapter,
                "verse_expr": citation.verse,
                "resolved": bool(found),
            }
            all_citations.append(entry)
            if not found:
                unresolved.append(entry)
    by_chapter: dict[str, dict] = {}
    for entry in all_citations:
        key = str(entry["chapter"])
        bucket = by_chapter.setdefault(key, {"total": 0, "resolved": 0})
        bucket["total"] += 1
        bucket["resolved"] += 1 if entry["resolved"] else 0
    resolved_count = sum(1 for entry in all_citations if entry["resolved"])
    return {
        "verse_store_version": verse_store_svc.version(),
        "citations_checked": len(all_citations),
        "resolved": resolved_count,
        "unresolved": len(all_citations) - resolved_count,
        "resolution_rate": round(resolved_count / max(len(all_citations), 1), 4),
        "by_chapter": by_chapter,
        "unresolved_citations": unresolved,
        "provenance": {"engine": "citation-check-1.0.0", "runtime_ai": False},
    }
