/* Today at the Court — data wiring. All numbers come from /api/v1. */
"use strict";

const $ = (id) => document.getElementById(id);
const state = { now: null, day: null, week: null, month: null, year: null, obs: null };

const fmtTime = (ms) => new Date(ms).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
const fmtDay = (ms) => new Date(ms).toLocaleDateString([], { weekday: "short", day: "numeric", month: "short" });
const fmtDateTime = (ms) => new Date(ms).toLocaleString([], { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });

function localMinutes(ms) {
  const d = new Date(ms);
  return d.getHours() * 60 + d.getMinutes() + d.getSeconds() / 60;
}

/* ------------------------------------------------------------------ hero */

function tickHero() {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  $("hero-time").textContent = `${hh}:${mm}:${ss}`;
}

function renderHero() {
  const n = state.now;
  if (!n) return;
  $("hero-date").textContent = new Date(n.timestamp_ms_utc).toLocaleDateString([], {
    weekday: "long", year: "numeric", month: "long", day: "numeric",
  });
  $("c-nak").textContent = n.nakshatra.name;
  $("c-tithi").textContent = n.tithi.name.replace(" (waxing)", "").replace(" (waning)", "");
  $("c-hora").textContent = n.hora.current ? n.hora.current.lord : "—";
  $("c-yoga").textContent = n.yoga.name;
  $("c-karana").textContent = n.karana.name;
  $("c-signs").textContent = `${n.sun_sign.sanskrit} · ${n.moon_sign.sanskrit}`;
  $("c-paksha").textContent = n.tithi.paksha + " paksha";

  // Countdown estimates from the measured progress through each arc.
  const tithiLeft = (1 - n.tithi.progress) * 12 / 0.5083;         // hours
  const nakLeft = (1 - n.nakshatra.progress) * (40 / 3) / 0.549;  // hours
  $("c-tithi-next").innerHTML = `next: <span class="count">${humanHours(tithiLeft)}</span>`;
  $("c-nak-next").innerHTML = `pada ${n.nakshatra.pada} · next in <span class="count">${humanHours(nakLeft)}</span>`;
  if (n.hora.current) {
    const left = Math.max(0, n.hora.current.ends - Date.now()) / 60000;
    $("c-hora-next").innerHTML = `ends in <span class="count">${left < 1 ? "under a minute" : Math.round(left) + " min"}</span>`;
  }

  const cal = n.calendars;
  if (cal) {
    $("cal-ribbon").innerHTML = [
      ["Gregorian", `${cal.gregorian.day} ${monthName(cal.gregorian.month)} ${cal.gregorian.year}`],
      ["Hijrī", `${cal.hijri.day} ${cal.hijri.month_name} ${cal.hijri.year}`],
      ["Jalālī", `${cal.jalali.day} ${cal.jalali.month_name} ${cal.jalali.year}`],
      ["Vikram", `Saṃvat ${cal.vikram_samvat.year}`],
      ["Śaka", `${cal.saka.day} ${cal.saka.month_name} ${cal.saka.year}`],
      ["Kali", `ahargaṇa ${Math.floor(cal.kali.ahargana_days)}`],
    ].map(([k, v]) => `<span>${k} <b>${v}</b></span>`).join("");
  }
}

function monthName(m) {
  return new Date(2026, m - 1, 1).toLocaleString([], { month: "long" });
}
function humanHours(h) {
  if (!Number.isFinite(h) || h < 0) return "—";
  if (h < 1) return `${Math.round(h * 60)} min`;
  return `${Math.floor(h)}h ${Math.round((h % 1) * 60)}m`;
}

/* ------------------------------------------------------------------- day */

