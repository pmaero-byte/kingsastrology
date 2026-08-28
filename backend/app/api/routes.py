from __future__ import annotations

from dataclasses import asdict
from typing import Optional
from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.api.schemas import ChartFactBundleRequest, ComposeReadingRequest, SaveRuleReviewRequest
from app.domain.models import ChapterRules, Rule, RuleScope
from app.services.composer import compose_reading
from app.services.evaluator import evaluate_chart
from app.services.review_pages import render_rules_review_page
from app.services.review_store import ReviewStore
from app.services.rule_loader import RuleRepository
from app.services import verse_store as verse_store_svc


router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict:
    repository = _repository(request)
    scope = repository.scope()
    return {
        "ok": True,
        "runtime_ai": False,
        "supported_chapters": f"{scope.min_chapter}-{scope.max_chapter}",
        "loaded_chapters": scope.loaded_chapters,
        "missing_chapters": scope.missing_chapters,
        "total_rules": scope.total_rules,
        "verse_store": verse_store_svc.stats(),
    }


@router.get("/rules/scope")
def rules_scope(request: Request) -> dict:
    return _scope_response(_repository(request).scope())


@router.get("/rules/chapters")
def rules_chapters(request: Request) -> list[dict]:
    repository = _repository(request)
    return [
        _chapter_summary(chapter)
        for chapter in repository.chapters.values()
    ]


@router.get("/rules/chapters/{chapter}")
def rules_for_chapter(chapter: int, request: Request) -> dict:
    chapter_rules = _repository(request).get_chapter(chapter)
    if chapter_rules is None:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter} is not loaded")
    return _chapter_response(chapter_rules)


@router.get("/rules")
def rules(
    request: Request,
    chapter: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
    classification: Optional[str] = Query(default=None),
) -> list[dict]:
    return [
        _rule_response(rule)
        for rule in _repository(request).list_rules(
            chapter=chapter,
            status=status,
            classification=classification,
        )
    ]


