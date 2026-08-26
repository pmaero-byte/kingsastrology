from __future__ import annotations

from html import escape
from urllib.parse import urlencode

from app.domain.models import Rule
from app.services.review_store import REVIEW_DECISIONS, RuleReview


DECISION_LABELS = {
    "unreviewed": "Unreviewed",
    "approved": "Approved",
    "needs_improvement": "Needs Improvement",
}


def render_rules_review_page(
    *,
    rules: list[Rule],
    all_rules: list[Rule],
    reviews: dict[str, RuleReview],
    summary: dict[str, int],
    filters: dict[str, str],
    return_to: str,
) -> str:
    title = "Kingsastrology Rule Review"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>{_css()}</style>
</head>
<body>
  <header class="topbar">
    <div>
      <h1>{title}</h1>
      <p>Chapters 8-20 · {len(all_rules)} rules · no runtime AI</p>
    </div>
    <a class="api-link" href="/rules/scope">Scope JSON</a>
  </header>
  <main>
    {_summary(summary, len(all_rules))}
    {_filters(filters)}
    <section class="rule-count" aria-live="polite">
      Showing <strong>{len(rules)}</strong> of <strong>{len(all_rules)}</strong> rules
    </section>
    <section class="rules">
      {''.join(_rule_card(rule, reviews.get(rule.id, RuleReview(rule_id=rule.id)), return_to) for rule in rules)}
    </section>
  </main>