function renderDay() {
  const d = state.day;
  if (!d) return;
  const n = d.now;
  const rs = n.rise_set;
  $("day-lede").textContent =
    `${n.vara.name} — ruled by ${n.vara.lord}. The Moon walks ${n.moon_sign.sanskrit} in ` +
    `${n.nakshatra.name} (${n.nakshatra.lord}'s star, pada ${n.nakshatra.pada}); ` +
    `the tithi is ${n.tithi.label} of the ${n.tithi.paksha} paksha.`;

  // Day wheel: full 24h local, with convention windows placed on it.
  const wheel = $("wheel");
  const segs = [];
  const put = (msA, msB, cls, label) => {
    const a = localMinutes(msA), b = localMinutes(msB);
    const left = (a / 1440) * 100, width = (Math.max(b - a, 0) / 1440) * 100;
    segs.push(`<div class="seg ${cls}" style="left:${left}%;width:${width}%">${label}</div>`);
  };
  if (n.muhurtas && n.muhurtas.brahma) put(n.muhurtas.brahma.starts, n.muhurtas.brahma.ends, "brahma", "Brahma");
  if (n.muhurtas && n.muhurtas.abhijit) put(n.muhurtas.abhijit.starts, n.muhurtas.abhijit.ends, "abhijit", "Abhijit");
  if (n.rahu_kaal && n.rahu_kaal.starts) put(n.rahu_kaal.starts, n.rahu_kaal.ends, "rahu", "Rahu Kaal");
  const nowMin = (localMinutes(Date.now()) / 1440) * 100;
  wheel.innerHTML = segs.join("") + `<div class="now-pin" style="left:${nowMin}%"></div>`;
  $("w-open").textContent = rs.sunrise ? "sunrise " + fmtTime(rs.sunrise) : "—";
  $("w-noon").textContent = "local day";
  $("w-close").textContent = rs.sunset ? "sunset " + fmtTime(rs.sunset) : "—";

  const card = (k, v, sub, gold) =>
    `<div class="card ${gold ? "gold" : ""}"><small class="k">${k}</small><div class="v">${v}</div><div class="sub">${sub || ""}</div></div>`;
  $("day-grid").innerHTML =
    card("Sunrise · Sunset", `${rs.sunrise ? fmtTime(rs.sunrise) : "—"} · ${rs.sunset ? fmtTime(rs.sunset) : "—"}`, "topocentric, refraction-corrected", true) +
    card("Moonrise · Moonset", `${rs.moonrise ? fmtTime(rs.moonrise) : "—"} · ${rs.moonset ? fmtTime(rs.moonset) : "—"}`, "the Moon's own day") +
    card("Vara lord", n.vara.lord, n.vara.name, true) +
    card("Karaṇa", n.karana.name, `half-tithi ${n.karana.index} of 60`) +
    card("Brahma-muhūrta", n.muhurtas.brahma ? `${fmtTime(n.muhurtas.brahma.starts)} – ${fmtTime(n.muhurtas.brahma.ends)}` : "—", "96–48 min before sunrise") +
    card("Abhijit", n.muhurtas.abhijit ? `${fmtTime(n.muhurtas.abhijit.starts)} – ${fmtTime(n.muhurtas.abhijit.ends)}` : "—", "the victor's window at midday") +
    card("Rahu Kaal", n.rahu_kaal.starts ? `${fmtTime(n.rahu_kaal.starts)} – ${fmtTime(n.rahu_kaal.ends)}` : "—", "convention, part " + n.rahu_kaal.part + " of 8") +
    card("Hora now", n.hora.current ? n.hora.current.lord : "—", n.hora.current ? `until ${fmtTime(n.hora.current.ends)}` : "", true);

  const tl = d.transitions.map((t) =>
    `<div class="tl-item ${t.kind === "nakshatra" ? "moon" : ""}"><span class="when">${fmtTime(t.at)}</span> <span class="what">${t.kind === "tithi" ? "Tithi becomes" : "Moon enters"} <b>${t.value}</b></span></div>`
  ).join("");
  $("day-timeline").innerHTML = tl || '<div class="tl-item"><span class="what">No panchanga hand turns again today — a rare, still day.</span></div>';
}

