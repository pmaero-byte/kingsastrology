from __future__ import annotations

import re
from pathlib import Path

from app.domain.models import ChapterRules, Citation, Rule, RuleClassification, RuleScope, RuleStatus


MIN_SUPPORTED_CHAPTER = 8
MAX_SUPPORTED_CHAPTER = 20

_CHAPTER_FILE_RE = re.compile(r"^ch(?P<chapter>\d{2})_.*\.md$")
_HEADER_CHAPTER_RE = re.compile(r"^#\s+Chapter\s+(?P<chapter>\d+)\b", re.IGNORECASE)
_RULE_HEADING_RE = re.compile(r"^##\s+(?P<id>R-[^—\n]+?)\s+—\s+(?P<title>.+?)\s*$", re.MULTILINE)
_FIELD_RE = re.compile(r"^-\s+\*\*(?P<name>[^*]+):\*\*\s*(?P<value>.*)$")
_CITATION_RE = re.compile(r"Ch\s+(?P<chapter>\d+)\s*,\s*v\s*(?P<verse>[^;)]+)", re.IGNORECASE)


class RuleRepository:
    """Loads draft rule markdown, restricted to the book chapters this backend supports."""

    def __init__(
        self,
        rules_dir: Path,
        min_chapter: int = MIN_SUPPORTED_CHAPTER,
        max_chapter: int = MAX_SUPPORTED_CHAPTER,
    ) -> None:
        self.rules_dir = rules_dir
        self.min_chapter = min_chapter
        self.max_chapter = max_chapter
        self._chapters = self._load_chapters()
        self._rules_by_id = {
            rule.id: rule
            for chapter in self._chapters.values()
            for rule in chapter.rules
        }

    @property
    def chapters(self) -> dict[int, ChapterRules]:
        return self._chapters

    def scope(self) -> RuleScope:
        loaded = sorted(self._chapters)
        expected = list(range(self.min_chapter, self.max_chapter + 1))
        rules = [rule for chapter in self._chapters.values() for rule in chapter.rules]
        warnings = [
            warning
            for chapter in self._chapters.values()
            for warning in chapter.warnings
        ]
        warnings.extend(
            warning
            for rule in rules
            for warning in rule.warnings
        )
        return RuleScope(
            min_chapter=self.min_chapter,
            max_chapter=self.max_chapter,
            loaded_chapters=loaded,
            missing_chapters=[chapter for chapter in expected if chapter not in loaded],
            total_rules=len(rules),
            verified_rules=sum(rule.status == "verified" for rule in rules),
            draft_rules=sum(rule.status == "draft" for rule in rules),
            blocked_rules=sum(rule.status == "blocked_ocr" for rule in rules),
            warnings=warnings,
        )

    def list_rules(
        self,
        chapter: int | None = None,
        status: str | None = None,
        classification: str | None = None,
    ) -> list[Rule]:
        rules = [
            rule
            for chapter_rules in self._chapters.values()
            for rule in chapter_rules.rules
        ]
        if chapter is not None:
            rules = [rule for rule in rules if rule.chapter == chapter]
        if status is not None:
            rules = [rule for rule in rules if rule.status == status]
        if classification is not None:
            rules = [rule for rule in rules if rule.classification == classification]
        return sorted(rules, key=lambda rule: (rule.chapter, _rule_sort_key(rule.id)))

    def get_chapter(self, chapter: int) -> ChapterRules | None:
        return self._chapters.get(chapter)

    def get_rule(self, rule_id: str) -> Rule | None:
        return self._rules_by_id.get(rule_id)

    def require_rule(self, rule_id: str) -> Rule:
        rule = self.get_rule(rule_id)
        if rule is None:
            raise KeyError(f"Unknown rule id: {rule_id}")
        return rule

    def _load_chapters(self) -> dict[int, ChapterRules]:
        if not self.rules_dir.exists():
            raise FileNotFoundError(f"Rules directory does not exist: {self.rules_dir}")

        chapters: dict[int, ChapterRules] = {}
        for path in sorted(self.rules_dir.glob("ch*.md")):
            chapter = _chapter_from_file(path)
            if chapter is None or not self.min_chapter <= chapter <= self.max_chapter:
                continue
            chapters[chapter] = _parse_chapter_file(path, chapter)
        return chapters