</body>
</html>"""


def _summary(summary: dict[str, int], total: int) -> str:
    approved = summary.get("approved", 0)
    needs = summary.get("needs_improvement", 0)
    unreviewed = summary.get("unreviewed", 0)
    progress = round((approved / total) * 100, 1) if total else 0
    return f"""
    <section class="summary" aria-label="Review summary">
      <div><span>{approved}</span><label>Approved</label></div>
      <div><span>{needs}</span><label>Needs Improvement</label></div>
      <div><span>{unreviewed}</span><label>Unreviewed</label></div>
      <div><span>{progress}%</span><label>Approved Progress</label></div>
    </section>
    """


def _filters(filters: dict[str, str]) -> str:
    return f"""
    <form class="filters" method="get" action="/review/rules">
      <label>Chapter
        <select name="chapter">
          {_option("", "All", filters.get("chapter", ""))}
          {''.join(_option(str(chapter), str(chapter), filters.get("chapter", "")) for chapter in range(8, 21))}
        </select>
      </label>
      <label>Rule Status
        <select name="rule_status">
          {_option("", "All", filters.get("rule_status", ""))}
          {_option("draft", "Draft", filters.get("rule_status", ""))}
          {_option("verified", "Verified", filters.get("rule_status", ""))}
          {_option("blocked_ocr", "Blocked OCR", filters.get("rule_status", ""))}
        </select>
      </label>
      <label>Classification
        <select name="classification">
          {_option("", "All", filters.get("classification", ""))}
          {_option("strength", "Strength", filters.get("classification", ""))}
          {_option("tend", "Tend", filters.get("classification", ""))}
          {_option("neutral", "Neutral", filters.get("classification", ""))}
          {_option("table", "Table", filters.get("classification", ""))}
        </select>
      </label>
      <label>Review
        <select name="decision">
          {_option("", "All", filters.get("decision", ""))}
          {''.join(_option(value, DECISION_LABELS[value], filters.get("decision", "")) for value in sorted(REVIEW_DECISIONS))}
        </select>
      </label>
      <label class="search">Search
        <input name="q" value="{escape(filters.get("q", ""))}" placeholder="rule id, title, effect, verse">
      </label>
      <button type="submit">Apply</button>
      <a class="secondary" href="/review/rules">Reset</a>
    </form>
    """


def _rule_card(rule: Rule, review: RuleReview, return_to: str) -> str:
    anchor = _anchor(rule.id)
    citations = ", ".join(escape(citation.raw) for citation in rule.citations) or "No citation parsed"
    warnings = "".join(f"<li>{escape(warning)}</li>" for warning in rule.warnings)
    warning_block = f"<details class=\"warnings\"><summary>Warnings ({len(rule.warnings)})</summary><ul>{warnings}</ul></details>" if rule.warnings else ""
    updated = f"<span>Updated {escape(review.updated_at)}</span>" if review.updated_at else "<span>Not saved yet</span>"
    return f"""
    <article class="rule-card decision-{escape(review.decision)}" id="{anchor}">
      <div class="rule-head">
        <div>
          <h2>{escape(rule.id)} · {escape(rule.title)}</h2>
          <p>{escape(citations)}</p>
        </div>
        <div class="badges">
          <span>Ch {rule.chapter}</span>
          <span>{escape(rule.classification)}</span>
          <span>{escape(rule.status)}</span>
          <span>{escape(DECISION_LABELS.get(review.decision, review.decision))}</span>
        </div>
      </div>
      <div class="rule-grid">
        <section>
          <h3>Condition</h3>
          <p>{_multiline(rule.condition)}</p>
        </section>
        <section>
          <h3>Effect</h3>
          <p>{_multiline(rule.effect)}</p>
        </section>
      </div>
      <details>
        <summary>Verse Source</summary>
        <p>{_multiline(rule.verse_source)}</p>
      </details>
      <details>
        <summary>Notes</summary>
        <p>{_multiline(rule.notes or "No notes")}</p>
      </details>
      {warning_block}
      <form class="review-form" method="post" action="/review/rules/{escape(rule.id)}/review">
        <input type="hidden" name="return_to" value="{escape(return_to)}">
        <label>Decision
          <select name="decision">
            {''.join(_option(value, DECISION_LABELS[value], review.decision) for value in sorted(REVIEW_DECISIONS))}
          </select>
        </label>
        <label>Reviewer
          <input name="reviewer" value="{escape(review.reviewer)}" placeholder="Your name">
        </label>
        <label class="wide">Comments
          <textarea name="comments" rows="4" placeholder="Your comment on source fidelity, tone, condition, or citation">{escape(review.comments)}</textarea>
        </label>
        <label class="wide">Improvements
          <textarea name="improvements" rows="4" placeholder="Rewrite, correction, or approval note">{escape(review.improvements)}</textarea>
        </label>
        <div class="form-actions">
          <button type="submit">Save Review</button>
          {updated}
        </div>
      </form>
    </article>
    """


def _option(value: str, label: str, selected: str) -> str:
    marker = " selected" if value == selected else ""
    return f"<option value=\"{escape(value)}\"{marker}>{escape(label)}</option>"


def _multiline(value: str) -> str:
    return "<br>".join(escape(value or "").splitlines())


def _anchor(rule_id: str) -> str:
    return "rule-" + "".join(char if char.isalnum() else "-" for char in rule_id)


def filter_query(**kwargs: str) -> str:
    return urlencode({key: value for key, value in kwargs.items() if value})


def _css() -> str:
    return """
    :root {
      color-scheme: light;
      --ink: #1e2329;
      --muted: #68717d;
      --line: #d9dee5;
      --paper: #fbfcfd;
      --panel: #ffffff;
      --accent: #0f766e;
      --accent-dark: #115e59;
      --warn: #9a3412;
      --ok: #166534;
      --soft: #eef6f5;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--paper);
      color: var(--ink);
      line-height: 1.5;
    }
    .topbar {
      position: sticky;
      top: 0;
      z-index: 2;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 28px;
      background: rgba(255,255,255,.96);
      border-bottom: 1px solid var(--line);
    }
    h1 { margin: 0; font-size: 22px; letter-spacing: 0; }
    h2 { margin: 0 0 6px; font-size: 18px; letter-spacing: 0; }
    h3 { margin: 0 0 8px; font-size: 13px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
    p { margin: 0; }
    .topbar p { color: var(--muted); }
    main { max-width: 1180px; margin: 0 auto; padding: 24px; }
    .api-link, .secondary {
      color: var(--accent-dark);
      text-decoration: none;
      font-weight: 650;
    }
    .summary {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }
    .summary div {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }
    .summary span { display: block; font-size: 24px; font-weight: 750; }
    .summary label { color: var(--muted); }
    .filters {
      display: grid;
      grid-template-columns: repeat(4, minmax(130px, 1fr));
      gap: 12px;
      align-items: end;
      padding: 16px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    label { display: grid; gap: 6px; font-size: 13px; font-weight: 650; color: var(--muted); }
    .search { grid-column: span 2; }
    input, select, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 10px;
      font: inherit;
      color: var(--ink);
      background: #fff;
    }
    textarea { resize: vertical; min-height: 92px; }
    button {
      border: 0;
      border-radius: 6px;
      padding: 10px 14px;
      background: var(--accent);
      color: #fff;
      font-weight: 750;
      cursor: pointer;
    }
    button:hover { background: var(--accent-dark); }
    .rule-count { margin: 18px 0; color: var(--muted); }
    .rules { display: grid; gap: 18px; }
    .rule-card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 5px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      scroll-margin-top: 96px;
    }
    .decision-approved { border-left-color: var(--ok); }
    .decision-needs_improvement { border-left-color: var(--warn); }
    .rule-head {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
    }
    .rule-head p { color: var(--muted); font-size: 13px; }
    .badges { display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-end; align-content: flex-start; }
    .badges span {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 8px;
      font-size: 12px;
      color: var(--muted);
      background: var(--soft);
      white-space: nowrap;
    }
    .rule-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-bottom: 12px;
    }
    .rule-grid section, details {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fff;
      overflow-wrap: anywhere;
    }
    details { margin-top: 10px; }
    summary { cursor: pointer; font-weight: 700; color: var(--accent-dark); }
    .warnings { border-color: #fed7aa; background: #fff7ed; }
    .warnings li { margin-bottom: 6px; }
    .review-form {
      display: grid;
      grid-template-columns: minmax(150px, 220px) minmax(180px, 260px) 1fr 1fr;
      gap: 12px;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid var(--line);
    }
    .wide { grid-row: span 2; }
    .form-actions {
      grid-column: 1 / -1;
      display: flex;
      align-items: center;
      gap: 12px;
      color: var(--muted);
    }
    @media (max-width: 900px) {
      .summary, .filters, .rule-grid, .review-form { grid-template-columns: 1fr; }
      .search, .wide, .form-actions { grid-column: auto; grid-row: auto; }
      .rule-head { display: grid; }
      .badges { justify-content: flex-start; }
      main { padding: 16px; }
      .topbar { position: static; padding: 16px; }
    }
    """