/* ------------------------------------------------------------------ week */

function renderWeek() {
  const w = state.week;
  if (!w) return;
  const todayStart = Date.now() - (Date.now() % 86400000);
  $("week-strip").innerHTML = w.days.map((d) => {
    const today = d.date_ms_utc === todayStart;
    return `<div class="day-card ${today ? "today" : ""}">
      <div class="dow">${fmtDay(d.date_ms_utc)}${today ? " · today" : ""}</div>
      <div class="lord">${d.lord}</div>
      <div class="msign">Moon in ${d.moon_sign}</div>
      <div class="tithi">${d.tithi}</div>
    </div>`;
  }).join("");
  const ev = w.events.map((e) => {
    const cls = e.kind === "full_moon" || e.kind === "new_moon" ? "" : e.kind.startsWith("retro") ? "retro" : "moon";
    return `<div class="tl-item ${cls}"><span class="when">${fmtDateTime(e.at)}</span> <span class="what">${describe(e)}</span></div>`;
  }).join("");
  $("week-timeline").innerHTML = ev || '<div class="tl-item"><span class="what">A quiet week in the sky.</span></div>';
}

function describe(e) {
  switch (e.kind) {
    case "moon_ingress": return `Moon enters <b>${e.value}</b>`;
    case "sankranti": return `Saṅkrānti — Sun enters <b>${e.value}</b>`;
    case "new_moon": case "full_moon": {
      const hint = e.eclipse_hint && e.eclipse_hint.indicator !== "unlikely"
        ? ` <span class="tier tier-measured">eclipse ${e.eclipse_hint.indicator}</span>` : "";
      return `<b>${e.value}</b>${hint}`;
    }
    case "retrograde": return `<b>${e.body}</b> turns retrograde`;
    case "direct": return `<b>${e.body}</b> resumes direct motion`;
    default: return `${e.kind} — ${e.value}`;
  }
}

/* ----------------------------------------------------------------- month */

function renderMonth() {
  const m = state.month;
  if (!m) return;
  const items = m.events.filter((e) =>
    ["new_moon", "full_moon", "sankranti", "retrograde", "direct"].includes(e.kind));
  $("month-timeline").innerHTML = items.map((e) => {
    const eclipse = e.eclipse_hint && e.eclipse_hint.indicator === "likely" ? "eclipse" : "";
    const cls = ["new_moon", "full_moon"].includes(e.kind) ? eclipse : e.kind.startsWith("retro") ? "retro" : "";
    const extra = e.eclipse_hint ? `<div class="extra">Moon latitude ${e.eclipse_hint.moon_latitude_deg}° · geometric indicator</div>` : "";
    return `<div class="tl-item ${cls}"><span class="when">${fmtDateTime(e.at)}</span> <span class="what">${describe(e)}</span>${extra}</div>`;
  }).join("") || '<div class="tl-item"><span class="what">No lunations in this window.</span></div>';
}

/* ------------------------------------------------------------------ year */

function renderYear() {
  const y = state.year;
  if (!y) return;
  const lordCard = (k, sign, note) =>
    `<div class="card"><small class="k">${k}</small><div class="v">${sign}</div><div class="sub">${note}</div></div>`;
  $("year-lords").innerHTML =
    lordCard("Jupiter — the year's slow lamp", y.year_lords.jupiter_sign, "changes sign roughly yearly") +
    lordCard("Saturn — the season-keeper", y.year_lords.saturn_sign, "lingers ~2.5 years per sign") +
    lordCard("Rahu — the eclipse axis", y.year_lords.rahu_sign, "retreats one sign every ~18 months");

  const big = [
    ...y.lunations.filter((e) => e.eclipse_hint && e.eclipse_hint.indicator !== "unlikely"),
    ...y.ingresses,
    ...y.sankrantis,
  ].sort((a, b) => a.at - b.at);
  $("year-timeline").innerHTML = big.map((e) => {
    const cls = e.eclipse_hint && e.eclipse_hint.indicator === "likely" ? "eclipse" : "";
    return `<div class="tl-item ${cls}"><span class="when">${fmtDateTime(e.at)}</span> <span class="what">${describe(e)}</span></div>`;
  }).join("") || '<div class="tl-item"><span class="what">A quiet year ahead.</span></div>';
}

