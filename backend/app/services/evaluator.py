from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.domain.models import Rule
from app.services.composer import compose_reading
from app.services.rule_loader import RuleRepository


PLANETS = {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"}
SIGNS = {
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
}

_PLANET_SIGN_RE = re.compile(
    r"\b(?P<planet>Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn)\s+"
    r"(?:is\s+)?(?:in|occupies|occupy)\s+sign\s+(?P<sign>[A-Za-z]+)",
    re.IGNORECASE,
)
_PLANET_HOUSE_RE = re.compile(
    r"\b(?P<planet>Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn)\s+"
    r"(?:occupies|occupy|in)\s+(?:one\s+of\s+)?(?:houses?\s+)?(?P<house>[0-9]+)",
    re.IGNORECASE,
)
_MOON_NAKSHATRA_RE = re.compile(
    r"\bMoon\s+(?:is\s+)?(?:in|occupies)\s+(?:nakshatra\s+)?(?P<nakshatra>[A-Za-z -]+)",
    re.IGNORECASE,
)
_NAVAMSA_RULED_BY_RE = re.compile(
    r"\bMoon\s+occupies\s+a\s+Navamsa\s+ruled\s+by\s+(?P<planet>Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn)",
    re.IGNORECASE,
)

NAVAMSA_RULERS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}


@dataclass
class EvaluationResult:
    matched_rule_ids: list[str]
    matched_rules: list[Rule]
    unsupported_rules: list[str]
    warnings: list[str] = field(default_factory=list)
    reading: dict[str, Any] | None = None


def evaluate_chart(
    repository: RuleRepository,
    facts: dict[str, Any],
    *,
    include_static_rules: bool = False,
    compose: bool = False,
    allow_draft: bool = False,
) -> EvaluationResult:
    normal = _normalize_facts(facts)
    matched: list[Rule] = []
    unsupported: list[str] = []

    for rule in repository.list_rules():
        verdict = _rule_matches(rule, normal, include_static_rules=include_static_rules)
        if verdict is True:
            matched.append(rule)
        elif verdict is None:
            unsupported.append(rule.id)

    reading = None
    if compose and matched:
        reading = compose_reading(
            repository,
            [rule.id for rule in matched],
            allow_draft=allow_draft,
        )

    return EvaluationResult(
        matched_rule_ids=[rule.id for rule in matched],
        matched_rules=matched,
        unsupported_rules=unsupported,
        warnings=[],
        reading=reading,
    )


def _normalize_facts(facts: dict[str, Any]) -> dict[str, Any]:
    planets = {}
    for raw in facts.get("planets", []):
        name = _norm(raw.get("name"))
        if not name:
            continue
        planets[name] = {
            "sign": _norm(raw.get("sign")),
            "house": raw.get("house"),
            "nakshatra": _norm(raw.get("nakshatra")),
            "navamsa_sign": _norm(raw.get("navamsa_sign")),
            "dignity": _norm(raw.get("dignity")),
            "conjunct": {_norm(item) for item in raw.get("conjunct", []) if _norm(item)},
        }

    if "moon" in planets:
        facts.setdefault("moon_sign", planets["moon"].get("sign"))
        facts.setdefault("moon_nakshatra", planets["moon"].get("nakshatra"))
        facts.setdefault("moon_navamsa_sign", planets["moon"].get("navamsa_sign"))
    if "sun" in planets:
        facts.setdefault("sun_navamsa_sign", planets["sun"].get("navamsa_sign"))

    return {
        "lagna_sign": _norm(facts.get("lagna_sign")),
        "moon_sign": _norm(facts.get("moon_sign")),
        "moon_nakshatra": _norm(facts.get("moon_nakshatra")),
        "moon_navamsa_sign": _norm(facts.get("moon_navamsa_sign")),
        "sun_navamsa_sign": _norm(facts.get("sun_navamsa_sign")),
        "planets": planets,
        "aspects_to_moon": {_norm(item) for item in facts.get("aspects_to_moon", []) if _norm(item)},
        "aspects_to_sun": {_norm(item) for item in facts.get("aspects_to_sun", []) if _norm(item)},
    }