@router.get("/rules/by-id/{rule_id}")
def rule_by_id(rule_id: str, request: Request) -> dict:
    rule = _repository(request).get_rule(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Unknown rule id: {rule_id}")
    return _rule_response(rule)


@router.post("/reading/compose")
def reading_compose(payload: ComposeReadingRequest, request: Request) -> dict:
    try:
        return compose_reading(
            _repository(request),
            payload.matched_rule_ids,
            allow_draft=payload.allow_draft,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/chart/evaluate")
def chart_evaluate(payload: ChartFactBundleRequest, request: Request) -> dict:
    repository = _repository(request)
    try:
        result = evaluate_chart(
            repository,
            payload.model_dump(),
            include_static_rules=payload.include_static_rules,
            compose=payload.compose,
            allow_draft=payload.allow_draft,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "matched_rule_ids": result.matched_rule_ids,
        "matched_rules": [_rule_response(rule) for rule in result.matched_rules],
        "unsupported_rule_count": len(result.unsupported_rules),
        "unsupported_rule_ids": result.unsupported_rules,
        "warnings": result.warnings,
        "reading": result.reading,
    }


@router.post("/reading/from-chart")
def reading_from_chart(payload: ChartFactBundleRequest, request: Request) -> dict:
    repository = _repository(request)
    try:
        result = evaluate_chart(
            repository,
            payload.model_dump(),
            include_static_rules=payload.include_static_rules,
            compose=True,
            allow_draft=payload.allow_draft,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if result.reading is None:
        raise HTTPException(status_code=404, detail="No supported rules matched the supplied chart facts")
    return result.reading


@router.get("/review/rules", response_class=HTMLResponse)
def review_rules_page(
    request: Request,
    chapter: Optional[int] = Query(default=None),
    rule_status: Optional[str] = Query(default=None),
    classification: Optional[str] = Query(default=None),
    decision: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
) -> str:
    repository = _repository(request)
    review_store = _review_store(request)
    all_rules = repository.list_rules()
    reviews = review_store.all()
    filtered = _filter_review_rules(
        all_rules,
        reviews,
        chapter=chapter,
        rule_status=rule_status,
        classification=classification,
        decision=decision,
        q=q,
    )
    return render_rules_review_page(
        rules=filtered,
        all_rules=all_rules,
        reviews=reviews,
        summary=review_store.summary([rule.id for rule in all_rules]),
        filters={
            "chapter": str(chapter or ""),
            "rule_status": rule_status or "",
            "classification": classification or "",
            "decision": decision or "",
            "q": q or "",
        },
        return_to=str(request.url),
    )


@router.get("/review")
def review_home() -> RedirectResponse:
    return RedirectResponse("/app", status_code=307)


@router.post("/review/rules/{rule_id}/review")
async def save_rule_review(rule_id: str, request: Request) -> RedirectResponse:
    repository = _repository(request)
    if repository.get_rule(rule_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown rule id: {rule_id}")
    form = _urlencoded_form(await request.body())
    try:
        _review_store(request).save(
            rule_id,
            decision=form.get("decision", "unreviewed"),
            comments=form.get("comments", ""),
            improvements=form.get("improvements", ""),
            reviewer=form.get("reviewer", ""),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return_to = form.get("return_to", "/review/rules")
    anchor = "rule-" + "".join(char if char.isalnum() else "-" for char in rule_id)
    return RedirectResponse(f"{return_to}#{anchor}", status_code=303)


@router.get("/review/api/summary")
def review_summary(request: Request) -> dict:
    repository = _repository(request)
    return _review_store(request).summary([rule.id for rule in repository.list_rules()])


@router.get("/review/api/rules")
def review_rules_api(
    request: Request,
    chapter: Optional[int] = Query(default=None),
    rule_status: Optional[str] = Query(default=None),
    classification: Optional[str] = Query(default=None),
    decision: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
) -> dict:
    repository = _repository(request)
    review_store = _review_store(request)
    all_rules = repository.list_rules()
    reviews = review_store.all()
    filtered = _filter_review_rules(
        all_rules,
        reviews,
        chapter=chapter,
        rule_status=rule_status,
        classification=classification,
        decision=decision,
        q=q,
    )
    return {
        "rules": [_review_rule_response(rule, reviews) for rule in filtered],
        "total_rules": len(all_rules),
        "filtered_rules": len(filtered),
        "summary": review_store.summary([rule.id for rule in all_rules]),
        "chapters": [
            _chapter_summary(chapter_rules)
            for chapter_rules in repository.chapters.values()
        ],
        "filters": {
            "chapter": chapter,
            "rule_status": rule_status,
            "classification": classification,
            "decision": decision,
            "q": q,
        },
    }


@router.get("/review/api/rules/{rule_id}")
def review_for_rule(rule_id: str, request: Request) -> dict:
    if _repository(request).get_rule(rule_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown rule id: {rule_id}")
    return asdict(_review_store(request).get(rule_id))


@router.post("/review/api/rules/{rule_id}/review")
def save_rule_review_api(rule_id: str, payload: SaveRuleReviewRequest, request: Request) -> dict:
    repository = _repository(request)
    if repository.get_rule(rule_id) is None:
        raise HTTPException(status_code=404, detail=f"Unknown rule id: {rule_id}")
    try:
        review = _review_store(request).save(
            rule_id,
            decision=payload.decision,
            comments=payload.comments,
            improvements=payload.improvements,
            reviewer=payload.reviewer,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "review": asdict(review),
        "summary": _review_store(request).summary([rule.id for rule in repository.list_rules()]),
    }


def _repository(request: Request) -> RuleRepository:
    return request.app.state.rule_repository


def _review_store(request: Request) -> ReviewStore:
    return request.app.state.review_store


def _filter_review_rules(
    rules: list[Rule],
    reviews: dict,
    *,
    chapter: int | None,
    rule_status: str | None,
    classification: str | None,
    decision: str | None,
    q: str | None,
) -> list[Rule]:
    filtered = rules
    if chapter is not None:
        filtered = [rule for rule in filtered if rule.chapter == chapter]
    if rule_status:
        filtered = [rule for rule in filtered if rule.status == rule_status]
    if classification:
        filtered = [rule for rule in filtered if rule.classification == classification]
    if decision:
        if decision == "unreviewed":
            filtered = [
                rule
                for rule in filtered
                if reviews.get(rule.id) is None or reviews[rule.id].decision == "unreviewed"
            ]
        else:
            filtered = [
                rule
                for rule in filtered
                if reviews.get(rule.id) is not None and reviews[rule.id].decision == decision
            ]
    if q:
        needle = q.casefold()
        filtered = [
            rule
            for rule in filtered
            if needle in " ".join(
                [
                    rule.id,
                    rule.raw_id,
                    rule.title,
                    rule.condition,
                    rule.effect,
                    rule.verse_source,
                    rule.notes,
                ]
            ).casefold()
        ]
    return filtered


def _urlencoded_form(body: bytes) -> dict[str, str]:
    parsed = parse_qs(body.decode("utf-8"), keep_blank_values=True)
    return {
        key: values[-1] if values else ""
        for key, values in parsed.items()
    }


def _scope_response(scope: RuleScope) -> dict:
    return asdict(scope)


def _chapter_summary(chapter: ChapterRules) -> dict:
    return {
        "chapter": chapter.chapter,
        "title": chapter.title,
        "source_file": str(chapter.source_file),
        "rule_count": len(chapter.rules),
        "warnings": chapter.warnings,
    }


def _chapter_response(chapter: ChapterRules) -> dict:
    return {
        **_chapter_summary(chapter),
        "rules": [_rule_response(rule) for rule in chapter.rules],
    }


def _rule_response(rule: Rule) -> dict:
    payload = asdict(rule)
    payload["source_file"] = str(rule.source_file)
    return payload


def _review_rule_response(rule: Rule, reviews: dict) -> dict:
    payload = _rule_response(rule)
    review = reviews.get(rule.id)
    payload["review"] = asdict(review) if review else {
        "rule_id": rule.id,
        "decision": "unreviewed",
        "comments": "",
        "improvements": "",
        "reviewer": "",
        "updated_at": "",
    }
    return payload
