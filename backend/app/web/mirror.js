/* The Mirror — birth data -> computed chart -> deterministic reading.
   All numbers come from /api/v1 (chart/compute + reading/mirror). No AI. */
"use strict";

const $ = (id) => document.getElementById(id);

function isoWithOffset(localValue) {
  // datetime-local -> ISO with the browser's local offset.
  const d = new Date(localValue);
  const off = -d.getTimezoneOffset();
  const sign = off >= 0 ? "+" : "-";
  const hh = String(Math.floor(Math.abs(off) / 60)).padStart(2, "0");
  const mm = String(Math.abs(off) % 60).padStart(2, "0");
  const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000)
    .toISOString().slice(0, 19);
  return local + sign + hh + ":" + mm;
}

function fmtDate(iso) {
  return new Date(iso).toISOString().slice(0, 10);
}

function renderChart(chart) {
  const lagna = chart.lagna;
  const dasa = chart.dasa_timeline.periods[0];
  const av = chart.ashtakavarga.sarvashtakavarga;
  const grahas = chart.grahas
    .filter((g) => g.name !== "Rahu" && g.name !== "Ketu")
    .map(
      (g) =>
        `<div class="graha"><div class="nm">${g.name}</div>` +
        `<div class="pos">${g.sign} ${g.sign_degree.toFixed(1)}° · house ${g.house ?? "—"}</div>` +
        `<div class="pos">${g.nakshatra} ${g.nakshatra_pada} · ${g.dignity.replace("_", " ")}</div>` +
        `<div class="pos">D9 ${g.navamsa_sign}${g.retrograde ? " · retrograde" : ""}</div></div>`
    )
    .join("");

  return `
    <h2>Your Chart at a Glance</h2>
    <div class="chart-grid">
      <div class="graha"><div class="nm">Lagna</div><div class="pos">${lagna.lagna_sign}</div>
        <div class="pos">ayanamsa ${lagna.ayanamsa_value.toFixed(4)}°</div></div>
      ${grahas}
    </div>
    <h2>The Season You Are In</h2>
    <p>Current period: <strong>${dasa.lord}</strong> (Vimshottari), from ${fmtDate(dasa.start)} to ${fmtDate(dasa.end)}.
    Next: ${chart.dasa_timeline.periods[1].lord} from ${fmtDate(chart.dasa_timeline.periods[1].start)}.</p>
    <h2>Ashtakavarga</h2>
    <p>Sarvashtakavarga total: <strong>${av.total_bindus}</strong> bindus (Ch 9, v 1–7).
    Per-sign bindus: ${av.bindu_by_sign.join(", ")}.</p>`;
}

function renderRules(rules, versePanel) {
  if (!rules.length) {
    return `<p class="muted">No supported rules matched this chart (the evaluator covers a subset of conditions).</p>`;
  }
  return rules
    .map(
      (rule) =>
        `<div class="rule" data-ch="${rule.chapter}" data-v="${(rule.citations[0]?.verse || "").trim().split(" ")[0]}">` +
        `<span class="rid">${rule.id}</span> — ${rule.title} · ${rule.classification} · ` +
        `${rule.effect.slice(0, 160)}${rule.effect.length > 160 ? "…" : ""}` +
        `<span class="muted"> · ${rule.citations.map((c) => c.raw).join("; ")}</span></div>`
    )
    .join("");
}

async function openVerse(chapter, verse) {
  try {
    const r = await fetch(`/api/v1/verse/${chapter}/${verse || 1}`);
    if (!r.ok) return;
    const body = await r.json();
    const panel = $("verse-panel");
    const text = body.verses.map((v) => v.translation_text).join("\n\n");
    panel.innerHTML =
      `<strong>Brihat Jataka ${chapter}.${verse}</strong>\n\n${text}` +
      (body.verses[0]?.notes ? `\n\n— Notes: ${body.verses[0].notes}` : "");
    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch {
    /* verse panel is an enhancement; silence failures */
  }
}

$("mirror-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const result = $("result");
  result.innerHTML = `<p class="muted">Computing the sky…</p>`;
  const payload = {
    datetime_iso: isoWithOffset($("datetime").value),
    place: $("place").value,
    lat: parseFloat($("lat").value),
    lon: parseFloat($("lon").value),
    elev_m: 0,
  };
  try {
    const resp = await fetch("/api/v1/reading/mirror", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      const err = await resp.json();
      result.innerHTML = `<p>Could not compute the chart: ${err.detail || resp.status}</p>`;
      return;
    }
    const body = await resp.json();
    const chart = body.chart;
    let html = renderChart(chart);
    html += `<h2>What the rules say (draft preview)</h2>`;
    if (body.reading) {
      html += body.reading.sections
        .map(
          (s) =>
            `<h3>${s.title}</h3>` +
            s.claims
              .map((c) => `<div class="rule" data-ch="${c.chapter}" data-v="${(c.citations[0]?.verse || "").trim().split(" ")[0]}">${c.effect}</div>`)
              .join("")
        )
        .join("");
    } else {
      html += `<div class="withheld"><strong>Reading withheld — the M3 scholar-review gate.</strong><br>` +
        `<span class="muted">${body.reading_withheld}</span></div>`;
      html += `<p class="muted">${body.matched_rule_count} rules matched your chart deterministically; ` +
        `${body.unsupported_rule_count} rules could not be tested (conditions outside the current evaluator).</p>`;
      html += `<div id="rule-list"><p class="muted">Loading matched rules…</p></div>`;
    }
    result.innerHTML = html + `<div id="verse-panel" class="verse-panel muted">Tap a rule to open its verse.</div>`;

    // Fetch full rule records for the matched ids (they were withheld).
    if (!body.reading) {
      const list = $("rule-list");
      const rows = await Promise.all(
        body.matched_rule_ids.map((id) =>
          fetch(`/api/v1/rules/by-id/${encodeURIComponent(id)}`).then((r) => (r.ok ? r.json() : null))
        )
      );
      list.innerHTML = renderRules(rows.filter(Boolean), $("verse-panel"));
    }
  } catch (err) {
    result.innerHTML = `<p>Something failed: ${err.message}</p>`;
  }
});

document.addEventListener("click", (ev) => {
  const rule = ev.target.closest(".rule");
  if (rule) openVerse(rule.dataset.ch, rule.dataset.v);
});