def _rule_matches(rule: Rule, facts: dict[str, Any], *, include_static_rules: bool) -> bool | None:
    condition = " ".join(rule.condition.split())
    condition_l = condition.lower()

    if rule.chapter == 20:
        return _chapter_20_matches(rule, facts)

    if condition_l.startswith("static lookup"):
        return include_static_rules

    if "all seven planets" in condition_l:
        return _all_planets_sign_quality_matches(condition_l, facts)

    planet_sign = _planet_sign_match(condition, facts)
    if planet_sign is not None:
        return planet_sign

    moon_aspect = _moon_aspect_table_match(condition, facts)
    if moon_aspect is not None:
        return moon_aspect

    navamsa = _moon_navamsa_match(condition, facts)
    if navamsa is not None:
        return navamsa

    nakshatra = _moon_nakshatra_match(condition, facts)
    if nakshatra is not None:
        return nakshatra

    conjunction = _conjunction_match(condition, facts)
    if conjunction is not None:
        return conjunction

    return None


def _chapter_20_matches(rule: Rule, facts: dict[str, Any]) -> bool:
    planet_by_rule = {
        "R-20.1": "sun",
        "R-20.2": "moon",
        "R-20.3": "mars",
        "R-20.4": "mercury",
        "R-20.5": "jupiter",
        "R-20.6": "venus",
        "R-20.7": "saturn",
    }
    if rule.id in planet_by_rule:
        planet = facts["planets"].get(planet_by_rule[rule.id])
        return bool(planet and planet.get("house"))
    if rule.id in {"R-20.8", "R-20.9", "R-20.10"}:
        return any(planet.get("house") for planet in facts["planets"].values())
    return False


def _planet_sign_match(condition: str, facts: dict[str, Any]) -> bool | None:
    match = _PLANET_SIGN_RE.search(condition)
    if not match:
        return None
    planet = _norm(match.group("planet"))
    sign = _norm(match.group("sign"))
    return facts["planets"].get(planet, {}).get("sign") == sign


def _moon_aspect_table_match(condition: str, facts: dict[str, Any]) -> bool | None:
    if "aspects the moon" not in condition.lower() or "moon occupies sign" not in condition.lower():
        return None
    match = re.search(r"Moon occupies sign (?P<sign>[A-Za-z]+)", condition, re.IGNORECASE)
    if not match:
        return None
    return facts["moon_sign"] == _norm(match.group("sign")) and bool(facts["aspects_to_moon"])


def _moon_navamsa_match(condition: str, facts: dict[str, Any]) -> bool | None:
    ruled_by = _NAVAMSA_RULED_BY_RE.search(condition)
    moon_navamsa = facts.get("moon_navamsa_sign")
    if ruled_by:
        ruler = _norm(ruled_by.group("planet"))
        return bool(moon_navamsa and NAVAMSA_RULERS.get(moon_navamsa) == ruler)
    if "moon occupies a navamsa of sign" in condition.lower():
        match = re.search(r"Moon occupies a Navamsa of sign (?P<sign>[A-Za-z]+)", condition, re.IGNORECASE)
        if match:
            return moon_navamsa == _norm(match.group("sign"))
    return None


def _moon_nakshatra_match(condition: str, facts: dict[str, Any]) -> bool | None:
    if "nakshatra" not in condition.lower():
        return None
    match = _MOON_NAKSHATRA_RE.search(condition)
    if not match:
        return None
    return facts["moon_nakshatra"] == _norm(match.group("nakshatra"))


def _conjunction_match(condition: str, facts: dict[str, Any]) -> bool | None:
    if "conjoined" not in condition.lower():
        return None
    match = re.search(
        r"(?P<a>Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn)\s+and\s+"
        r"(?P<b>Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn)\s+conjoined",
        condition,
        re.IGNORECASE,
    )
    if not match:
        return None
    a = _norm(match.group("a"))
    b = _norm(match.group("b"))
    return b in facts["planets"].get(a, {}).get("conjunct", set()) or a in facts["planets"].get(b, {}).get("conjunct", set())


def _all_planets_sign_quality_matches(condition_l: str, facts: dict[str, Any]) -> bool | None:
    movable = {"aries", "cancer", "libra", "capricorn"}
    fixed = {"taurus", "leo", "scorpio", "aquarius"}
    common = {"gemini", "virgo", "sagittarius", "pisces"}
    if "movable signs" in condition_l:
        allowed = movable
    elif "fixed signs" in condition_l:
        allowed = fixed
    elif "common" in condition_l or "dual" in condition_l:
        allowed = common
    else:
        return None
    visible = [facts["planets"].get(planet, {}).get("sign") for planet in PLANETS if planet != "moon"]
    moon_sign = facts["planets"].get("moon", {}).get("sign") or facts.get("moon_sign")
    signs = visible + [moon_sign]
    return all(sign in allowed for sign in signs if sign) and len([sign for sign in signs if sign]) >= 7


def _norm(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace("_", " ")
