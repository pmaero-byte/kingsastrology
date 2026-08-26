from __future__ import annotations

from dataclasses import asdict

from app.domain.models import Rule
from app.services.rule_loader import RuleRepository


SECTION_ORDER = [
    "who_you_are",
    "your_strengths",
    "what_to_tend",
    "your_vocation",
    "the_season_you_are_in",
    "source_tables",
]

SECTION_TITLES = {
    "who_you_are": "Who You Are",
    "your_strengths": "Your Strengths",
    "what_to_tend": "What to Tend",
    "your_vocation": "Your Vocation",
    "the_season_you_are_in": "The Season You Are In",
    "source_tables": "Source Tables",
}


def compose_reading(
    repository: RuleRepository,
    matched_rule_ids: list[str],
    *,
    allow_draft: bool = False,
) -> dict:
    """Assemble matched rules into deterministic reading sections.

    This is not a chart engine. The caller supplies rule IDs that were matched by a
    deterministic evaluator. Until scholar review exists, draft rules must be
    explicitly allowed for development previews.
    """

    rules = [repository.require_rule(rule_id) for rule_id in matched_rule_ids]
    draft_rules = [rule for rule in rules if not rule.is_verified]
    if draft_rules and not allow_draft:
        draft_ids = ", ".join(rule.id for rule in draft_rules)
        raise ValueError(f"Unverified rules cannot be composed for production: {draft_ids}")

    grouped: dict[str, list[Rule]] = {section: [] for section in SECTION_ORDER}
    for rule in rules:
        grouped[_section_for_rule(rule)].append(rule)

    sections = []
    for section_id in SECTION_ORDER:
        section_rules = grouped[section_id]
        if not section_rules:
            continue
        sections.append(
            {
                "id": section_id,
                "title": SECTION_TITLES[section_id],
                "claims": [_claim_from_rule(rule) for rule in section_rules],
            }
        )

    return {
        "feature": "one_way_reading_preview",
        "scope": {"min_chapter": repository.min_chapter, "max_chapter": repository.max_chapter},
        "verification_passed": bool(rules) and all(rule.is_verified for rule in rules),
        "artifact_status": "verified" if all(rule.is_verified for rule in rules) else "draft_preview",
        "sections": sections,
        "provenance": {
            "rulebase_source": "markdown",
            "supported_chapters": f"{repository.min_chapter}-{repository.max_chapter}",
            "runtime_ai": False,
        },
    }


def _section_for_rule(rule: Rule) -> str:
    if rule.classification == "table":
        return "source_tables"
    if rule.chapter == 8:
        return "the_season_you_are_in"
    if rule.chapter == 10:
        return "your_vocation"
    if rule.chapter in {16, 17, 18} and rule.classification in {"neutral", "strength"}:
        return "who_you_are"
    if rule.classification == "strength":
        return "your_strengths"
    if rule.classification == "tend":
        return "what_to_tend"
    return "who_you_are"


def _claim_from_rule(rule: Rule) -> dict:
    payload = asdict(rule)
    payload["source_file"] = str(rule.source_file)
    return {
        "rule_id": rule.id,
        "chapter": rule.chapter,
        "title": rule.title,
        "classification": rule.classification,
        "status": rule.status,
        "effect": rule.effect,
        "citations": payload["citations"],
        "warnings": rule.warnings,
    }