def _chapter_from_file(path: Path) -> int | None:
    match = _CHAPTER_FILE_RE.match(path.name)
    if not match:
        return None
    return int(match.group("chapter"))


def _canonical_rule_id(raw_id: str, effective_chapter: int) -> str:
    legacy_prefix = "R-4"
    if effective_chapter != 4 and raw_id.startswith(legacy_prefix):
        return f"R-{effective_chapter}{raw_id[len(legacy_prefix):]}"
    return raw_id


def _parse_chapter_file(path: Path, effective_chapter: int) -> ChapterRules:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip() if lines else path.stem
    warnings: list[str] = []

    header_match = _HEADER_CHAPTER_RE.match(lines[0]) if lines else None
    if header_match:
        header_chapter = int(header_match.group("chapter"))
        if header_chapter != effective_chapter:
            warnings.append(
                f"{path.name}: header says Chapter {header_chapter}; "
                f"backend scope treats filename chapter {effective_chapter} as canonical."
            )

    matches = list(_RULE_HEADING_RE.finditer(text))
    rules: list[Rule] = []
    for index, match in enumerate(matches):
        raw_id = match.group("id").strip()
        canonical_id = _canonical_rule_id(raw_id, effective_chapter)
        block_start = match.end()
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        fields = _parse_fields(text[block_start:block_end])
        rule_warnings = _rule_warnings(path, effective_chapter, fields)
        if canonical_id != raw_id:
            rule_warnings.append(
                f"{path.name}: normalized legacy rule id {raw_id} to canonical id {canonical_id}."
            )
        rules.append(
            Rule(
                id=canonical_id,
                raw_id=raw_id,
                title=match.group("title").strip(),
                chapter=effective_chapter,
                source_file=path,
                classification=_classification(fields.get("classification", "")),
                status=_status(fields.get("status", "")),
                citations=_citations(fields.get("cites", "")),
                condition=fields.get("condition", ""),
                effect=fields.get("effect (one-way, dignity-closing)", ""),
                verse_source=fields.get("verse (source)", ""),
                notes=fields.get("notes", "") or fields.get("notes (full)", ""),
                warnings=rule_warnings,
            )
        )

    return ChapterRules(
        chapter=effective_chapter,
        title=title,
        source_file=path,
        rules=rules,
        warnings=warnings,
    )


def _parse_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_name, current_lines
        if current_name is not None:
            fields[current_name] = "\n".join(current_lines).strip()
        current_name = None
        current_lines = []

    for raw_line in block.splitlines():
        match = _FIELD_RE.match(raw_line)
        if match:
            flush()
            current_name = match.group("name").strip().lower()
            current_lines = [match.group("value").strip()]
            continue
        if current_name is not None:
            current_lines.append(raw_line.rstrip())
    flush()
    return fields


def _citations(raw: str) -> list[Citation]:
    matches = list(_CITATION_RE.finditer(raw))
    if not matches:
        return [Citation(raw=raw.strip())] if raw.strip() else []
    return [
        Citation(
            raw=match.group(0).strip(),
            chapter=int(match.group("chapter")),
            verse=match.group("verse").strip(),
        )
        for match in matches
    ]


def _classification(raw: str) -> RuleClassification:
    value = raw.strip().lower()
    if value in {"strength", "tend", "neutral", "table"}:
        return value  # type: ignore[return-value]
    return "unknown"


def _status(raw: str) -> RuleStatus:
    value = raw.strip().lower()
    if value in {"draft", "verified", "blocked_ocr"}:
        return value  # type: ignore[return-value]
    return "unknown"


def _rule_warnings(path: Path, effective_chapter: int, fields: dict[str, str]) -> list[str]:
    warnings: list[str] = []
    for citation in _citations(fields.get("cites", "")):
        if citation.chapter is not None and citation.chapter != effective_chapter:
            warnings.append(
                f"{path.name}: citation {citation.raw} does not match canonical "
                f"backend chapter {effective_chapter}."
            )
    if not fields.get("condition"):
        warnings.append(f"{path.name}: rule is missing a machine-testable condition.")
    if not fields.get("effect (one-way, dignity-closing)"):
        warnings.append(f"{path.name}: rule is missing deterministic effect text.")
    return warnings


def _rule_sort_key(rule_id: str) -> tuple:
    pieces = re.split(r"([0-9]+)", rule_id)
    return tuple(int(piece) if piece.isdigit() else piece.lower() for piece in pieces)
