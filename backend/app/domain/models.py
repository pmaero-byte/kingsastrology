from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


RuleStatus = Literal["draft", "verified", "blocked_ocr", "unknown"]
RuleClassification = Literal["strength", "tend", "neutral", "table", "unknown"]


@dataclass(frozen=True)
class Citation:
    raw: str
    chapter: int | None = None
    verse: str | None = None


@dataclass(frozen=True)
class Rule:
    id: str
    raw_id: str
    title: str
    chapter: int
    source_file: Path
    classification: RuleClassification
    status: RuleStatus
    citations: list[Citation]
    condition: str
    effect: str
    verse_source: str
    notes: str
    warnings: list[str] = field(default_factory=list)

    @property
    def is_verified(self) -> bool:
        return self.status == "verified"


@dataclass(frozen=True)
class ChapterRules:
    chapter: int
    title: str
    source_file: Path
    rules: list[Rule]
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RuleScope:
    min_chapter: int
    max_chapter: int
    loaded_chapters: list[int]
    missing_chapters: list[int]
    total_rules: int
    verified_rules: int
    draft_rules: int
    blocked_rules: int
    warnings: list[str]
