# 15 — The Spacetime Clock

*The court's living orrery: the grahas riding a curved sheet of spacetime, wrapped in a sidereal zodiac bezel like a clock face.*

---

## What it is

The Spacetime Clock (`/clock`) is the product's **major attraction** — a live, animated visualization inspired by the viral "gravity well" animation (the Sun's gravity holding the planets on a curved spacetime grid). It renders:

- **The fabric** — a schematic polar grid that dips toward the centre (the gravity-well look), drawn once per layout into a cached layer.
- **The court** — all nine grahas at their **true geocentric sidereal positions**, glowing and labelled, with motion trails when time is accelerated.
- **The clock face** — a sidereal zodiac bezel (Lahiri) with 12 rasi sectors; 0° Mesha at the crown. A gold solar hand and a teal lunar hand point at the Sun's and Moon's current longitudes. **Earth is the hub** — the product is geocentric, so the observer sits at the centre of the clock.
- **The Moon's halo** — the Moon's orbit is drawn enlarged around Earth with Rahu/Ketu on it and the shadow axis connecting them (eclipse axis).

## Where it lives

| File | Role |
|----|----|
| `backend/app/web/ephemeris.js` | Pure astronomy module — no DOM. Geocentric longitudes, sidereal conversion, rasi/nakshatra mapping. |
| `backend/app/web/clock.js` | Stage geometry, gravity-well renderer, zodiac bezel, hands, trails, time controls, legend. |
| `backend/app/web/clock.html` / `clock.css` | Page shell and Royal-Review-themed styling. |
| `backend/app/main.py` | Serves the page at `GET /clock`; assets under `/assets/…`. |
| `backend/tests/test_spacetime_clock.py` | Route + asset smoke tests. |

Run it:

```bash
cd backend && uvicorn app.main:app --port 8000
# open http://127.0.0.1:8000/clock
```

## Accuracy and provenance (charter pillar II — round-Earth accuracy)

- **Planets (Mercury–Saturn) and Sun:** JPL *approximate positions* Keplerian elements (valid 1800–2050), full heliocentric → geocentric transformation, Kepler's equation solved by Newton iteration. **Verified against PyEphem for 2026-08-26 10:57 UT: every planet within 0.1°, Moon within 0.36°.**
- **Moon:** Schlyter's truncated lunar theory (evection, variation, yearly equation, +9 lesser terms).
- **Rahu/Ketu:** mean lunar node (Meeus polynomial); Ketu = Rahu + 180°.
- **Sidereal:** Lahiri (Chitrapaksha) ayanamsa approximation — arcminute-level across 1950–2050.
- **Honest compression (disclosed in the page footer):** orbit radii are compressed (`r^0.45`) and the Moon's orbit enlarged for legibility; the fabric is schematic. Angles — the astrologically meaningful quantity — are never compressed or altered.
- **Retrograde** is detected by finite difference (±12 h), never asserted by rule of thumb.

This module is **visualization-grade and display-only**. It makes no doctrinal claims, so no counselor/guardrail pipeline is triggered (AGENTS.md §5 applies to readings, not computed positions). When the Phase-0 Swiss-Ephemeris compute engine (A1) lands, it becomes the source of truth for any *served fact*; this module remains the fast visual layer.

## Interactions

- **Now** — snap back to the living sky (LIVE badge glows teal).
- **Play/Pause** (or Space) — freeze or run time at the chosen speed.
- **Speed** — real time, 1 hour/s, 1 day/s, 1 week/s, 1 month/s. At accelerated speeds each graha leaves a fading trail — watch Mars and Mercury draw their retrograde loops.
- **Date-time picker** — jump to any moment (e.g. your birth date to preview your graha placements; a full reading still requires the computed `ChartFactBundle`).
- **← / →** — step ±1 day.

## Deliberate design decisions

1. **Earth-centred, not Sun-centred.** The viral video is heliocentric; our product is Vedic and therefore geocentric. Earth sits at the clock's hub, the Sun rides its annual circle as the court's largest lamp, and retrograde loops appear naturally and truthfully. The gravity-well fabric stays as the visual homage.
2. **Sidereal, not tropical.** The bezel and all labels use Lahiri sidereal longitudes so the screen matches the product's rasi language everywhere.
3. **No astrological verdicts on this screen.** The legend states placements only (rasi, degree, nakshatra, retrograde). Interpretation belongs to the cited, tone-gated reading pipeline.

## Future hooks

- Overlay a user's **natal placements** as fixed markers against the live sky (transit view) once the chart API serves `ChartFactBundle`s.
- **Panchanga strip** (tithi, vara, nakshatra, yoga, karana) computed from the same engine.
- Replace the ayanamsa/element approximations with the Swiss-Ephemeris engine behind a `/sky` JSON endpoint; the canvas layer then renders server-computed truth.
- Native ports: the geometry is plain math — SwiftUI Canvas / Jetpack Compose Canvas can reuse `ephemeris.js` logic ported directly.