/* -------------------------------------------------------------- location */

function loadAll() {
  const q = state.obs ? `lat=${state.obs.lat}&lon=${state.obs.lon}` : "";
  const lang = localStorage.getItem("ka-lang") || "en";
  const j = (url) => fetch(url).then((r) => r.json());
  Promise.all([
    j(`/api/v1/now?${q}&_=${Date.now()}`),
    j(`/api/v1/report/day?${q}&_=${Date.now()}`),
    j(`/api/v1/report/week?${q}&_=${Date.now()}`),
    j(`/api/v1/report/month?${q}&_=${Date.now()}`),
    j(`/api/v1/report/year?${q}&_=${Date.now()}`),
    j(`/api/v1/brief?${q}&lang=${lang}&_=${Date.now()}`),
  ]).then(([now, day, week, month, year, brief]) => {
    state.now = now; state.day = day; state.week = week; state.month = month; state.year = year;
    renderBrief(brief);
    renderHero(); renderDay(); renderWeek(); renderMonth(); renderYear();
  }).catch((err) => {
    $("hero-date").textContent = "The court could not be reached: " + err.message;
  });
}

/* ----------------------------------------------------------- daily brief */

function renderBrief(b) {
  state.brief = b;
  const lines = b.lines.map((l) =>
    `<p class="brief-line" data-tier="${l.tier}">${l.text}<small class="tier-tag">${l.tier}</small></p>`
  ).join("");
  $("brief-lines").innerHTML = lines;
  $("brief-tomorrow").innerHTML = `☾ ${b.tomorrow.text}`;
  $("brief-skill").textContent = b.skill_statement;
  $("brief-lang").textContent = { en: "English", hi: "हिंदी", ar: "العربية" }[b.lang];
  const rtl = b.lang === "ar";
  $("brief").setAttribute("dir", rtl ? "rtl" : "ltr");
}

function wireLang() {
  const sel = $("lang");
  let saved = "en";
  try { saved = localStorage.getItem("ka-lang") || "en"; } catch (e) { void e; }
  sel.value = saved;
  sel.addEventListener("change", () => {
    const lang = sel.value;
    try { localStorage.setItem("ka-lang", lang); } catch (e) { void e; }
    const q = state.obs ? `&lat=${state.obs.lat}&lon=${state.obs.lon}` : "";
    fetch(`/api/v1/brief?lang=${lang}${q}&_=${Date.now()}`)
      .then((r) => r.json())
      .then(renderBrief)
      .catch(() => {});
  });
}

$("locate").addEventListener("click", () => {
  if (!navigator.geolocation) return;
  navigator.geolocation.getCurrentPosition((pos) => {
    state.obs = { lat: pos.coords.latitude.toFixed(4), lon: pos.coords.longitude.toFixed(4) };
    $("loc-name").textContent = `${state.obs.lat}, ${state.obs.lon}`;
    loadAll();
  }, () => { $("loc-name").textContent = "location unavailable"; });
});

/* ------------------------------------------------------- streak / share / remind */

function updateStreak() {
  const KEY = "ka-streak";
  const TODAY = new Date().toISOString().slice(0, 10);
  let data;
  try { data = JSON.parse(localStorage.getItem(KEY)) || { count: 0, last: null }; } catch (e) { void e; data = { count: 0, last: null }; }
  if (data.last !== TODAY) {
    const yest = new Date(); yest.setDate(yest.getDate() - 1);
    const yestStr = yest.toISOString().slice(0, 10);
    data.count = (data.last === yestStr) ? data.count + 1 : 1;
    data.last = TODAY;
    try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) { void e; }
  }
  const pill = $("streak-pill");
  if (pill) pill.textContent = `🔥 ${data.count} day${data.count === 1 ? "" : "s"}`;
  if (pill) pill.title = `${data.count}-day streak — come back tomorrow`;
}

