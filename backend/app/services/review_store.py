from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


REVIEW_DECISIONS = {"unreviewed", "approved", "needs_improvement"}


@dataclass(frozen=True)
class RuleReview:
    rule_id: str
    decision: str = "unreviewed"
    comments: str = ""
    improvements: str = ""
    reviewer: str = ""
    updated_at: str = ""


class ReviewStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def all(self) -> dict[str, RuleReview]:
        with self._lock:
            return self._read()

    def get(self, rule_id: str) -> RuleReview:
        return self.all().get(rule_id, RuleReview(rule_id=rule_id))

    def save(
        self,
        rule_id: str,
        *,
        decision: str,
        comments: str,
        improvements: str,
        reviewer: str,
    ) -> RuleReview:
        if decision not in REVIEW_DECISIONS:
            raise ValueError(f"Unsupported review decision: {decision}")

        review = RuleReview(
            rule_id=rule_id,
            decision=decision,
            comments=comments.strip(),
            improvements=improvements.strip(),
            reviewer=reviewer.strip(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            reviews = self._read()
            reviews[rule_id] = review
            self._write(reviews)
        return review

    def summary(self, rule_ids: list[str]) -> dict[str, int]:
        reviews = self.all()
        counts = {decision: 0 for decision in sorted(REVIEW_DECISIONS)}
        for rule_id in rule_ids:
            decision = reviews.get(rule_id, RuleReview(rule_id=rule_id)).decision
            counts[decision] = counts.get(decision, 0) + 1
        return counts

    def _read(self) -> dict[str, RuleReview]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return {
            rule_id: RuleReview(
                rule_id=rule_id,
                decision=str(raw.get("decision", "unreviewed")),
                comments=str(raw.get("comments", "")),
                improvements=str(raw.get("improvements", "")),
                reviewer=str(raw.get("reviewer", "")),
                updated_at=str(raw.get("updated_at", "")),
            )
            for rule_id, raw in data.items()
            if isinstance(raw, dict)
        }

    def _write(self, reviews: dict[str, RuleReview]) -> None:
        payload: dict[str, Any] = {
            rule_id: asdict(review)
            for rule_id, review in sorted(reviews.items())
        }
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
