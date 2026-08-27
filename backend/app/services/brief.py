"""
The Daily Brief — the almanac spoken plainly, in the visitor's own tongue.

al-Bīruni's rules, applied to a common person's morning:
  1. Measure before asserting  — every line is rendered from computed zīj
     facts by fixed templates; no AI runs at runtime (AGENTS.md §6), so the
     same instant always yields the same words (determinism is tested).
  2. Certain and conjectural never share a voice — each line carries its
     tier: measured astronomy, or labelled convention.
  3. Translate everything — English, हिंदी, العربية.
  4. Refuse flattery — the Brief informs ("the Moon is in X"), it never
     promises ("your day will be great"). No line is a verdict.
"""
from __future__ import annotations

from typing import Any

from app.services import panchanga
from app.services import sky_engine

ENGINE_VERSION = "brief-1.0.0"
DAY = 86_400_000

LANGS = ("en", "hi", "ar")

VARA_T = {
    "en": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    "hi": ["रविवार", "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"],
    "ar": ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"],
}
LORD_T = {
    "en": {"Sun": "the Sun", "Moon": "the Moon", "Mars": "Mars", "Mercury": "Mercury",
           "Jupiter": "Jupiter", "Venus": "Venus", "Saturn": "Saturn"},
    "hi": {"Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध",
           "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि"},
    "ar": {"Sun": "الشمس", "Moon": "القمر", "Mars": "المريخ", "Mercury": "عطارد",
           "Jupiter": "المشتري", "Venus": "الزهرة", "Saturn": "زحل"},
}
PAKSHA_T = {"en": {"Shukla": "waxing", "Krishna": "waning"},
            "hi": {"Shukla": "शुक्ल", "Krishna": "कृष्ण"},
            "ar": {"Shukla": "الشهر المتزايد", "Krishna": "الشهر المتناقص"}}


def _fmt(ms: int | None) -> str | None:
    if ms is None:
        return None
    import datetime
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime("%H:%M")


def daily_brief(ms_utc: int, lat: float, lon: float, elev_m: float = 0.0,
                lang: str = "en") -> dict[str, Any]:
    if lang not in LANGS:
        lang = "en"
    now = panchanga.now_strip(ms_utc, lat, lon, elev_m)
    rs = now["rise_set"]
    t = now["tithi"]
    nak = now["nakshatra"]
    wd = now["vara"]["index"]
    lines: list[dict[str, str]] = []

    # Line 1 — the day and its lord [measured convention of naming].
    lines.append({
        "tier": "measured",
        "en": f"Today is {VARA_T['en'][wd]}, ruled by {LORD_T['en'][now['vara']['lord']]}.",
        "hi": f"आज {VARA_T['hi'][wd]} है — स्वामी {LORD_T['hi'][now['vara']['lord']]}।",
        "ar": f"اليوم {VARA_T['ar'][wd]}، وسيّده {LORD_T['ar'][now['vara']['lord']]}.",
    })

    # Line 2 — the Moon's place [measured].
    moon_sign_sa = now["moon_sign"]["sanskrit"]
    paksha_key = "Shukla" if "Shukla" in t["label"] else "Krishna"
    lines.append({
        "tier": "measured",
        "en": f"The Moon is in {nak['name']} nakshatra (pada {nak['pada']}), "
              f"in {moon_sign_sa} rasi — the tithi is {t['label']}.",
        "hi": f"चंद्रमा {nak['name']} नक्षत्र (पद {nak['pada']}) में, "
              f"{moon_sign_sa} राशि में है — आज {PAKSHA_T['hi'][paksha_key]} पक्ष की {t['name']} तिथि है।",
        "ar": f"القمر في منزلة {nak['name']} (الربع {nak['pada']}) وبرج {moon_sign_sa} — "
              f"واليوم {t['label']}.",
    })

    # Line 3 — the lights' timetable [measured, topocentric].
    lines.append({
        "tier": "measured",
        "en": f"Sunrise {_fmt(rs['sunrise'])}, sunset {_fmt(rs['sunset'])} — "
              f"moonrise {_fmt(rs['moonrise'])}, moonset {_fmt(rs['moonset'])}.",
        "hi": f"सूर्योदय {_fmt(rs['sunrise'])}, सूर्यास्त {_fmt(rs['sunset'])} — "
              f"चंद्रोदय {_fmt(rs['moonrise'])}, चंद्रास्त {_fmt(rs['moonset'])}।",
        "ar": f"الشروق {_fmt(rs['sunrise'])} والغروب {_fmt(rs['sunset'])} — "
              f"طلوع القمر {_fmt(rs['moonrise'])} وغروبه {_fmt(rs['moonset'])}.",
    })

    # Line 4 — the day's windows, labelled as convention, never a verdict.
    mu, rk = now["muhurtas"], now["rahu_kaal"]
    lines.append({
        "tier": "convention",
        "en": f"Abhijit window {_fmt(mu['abhijit']['starts'])}–{_fmt(mu['abhijit']['ends'])}; "
              f"Rahu Kaal {_fmt(rk['starts'])}–{_fmt(rk['ends'])}. "
              f"These are traditional timing conventions — information, not instruction.",
        "hi": f"अभिजीत मुहूर्त {_fmt(mu['abhijit']['starts'])}–{_fmt(mu['abhijit']['ends'])}; "
              f"राहु काल {_fmt(rk['starts'])}–{_fmt(rk['ends'])}। "
              f"ये परंपरागत समय-परंपरा हैं — सूचना है, निर्देश नहीं।",
        "ar": f"نافذة أبهيجيت {_fmt(mu['abhijit']['starts'])}–{_fmt(mu['abhijit']['ends'])}؛ "
              f"كالة راهو {_fmt(rk['starts'])}–{_fmt(rk['ends'])}. "
              f"هذه أعراف تقليدية للتوقيت — معلومة، لا توجيه.",
    })

    # Tomorrow — the one measured glance ahead (no promises attached).
    t1 = panchanga.tithi_of(_elongation(ms_utc + DAY))
    nak1 = panchanga.nakshatra_of_full(ms_utc + DAY)
    tomorrow = {
        "tier": "measured",
        "en": f"Tomorrow: {nak1['name']} nakshatra, tithi {t1['label']}.",
        "hi": f"कल: {nak1['name']} नक्षत्र, तिथि {t1['label']}।",
        "ar": f"غدًا: منزلة {nak1['name']}، وتيثي {t1['label']}.",
    }

    return {
        "lang": lang,
        "timestamp_ms_utc": ms_utc,
        "lines": [{**line, "text": line[lang]} for line in lines],
        "tomorrow": {**tomorrow, "text": tomorrow[lang]},
        "facts": {  # the machinery, for the curious (al-Bīruni: teach fully)
            "tithi": t, "nakshatra": nak, "yoga": now["yoga"], "karana": now["karana"],
            "sun_sign": now["sun_sign"], "moon_sign": now["moon_sign"],
        },
        "skill_statement": "The Brief reports measured sky facts in plain language. "
                           "It predicts nothing, promises nothing, and fears nothing.",
        "provenance": {"engine": ENGINE_VERSION, "runtime_ai": False,
                       "zij_engine": "zij-1.0.0",
                       "note": "rendered by fixed templates from computed facts; "
                               "conventions are labelled on their own lines"},
    }


def _elongation(ms: int) -> float:
    ml, _, _ = sky_engine.moon_ecliptic(ms)
    sl = sky_engine.sun_ecliptic(ms)
    return (ml - sl) % 360.0