function wireShare() {
  const btn = $("share-btn");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const n = state.now;
    const text = n
      ? `${n.tithi.label} · ${n.nakshatra.name} pada ${n.nakshatra.pada} · Moon in ${n.moon_sign.sanskrit}`
      : "Today at the Court — Kingsastrology";
    const url = location.href;
    if (navigator.share) {
      try { await navigator.share({ title: "Today at the Court", text, url }); } catch (e) { void e; }
    } else if (navigator.clipboard) {
      await navigator.clipboard.writeText(`${text}\n${url}`);
      btn.textContent = "✓ copied";
      setTimeout(() => { btn.textContent = "↗ share your day's sky"; }, 1600);
    }
  });
}

function wireRemind() {
  const btn = $("remind-btn"), note = $("remind-note");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    if (!("Notification" in window)) { note.textContent = "Notifications not supported in this browser."; return; }
    let perm = Notification.permission;
    if (perm === "default") perm = await Notification.requestPermission();
    if (perm !== "granted") { note.textContent = "Permission denied."; return; }
    const snap = state.now;
    if (!snap) return;
    const msg = snap.tithi ? `Tomorrow: ${snap.tithi.label} · ${snap.nakshatra.name}` : "Your daily sky is ready";
    try {
      new Notification("Kingsastrology — your daily sky", { body: msg });
      note.textContent = "A nudge is on its way — come back at 8 AM for the fresh sky.";
    } catch (e) { void e; note.textContent = "Could not show a notification."; }
  });
}

/* ------------------------------------------------------- dot nav / reveal */

function wireDotNav() {
  const ids = ["day", "week", "month", "year", "moment"];
  const nav = $("dot-nav");
  if (!nav) return;
  nav.innerHTML = ids.map((id) => `<a href="#${id}" title="${id}"></a>`).join("");
  const dots = [...nav.querySelectorAll("a")];
  const chapters = ids.map((id) => document.getElementById(id)).filter(Boolean);
  const obs = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) {
      const idx = chapters.indexOf(e.target);
      dots.forEach((d, i) => d.classList.toggle("active", i === idx));
    }
  }, { rootMargin: "-45% 0px -45% 0px", threshold: 0 });
  chapters.forEach((c) => obs.observe(c));
}

function wireReveal() {
  const items = document.querySelectorAll(".card, .day-card, .tl-item, .chapter-head, .day-wheel");
  items.forEach((el) => el.classList.add("reveal"));
  const obs = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) {
      e.target.classList.add("in");
      obs.unobserve(e.target);
    }
  }, { threshold: 0.18 });
  items.forEach((el) => obs.observe(el));
}

/* ------------------------------------------------------- live ticking */

let tickTimer = null;
function startLiveTicking() {
  if (tickTimer) return;
  tickTimer = setInterval(() => {
    if (!state.now || !state.now.hora || !state.now.hora.current) return;
    const left = Math.max(0, state.now.hora.current.ends - Date.now()) / 60000;
    const el = document.getElementById("c-hora-next");
    if (el) el.innerHTML = `ends in <span class="count">${left < 1 ? "under a minute" : Math.round(left) + " min"}</span>`;
  }, 30_000);
}

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}

setInterval(tickHero, 1000);
setInterval(() => fetch(`/api/v1/now?_=${Date.now()}`).then((r) => r.json()).then((n) => {
  state.now = n; renderHero();
}).catch(() => {}), 60_000);
tickHero();
loadAll();
updateStreak();
wireShare();
wireRemind();
wireDotNav();
wireReveal();
wireLang();
startLiveTicking();
