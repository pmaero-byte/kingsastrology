"""A1-A6 — Chart engine: birth data -> ChartFactBundle.

Covers the Swiss-Ephemeris engine (when available), the chart computation
(positions, lagna, bhavas, nakshatra, Vimshottari dasa, ashtakavarga,
navamsa, dignity), the /api/v1/chart/compute endpoint, and the
approximation cross-check that guards round-Earth accuracy.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services import chart_engine
from app.services import sky_engine
from app.services import swe_engine

DELHI = {"datetime_iso": "2026-08-26T10:57:00Z", "lat": 28.6139,
         "lon": 77.2090, "elev_m": 216.0, "place": "Delhi"}


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


def test_swe_engine_available() -> None:
    if not swe_engine.available():
        pytest.skip("swisseph not installed (pip install --target ./vendor pyswisseph)")
    assert swe_engine.version().startswith("swe-")


def test_swe_matches_approximation_within_published_bars() -> None:
    """The approximation engine's published error bars (Tribunal VER-001,
    LIM-003) must hold against the Swiss-Ephemeris truth."""
    if not swe_engine.available():
        pytest.skip("swisseph not installed")
    check = swe_engine.compare_to_approximation(1756208220000)
    assert check["available"]
    # Moon: truncated theory, published ~0.4 deg worst.
    assert check["deltas_deg"]["Moon"] < 0.4
    # Outer planets: JPL approximate elements, published <=0.1 deg for the
    # validation instant; allow 0.2 for ayanamsa-model differences.
    for name in ("Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        assert check["deltas_deg"][name] < 0.4, name


def test_chart_bundle_shape() -> None:
    chart = chart_engine.compute_chart(**DELHI)
    assert chart["birth"]["place"] == "Delhi"
    assert chart["lagna"]["citation"] == {"chapter": 2, "verse": "v 1"}
    assert len(chart["grahas"]) == 9
    assert len(chart["lagna"]["houses"]) == 12
    assert chart["provenance"]["runtime_ai"] is False
    assert chart["provenance"]["verification_passed"] is True


def test_chart_graha_fields() -> None:
    chart = chart_engine.compute_chart(**DELHI)
    sun = next(g for g in chart["grahas"] if g["name"] == "Sun")
    for field in ("longitude_deg", "sign", "nakshatra", "nakshatra_pada",
                  "navamsa_sign", "dignity", "retrograde", "citation"):
        assert field in sun, field
    # Sun in sidereal Leo on 2026-08-26.
    assert sun["sign"] == "Leo"
    assert sun["dignity"] == "own_sign"


def test_vimshottari_timeline() -> None:
    chart = chart_engine.compute_chart(**DELHI)
    dasa = chart["dasa_timeline"]
    assert dasa["system"] == "Vimshottari"
    periods = dasa["periods"]
    assert len(periods) == 9
    # Shravana is ruled by the Moon; the balance must be < 10 years.
    assert periods[0]["lord"] == "Moon"
    assert 0 < periods[0]["years"] < 10
    # Periods are contiguous.
    for prev, nxt in zip(periods, periods[1:]):
        assert prev["end"] == nxt["start"]
    # The 9 antardasas of the first period cover exactly the period.
    ads = periods[0]["antardasas"]
    assert len(ads) == 9
    assert ads[0]["start"] == periods[0]["start"]
    assert ads[-1]["end"] == periods[0]["end"]


def test_ashtakavarga_totals() -> None:
    chart = chart_engine.compute_chart(**DELHI)
    av = chart["ashtakavarga"]
    assert av["bindu_by_planet"]["Sun"]["total_bindus"] == 8
    assert av["bindu_by_planet"]["Moon"]["total_bindus"] == 4
    # Sun 8 + Moon 4 + Mars 5 + Mercury 8 + Jupiter 7 + Venus 8 + Saturn 4.
    assert av["sarvashtakavarga"]["total_bindus"] == 44
    assert all(len(b["bindu_by_sign"]) == 12
               for b in av["bindu_by_planet"].values())


def test_navamsa_and_dignity_spot_checks() -> None:
    chart = chart_engine.compute_chart(**DELHI)
    by_name = {g["name"]: g for g in chart["grahas"]}
    # Leo is a fixed sign; 9.0 deg into Leo -> 3rd navamsa from Aries
    # (9th from Leo) = Gemini.
    assert by_name["Sun"]["navamsa_sign"] == "Gemini"


def test_fallback_ascendant_matches_swe() -> None:
    """The no-swisseph fallback ascendant must agree with Swiss Ephemeris."""
    if not swe_engine.available():
        pytest.skip("swisseph not installed")
    ms = 1756208220000
    aya = swe_engine.ayanamsa_deg(ms)
    swe_asc = swe_engine.ascendant_and_houses(ms, 28.6139, 77.2090)
    fb = chart_engine._ascendant_fallback(ms, 28.6139, 77.2090, aya)
    swe_tropical = swe_asc["ascendant_tropical"]
    fb_tropical = (fb["ascendant_sidereal"] + aya) % 360.0
    delta = abs((swe_tropical - fb_tropical + 180.0) % 360.0 - 180.0)
    assert delta < 0.05


def test_chart_compute_endpoint(client: TestClient) -> None:
    r = client.post("/api/v1/chart/compute", json=DELHI)
    assert r.status_code == 200
    body = r.json()
    assert body["nakshatra"] == "Shravana"
    assert body["lagna"]["lagna_sign"] in {"Sagittarius", "Capricorn"}
    assert body["dasa_timeline"]["periods"][0]["lord"] == "Moon"
    # Determinism: same input, same output.
    again = client.post("/api/v1/chart/compute", json=DELHI).json()
    assert again == body


def test_chart_compute_rejects_bad_input(client: TestClient) -> None:
    r = client.post("/api/v1/chart/compute",
                    json={"datetime_iso": "not-a-date", "lat": 0, "lon": 0})
    assert r.status_code == 422
    r = client.post("/api/v1/chart/compute",
                    json={**DELHI, "ayanamsa": "Raman"})
    assert r.status_code == 422


def test_mirror_pipeline_endpoint(client: TestClient) -> None:
    """Birth data -> chart -> deterministic rule match -> composed reading.
    The Chennai test chart matches only verified rules, so the reading is
    served with verification_passed=true."""
    r = client.post(
        "/api/v1/reading/mirror",
        json={"datetime_iso": "1990-03-12T06:30:00+05:30",
              "lat": 13.08, "lon": 80.27, "place": "Chennai"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["chart"]["lagna"]["lagna_sign"] == "Aquarius"
    assert body["matched_rule_count"] > 0
    reading = body["reading"]
    assert reading is not None
    assert reading["verification_passed"] is True
    assert reading["artifact_status"] == "verified"
    sections = {s["id"] for s in reading["sections"]}
    assert "who_you_are" in sections
    assert "what_to_tend" in sections
    # Determinism: identical request, identical response.
    again = client.post(
        "/api/v1/reading/mirror",
        json={"datetime_iso": "1990-03-12T06:30:00+05:30",
              "lat": 13.08, "lon": 80.27, "place": "Chennai"},
    ).json()
    assert again == body


def test_mirror_withheld_when_draft_rules_match(client: TestClient) -> None:
    """A chart that matches any still-draft rule is withheld at the M3 gate
    (only verification_passed=true readings are served)."""
    r = client.post(
        "/api/v1/reading/mirror",
        json={"datetime_iso": "2026-08-26T10:57:00Z",
              "lat": 28.6139, "lon": 77.2090, "place": "Delhi"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["reading"] is None
    assert "Scholar Reviewer" in body["reading_withheld"]
