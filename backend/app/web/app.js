const state = {
  allRules: [],
  chapters: [],
  selectedId: null,
  filters: {
    chapter: "",
    decision: "",
    classification: "",
    q: "",
  },
};

const els = {
  chapter: document.querySelector("#chapter-filter"),
  decision: document.querySelector("#decision-filter"),
  classification: document.querySelector("#classification-filter"),
  search: document.querySelector("#search-filter"),
  list: document.querySelector("#rule-list"),
  inspector: document.querySelector("#inspector"),
  resultCount: document.querySelector("#result-count"),
  progressLabel: document.querySelector("#progress-label"),
  progressBar: document.querySelector("#progress-bar"),
  approved: document.querySelector("#metric-approved"),
  needs: document.querySelector("#metric-needs"),
  open: document.querySelector("#metric-open"),
  rowTemplate: document.querySelector("#rule-row-template"),
};

const decisionLabels = {
  unreviewed: "Unreviewed",
  approved: "Approved",
  needs_improvement: "Needs improvement",
};

const classLabels = {
  strength: "Strength",
  tend: "Tend",
  neutral: "Neutral",
  table: "Table",
  unknown: "Unknown",
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function normalize(value) {
  return String(value ?? "").trim().toLowerCase();
}

function reviewFor(rule) {
  return rule.review || {
    rule_id: rule.id,
    decision: "unreviewed",
    comments: "",
    improvements: "",
    reviewer: "",
    updated_at: "",
  };
}

function filteredRules() {
  const query = normalize(state.filters.q);
  return state.allRules.filter((rule) => {
    const review = reviewFor(rule);
    if (state.filters.chapter && String(rule.chapter) !== state.filters.chapter) return false;
    if (state.filters.decision && review.decision !== state.filters.decision) return false;
    if (state.filters.classification && rule.classification !== state.filters.classification) return false;
    if (!query) return true;
    return [
      rule.id,
      rule.raw_id,
      rule.title,
      rule.condition,
      rule.effect,
      rule.verse_source,
      rule.notes,
      review.comments,
      review.improvements,
    ].join(" ").toLowerCase().includes(query);
  });
}

function updateSummary(summary) {
  const total = state.allRules.length || 1;
  const approved = summary.approved || 0;
  const needs = summary.needs_improvement || 0;
  const open = summary.unreviewed || 0;
  const percent = Math.round((approved / total) * 1000) / 10;
  els.approved.textContent = approved;
  els.needs.textContent = needs;
  els.open.textContent = open;
  els.progressLabel.textContent = `${percent}%`;
  els.progressBar.style.width = `${percent}%`;
}

function computeSummary() {
  return state.allRules.reduce((acc, rule) => {
    const decision = reviewFor(rule).decision || "unreviewed";
    acc[decision] = (acc[decision] || 0) + 1;
    return acc;
  }, { approved: 0, needs_improvement: 0, unreviewed: 0 });
}

function populateChapters() {
  const current = els.chapter.value;
  const chapters = state.chapters.length
    ? state.chapters.map((item) => item.chapter)
    : [...new Set(state.allRules.map((rule) => rule.chapter))].sort((a, b) => a - b);
  els.chapter.innerHTML = '<option value="">All chapters</option>' + chapters
    .map((chapter) => `<option value="${chapter}">Chapter ${chapter}</option>`)
    .join("");
  els.chapter.value = current;
}

function renderList() {
  const rules = filteredRules();
  els.resultCount.textContent = `${rules.length} of ${state.allRules.length} rules`;
  els.list.innerHTML = "";

  if (!rules.length) {
    els.list.innerHTML = '<div class="empty-state"><h3>No matching rules</h3><p>Adjust the filters.</p></div>';
    renderEmpty("No rule selected", "Adjust the filters to return rules.");
    return;
  }

  if (!state.selectedId || !rules.some((rule) => rule.id === state.selectedId)) {
    state.selectedId = rules[0].id;
  }

  for (const rule of rules) {
    const review = reviewFor(rule);
    const row = els.rowTemplate.content.firstElementChild.cloneNode(true);
    row.dataset.ruleId = rule.id;
    row.classList.toggle("is-active", rule.id === state.selectedId);
    row.classList.toggle("approved", review.decision === "approved");
    row.classList.toggle("needs_improvement", review.decision === "needs_improvement");
    row.querySelector(".row-id").textContent = rule.id;
    row.querySelector(".row-decision").textContent = decisionLabels[review.decision] || review.decision;
    row.querySelector(".row-title").textContent = rule.title;
    row.querySelector(".row-meta").textContent = `Ch ${rule.chapter} · ${classLabels[rule.classification] || rule.classification} · ${rule.status}`;
    row.addEventListener("click", () => {
      state.selectedId = rule.id;
      render();
    });
    els.list.appendChild(row);
  }
}

function renderEmpty(title, body) {
  els.inspector.innerHTML = `
    <div class="empty-state">
      <h3>${escapeHtml(title)}</h3>
      <p>${escapeHtml(body)}</p>
    </div>
  `;
}

function renderInspector() {
  const rule = state.allRules.find((item) => item.id === state.selectedId);
  if (!rule) {
    renderEmpty("No rule selected", "Select a rule from the list.");
    return;
  }
  const review = reviewFor(rule);
  const citations = (rule.citations || []).map((citation) => citation.raw).filter(Boolean).join(", ") || "No citation parsed";
  const warnings = (rule.warnings || []).length
    ? `<section class="warnings"><strong>Warnings</strong><ul>${rule.warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")}</ul></section>`
    : "";

  els.inspector.innerHTML = `
    <header class="inspector-head">
      <div class="inspector-title">
        <div>
          <p class="eyebrow">${escapeHtml(rule.id)}</p>
          <h3>${escapeHtml(rule.title)}</h3>
        </div>
        <div class="badge-row">
          <span class="badge">Ch ${escapeHtml(rule.chapter)}</span>
          <span class="badge class-${escapeHtml(rule.classification)}">${escapeHtml(classLabels[rule.classification] || rule.classification)}</span>
          <span class="badge">${escapeHtml(rule.status)}</span>
          <span class="badge decision-${escapeHtml(review.decision)}">${escapeHtml(decisionLabels[review.decision] || review.decision)}</span>
        </div>
      </div>
      <p class="row-meta">${escapeHtml(citations)}</p>
    </header>
    <div class="inspector-body">
      <section class="field-block">
        <span class="field-title">Condition</span>
        <p class="field-text">${escapeHtml(rule.condition)}</p>
      </section>
      <section class="field-block">
        <span class="field-title">Effect</span>
        <p class="field-text">${escapeHtml(rule.effect)}</p>
      </section>
      <section class="field-block">
        <span class="field-title">Verse Source</span>
        <p class="field-text">${escapeHtml(rule.verse_source)}</p>
      </section>
      <section class="field-block">
        <span class="field-title">Notes</span>
        <p class="field-text">${escapeHtml(rule.notes || "No notes")}</p>
      </section>
      ${warnings}
      <form class="review-panel" id="review-form">
        <div class="decision-control" role="radiogroup" aria-label="Decision">
          ${decisionOption("unreviewed", review.decision)}
          ${decisionOption("approved", review.decision)}
          ${decisionOption("needs_improvement", review.decision)}
        </div>
        <label class="reviewer-line">
          <span>Reviewer</span>
          <input name="reviewer" value="${escapeHtml(review.reviewer)}" placeholder="Your name">
        </label>
        <div class="review-grid">
          <label>
            <span>Comments</span>
            <textarea name="comments" placeholder="Source, tone, citation, condition">${escapeHtml(review.comments)}</textarea>
          </label>
          <label>
            <span>Improvements</span>
            <textarea name="improvements" placeholder="Correction or rewrite">${escapeHtml(review.improvements)}</textarea>
          </label>
        </div>
        <div class="save-row">
          <button class="primary-button" type="submit">Save Review</button>
          <span class="save-state" id="save-state">${review.updated_at ? `Saved ${escapeHtml(review.updated_at)}` : "Not saved yet"}</span>
        </div>
      </form>
    </div>
  `;

  document.querySelector("#review-form").addEventListener("submit", saveSelectedReview);
}

function decisionOption(value, current) {
  const checked = value === current ? "checked" : "";
  return `
    <label>
      <input type="radio" name="decision" value="${escapeHtml(value)}" ${checked}>
      <span>${escapeHtml(decisionLabels[value])}</span>
    </label>
  `;
}

async function saveSelectedReview(event) {
  event.preventDefault();
  const rule = state.allRules.find((item) => item.id === state.selectedId);
  if (!rule) return;
  const form = event.currentTarget;
  const saveState = document.querySelector("#save-state");
  const payload = {
    decision: form.querySelector('input[name="decision"]:checked')?.value || "unreviewed",
    reviewer: form.querySelector('input[name="reviewer"]').value,
    comments: form.querySelector('textarea[name="comments"]').value,
    improvements: form.querySelector('textarea[name="improvements"]').value,
  };

  saveState.textContent = "Saving";
  const response = await fetch(`/review/api/rules/${encodeURIComponent(rule.id)}/review`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    saveState.textContent = "Save failed";
    return;
  }
  const data = await response.json();
  rule.review = data.review;
  updateSummary(data.summary);
  render();
}

function render() {
  renderList();
  renderInspector();
  updateSummary(computeSummary());
}

function bindFilters() {
  els.chapter.addEventListener("change", () => {
    state.filters.chapter = els.chapter.value;
    state.selectedId = null;
    render();
  });
  els.decision.addEventListener("change", () => {
    state.filters.decision = els.decision.value;
    state.selectedId = null;
    render();
  });
  els.classification.addEventListener("change", () => {
    state.filters.classification = els.classification.value;
    state.selectedId = null;
    render();
  });
  els.search.addEventListener("input", () => {
    state.filters.q = els.search.value;
    state.selectedId = null;
    render();
  });
}

async function boot() {
  bindFilters();
  const response = await fetch("/review/api/rules");
  if (!response.ok) {
    renderEmpty("Could not load rules", "The backend did not return the rule set.");
    return;
  }
  const data = await response.json();
  state.allRules = data.rules || [];
  state.chapters = data.chapters || [];
  populateChapters();
  updateSummary(data.summary || computeSummary());
  render();
}

boot();
