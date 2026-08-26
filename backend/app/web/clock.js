/*
 * Kingsastrology — Spacetime Clock renderer.
 *
 * Stage geometry: Earth sits at the focus of the court (the product is
 * geocentric), the grahas ride a schematic spacetime fabric that dips toward
 * the centre, and a sidereal zodiac ring wraps the whole stage like a clock
 * face. All angles are true geocentric sidereal longitudes; radial distances
 * are compressed (r^0.45) and the Moon's orbit enlarged for legibility.
 */
"use strict";

(() => {
  const DEG = Math.PI / 180;
  const TILT_Y = 0.5;      // vertical squash of the orbital plane
  const WELL_DEPTH_FACTOR = 0.15; // fraction of stage height the funnel dips

  const GRAHAS = [
    { key: "Sun",     name: "Surya",   glyph: "\u2609", color: "#ffd77a" },
    { key: "Moon",    name: "Chandra", glyph: "\u263D", color: "#dfe7f5" },
    { key: "Mercury", name: "Budha",   glyph: "\u263F", color: "#27c5b6" },
    { key: "Venus",   name: "Shukra",  glyph: "\u2640", color: "#f7a8c4" },
    { key: "Mars",    name: "Mangala", glyph: "\u2642", color: "#ff7a7a" },
    { key: "Jupiter", name: "Guru",    glyph: "\u2643", color: "#ffb35c" },
    { key: "Saturn",  name: "Shani",   glyph: "\u2644", color: "#b08cff" },
    { key: "Rahu",    name: "Rahu",    glyph: "\u260A", color: "#8a7dff" },
    { key: "Ketu",    name: "Ketu",    glyph: "\u260B", color: "#7fd0ff" },
  ];

  const SPEEDS = [
    { label: "Real time", f: 1 },
    { label: "1 hour / sec", f: 3600 },
    { label: "1 day / sec", f: 86400 },
    { label: "1 week / sec", f: 604800 },
    { label: "1 month / sec", f: 2629800 },
  ];

  // Published error bars (arcmin) — mirrors services/sky_engine.py. See Tribunal.
  const ERROR_ARCMIN = {
    Sun: 0.5, Moon: 22, Mercury: 0.6, Venus: 0.6,
    Mars: 0.5, Jupiter: 1.2, Saturn: 5, Rahu: 3, Ketu: 3,
  };

  const I18N = {
    en: {
      title: "Spacetime Clock",
      subtitle: "the royal court of the grahas, riding the curved sky",
      local_date: "local date", local_time: "local time", epoch: "epoch", ayanamsa: "ayanamsa",
      tribunal: "Tribunal",
      cal_hijri: "Hijrī", cal_jalali: "Jalālī", cal_vikram: "Vikram Saṃvat", cal_saka: "Śaka", cal_kali: "Kali ahargaṇa",
      hilal_title: "The crescent — hilāl", hilal_check: "Check this evening",
      hilal_disclaimer: "Observables are computed; the visibility class is one labelled criterion (Yallop, hypothesis-under-trial). Not a religious ruling.",
      graha: "Graha", rasi: "Rāśi", deg: "Deg", nakshatra: "Nakshatra",
      legend_note: "Geocentric sidereal longitudes. R = retrograde. Rahu/Ketu are the mean lunar nodes. Tap a row for its lesson (Tafhīm mode).",
      now: "Now", drishti: "Drishti",
      provenance: "Visualization-grade ephemeris: JPL approximate Keplerian elements (1800–2050) with truncated lunar theory; sidereal via Lahiri ayanamsa approximation · orbit radii compressed (r^0.45) and the Moon's orbit enlarged for legibility · schematic fabric — the Swiss-Ephemeris compute engine remains the source of truth.",
      see_tribunal: "See the Tribunal ledger",
    },
    hi: {
      title: "देशकाल घड़ी",
      subtitle: "ग्रहों का राजदरबार, वक्र आकाश पर",
      local_date: "स्थानीय तिथि", local_time: "स्थानीय समय", epoch: "जूलियन दिवस", ayanamsa: "अयनांश",
      tribunal: "ट्रिब्यूनल",
      cal_hijri: "हिजरी", cal_jalali: "जलाली", cal_vikram: "विक्रम संवत्", cal_saka: "शक", cal_kali: "कलि अहर्गण",
      hilal_title: "हिलाल — नया चाँद", hilal_check: "आज की शाम देखें",
      hilal_disclaimer: "माप गणना से हैं; दृश्यता-वर्ग एक घोषित मापदंड है (यालॉप, परीक्षणाधीन)। यह धार्मिक आदेश नहीं है।",
      graha: "ग्रह", rasi: "राशि", deg: "अंश", nakshatra: "नक्षत्र",
      legend_note: "भू-केंद्रित निरयण रेखांश। R = वक्री। राहु/केतु चंद्र-पात हैं। पाठ के लिए किसी पंक्ति पर टैप करें।",
      now: "अभी", drishti: "दृष्टि",
      provenance: "दृश्य-स्तर की गणना: JPL सन्निकट केप्लर तत्व (1800–2050) + संक्षिप्त चंद्र-सिद्धांत; लाहिड़ी अयनांश · कक्षा-त्रिज्याएँ संपीड़ित, चंद्र-कक्षा बड़ी दिखाई गई है · वास्तविक स्रोत: Swiss-Ephemeris इंजन।",
      see_tribunal: "ट्रिब्यूनल-बही देखें",
    },
    ar: {
      title: "ساعة الزمكان",
      subtitle: "بلاط الكواكب الملكي على قبة الزمن المنحني",
      local_date: "التاريخ المحلي", local_time: "الوقت المحلي", epoch: "اليوم اليولياني", ayanamsa: "الأيانامسا",
      tribunal: "المحكمة",
      cal_hijri: "هجري", cal_jalali: "جلالي", cal_vikram: "فيكرام", cal_saka: "شاكا", cal_kali: "أيام كالي",
      hilal_title: "الهلال", hilal_check: "افحص هذه المساء",
      hilal_disclaimer: "القياسات محسوبة؛ وتصنيف الرؤية معيار مُعلن واحد (ياللوب، قيد التجربة). ليس حكمًا شرعيًا.",
      graha: "الكوكب", rasi: "البرج", deg: "درجة", nakshatra: "المنزل القمري",
      legend_note: "أطوال sidereal مركزية الأرض. R = تراجعي. راهو/كيتو العقدتان القمريتان. انقر صفًا للدرس.",
      now: "الآن", drishti: "الدريشتي",
      provenance: "فلك بدرجة العرض: عناصر كبلر التقريبية (1800–2050) ونظرية قمرية مختصرة؛ الأيانامسا اللاهيري · أنصاف الأقطار مضغوطة للوضوح · المصدر المرجعي: محرك Swiss Ephemeris.",
      see_tribunal: "سجل المحكمة",
    },
  };

  // Tafhīm mode (Layer 4): long-press any element and receive the lesson.
  const LESSONS = {
    Sun: {
      q: "Why does the Sun lead the court?",
      en: "Astronomically [measured]: the Sun holds 99.8% of the solar system's mass — its gravity is the curvature you see drawn here. In the canon [doctrine, R-2.1]: the Sun is the soul and the king among planets.",
      hi: "खगोल [मापित]: सूर्य के पास सौरमंडल का 99.8% द्रव्यमान है — यही यहाँ दिखाया गया वक्र है। शास्त्र [R-2.1]: सूर्य आत्मा है और ग्रहों का राजा।",
      ar: "فلكيًا [مقاس]: الشمس تملك 99.8% من كتلة المجموعة — جاذبيتها هي الانحناء المرسوم هنا. في النص [R-2.1]: الشمس هي الروح وملك الكواكب.",
    },
    Moon: {
      q: "Why is the Moon's orbit drawn enlarged?",
      en: "[measured] The Moon is only 384,400 km from Earth — on this compressed map its true orbit would vanish inside the Earth dot. The dashed halo is enlarged for legibility; its ANGLE is always the true sidereal longitude. The canon [R-2.1]: the Moon is the mind.",
      hi: "[मापित] चंद्रमा पृथ्वी से केवल 384,400 किमी दूर है — संपीड़ित मानचित्र पर उसकी वास्तविक कक्षा पृथ्वी-बिंदु के भीतर सिमट जाती। बिंदीदार वलय बड़ा दिखाया गया है; कोण सदैव वास्तविक है। शास्त्र [R-2.1]: चंद्रमा मन है।",
      ar: "[مقاس] القمر يبعد 384,400 كم فقط — مداره الحقيقي يختفي داخل نقطة الأرض على هذه الخريطة. الحلقة مكبَّرة للوضوح؛ والزاوية دائمًا حقيقية. [R-2.1]: القمر هو العقل.",
    },
    retrograde: {
      q: "What does the R badge mean?",
      en: "[measured] A planet is retrograde when its geocentric longitude decreases — an apparent backward drift caused by Earth overtaking it (or being overtaken). The engine detects it by comparing the longitude 12 hours ahead and behind. Nothing reverses in the sky; it is geometry.",
      hi: "[मापित] जब किसी ग्रह का भू-केंद्रित रेखांश घटने लगे तो वह वक्री (R) है — पृथ्वी के आगे निकलने से पैदा दृश्य-प्रतीति। इंजन ±12 घंटे की तुलना से इसे पहचानता है। आकाश में कुछ उल्टा नहीं चलता; यह ज्यामिति है।",
      ar: "[مقاس] الكوكب تراجعي (R) عندما يقل طوله المركزي الأرضي — وهبٌ ظاهري بسبب تجاوز الأرض له. يكتشفه المحرك بمقارنة ±12 ساعة. لا شيء يسير عكسيًا في السماء؛ إنه هندسة.",
    },
    nakshatra: {
      q: "What is a nakshatra?",
      en: "[measured] The 27 nakshatras divide the ecliptic into 27 equal arcs of 13°20′. Each graha sits in exactly one; the Moon's nakshatra is the traditional pulse of the day.",
      hi: "[मापित] 27 नक्षत्र क्रांति-वृत्त को 13°20′ के 27 बराबर भागों में बाँटते हैं। प्रत्येक ग्रह एक में स्थित होता है; चंद्र-नक्षत्र दिन की पारंपरिक नाड़ी है।",
      ar: "[مقاس] الـ27 منزلاً قمرياً يقسمان الدائرة إلى 27 قوساً متساوياً (13°20′). كل كوكب في واحد منها؛ ومنزل القمر نبض اليوم التقليدي.",
    },
    sidereal: {
      q: "Sidereal or tropical — why two zodiacs?",
      en: "[measured] The equinox slips ~50″/yr against the stars (precession). The tropical zodiac pins 0° Aries to the equinox; the sidereal pins it to the star Chitra (Lahiri ayanamsa ≈ 24°13′ today). This clock shows sidereal, the Vedic convention; the difference IS the ayanamsa shown in the header.",
      hi: "[मापित] विषुव प्रति वर्ष ~50″ पीछे सरकता है (अयन-चलन)। सायन लग्न विषुव को 0° मेष मानता है; निरयण चित्रा तारे को (लाहिड़ी अयनांश ≈ 24°13′)। यह घड़ी निरयण दिखाती है; दोनों का अंतर ही अयनांश है।",
      ar: "[مقاس] ينزلق الاعتدال ~50″ سنويًا (التقدم المحوري). الدائرة الاستوائية تربط 0° الحمل بالاعتدال، والفلكية تربطه بنجم سبيكا (الأيانامسا اللاهيري ≈ 24°13′). هذه الساعة فلكية؛ والفرق هو الأيانامسا المعروض.",
    },
    drishti: {
      q: "What do the chords mean?",
      en: "[doctrine, R-2.13] Planetary sight: every graha casts ¼ sight on the 3rd & 10th houses from itself, ½ on the 5th & 9th, ¾ on the 4th & 8th, and full sight on the 7th. Saturn's 3rd/10th, Jupiter's 5th/9th and Mars's 4th/8th are full. Chords fade with strength; a 15° orb about the house-middle applies. Rahu/Ketu are excluded — the table does not include them.",
      hi: "[शास्त्र, R-2.13] ग्रह-दृष्टि: प्रत्येक ग्रह स्वयं से 3-10 भाव पर ¼, 5-9 पर ½, 4-8 पर ¾ और 7 पर पूर्ण दृष्टि रखता है। शनि की 3/10, गुरु की 5/9 और मंगल की 4/8 पूर्ण है। जीवा की गहराई दृष्टि-बल दर्शाती है; भाव-मध्य से 15° की कक्षा। राहु/केतु सारणी में नहीं — अतः नहीं दिखाए जाते।",
      ar: "[نص، R-2.13] نظر الكواكب: كل كوكب ينظر إلى البيتَين 3 و10 برُبع، و5 و9 بالنصف، و4 و8 بثلاثة أرباع، و7 كاملة. زحل 3/10 والمشتري 5/9 والمريخ 4/8 كاملة. تشتد الوتر بالقوة، وهامش 15°. راهو/كيتو خارج الجدول.",
    },
  };
  for (const g of GRAHAS) {
    if (!LESSONS[g.key]) {
      LESSONS[g.key] = {
        q: `What is ${g.name}?`,
        en: `Astronomically [measured]: a real body of the solar system, shown at its true geocentric sidereal longitude. Its classical signification lives in the canon [doctrine, R-2.1]; this screen reports placement, never verdict.`,
        hi: `खगोल [मापित]: सौरमंडल की वास्तविक सत्ता, वास्तविक भू-केंद्रित निरयण रेखांश पर। इसका शास्त्रीय अर्थ [R-2.1] में है; यह पटल केवल स्थिति बताता है, निर्णय नहीं।`,
        ar: `فلكيًا [مقاس]: جرم حقيقي يظهر عند طوله sidereal الحقيقي. دلالته الكلاسيكية في النص [R-2.1]؛ وهذه الشاشة تذكر الموضع لا الحكم.`,
      };
    }
  }

  const state = {
    mode: "live",        // live | play | paused
    simMs: Date.now(),
    speedIndex: 2,
    trails: new Map(),   // key -> [{x, y}]
    lang: "en",
    drishtiOn: false,
    drishtiChords: null, // from /api/v1/sky, cached
    calendars: null,     // from /api/v1/calendars, cached
    lastFetchedMs: 0,
    lastFetchAt: 0,
  };

  const canvas = document.getElementById("sky");
  const ctx = canvas.getContext("2d");
  const stageEl = document.getElementById("stage");
  let cssW = 0;
  let cssH = 0;
  let dpr = 1;
  let staticLayer = null;
  let geom = null;

  // ---------------------------------------------------------------- layout

  function layout() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    cssW = stageEl.clientWidth;
    cssH = stageEl.clientHeight;
    canvas.width = Math.round(cssW * dpr);
    canvas.height = Math.round(cssH * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const cz = Math.min(cssW, cssH);
    void cz;
    // The zodiac bezel must fit the stage height as well as its width.
    const ringR = Math.min(cssW * 0.46, cssH * 0.46);
    const sheetR = Math.min(ringR * 0.82, cssW * 0.42);
    geom = {
      cx: cssW / 2,
      cy: cssH * 0.5,
      ringR,
      sheetR,
      wellDepth: cssH * WELL_DEPTH_FACTOR,
      moonHalo: Math.max(20, Math.min(42, sheetR * 0.1)),
    };
    buildStaticLayer();
    state.trails.clear();
  }

  // Radial compression: geocentric AU -> normalised sheet radius [0, 1].
  const SATURN_NORM = Math.pow(9.53, 0.45);
  function auToNorm(au) {
    return Math.pow(Math.max(au, 1e-6), 0.45) / SATURN_NORM;
  }

  // Project a point given sidereal longitude, normalised radius, depth [0,1].
  function project(lonDeg, normU, depth01) {
    const a = (lonDeg - 90) * DEG;
    const r = geom.sheetR * normU;
    const dip = geom.wellDepth * Math.pow(1 - Math.min(normU, 1), 2.2) * depth01;
    return {
      x: geom.cx + Math.cos(a) * r,
      y: geom.cy + Math.sin(a) * r * TILT_Y + dip,
    };
  }

  // ----------------------------------------------------------- static layer

  function buildStaticLayer() {
    staticLayer = document.createElement("canvas");
    staticLayer.width = Math.round(cssW * dpr);
    staticLayer.height = Math.round(cssH * dpr);
    const c = staticLayer.getContext("2d");
    c.setTransform(dpr, 0, 0, dpr, 0, 0);

    drawStars(c);
    drawWellGrid(c);
    drawZodiacRing(c);
  }

  function drawStars(c) {
    let seed = 20260826;
    const rnd = () => {
      seed = (seed * 1103515245 + 12345) % 2147483648;
      return seed / 2147483648;
    };
    c.save();
    for (let i = 0; i < 260; i += 1) {
      const x = rnd() * cssW;
      const y = rnd() * cssH;
      const s = rnd() * 1.3 + 0.2;
      const warm = rnd() > 0.82;
      c.fillStyle = warm ? "rgba(231,189,99,.5)" : `rgba(214,226,255,${0.18 + rnd() * 0.5})`;
      c.beginPath();
      c.arc(x, y, s, 0, Math.PI * 2);
      c.fill();
    }
    c.restore();
  }

  // Schematic spacetime fabric: concentric rings + spokes sagging into the well.
  function drawWellGrid(c) {
    const { cx, cy, sheetR, wellDepth } = geom;

    // Soft shadow pooling at the bottom of the funnel.
    const shade = c.createRadialGradient(cx, cy + wellDepth * 0.55, 10, cx, cy + wellDepth * 0.55, sheetR * 0.75);
    shade.addColorStop(0, "rgba(3,7,17,.85)");
    shade.addColorStop(0.45, "rgba(10,20,38,.45)");
    shade.addColorStop(1, "rgba(10,20,38,0)");
    c.fillStyle = shade;
    c.save();
    c.translate(cx, cy + wellDepth * 0.35);
    c.scale(1, TILT_Y);
    c.beginPath();
    c.arc(0, 0, sheetR * 0.8, 0, Math.PI * 2);
    c.fill();
    c.restore();

    const ringCount = 9;
    const spokeCount = 24;
    const samples = 84;
    const depthOf = (u) => Math.pow(Math.max(1 - u, 0), 2.2);

    c.lineWidth = 1;
    c.strokeStyle = "rgba(120,150,205,.20)";
    for (let ri = 1; ri <= ringCount; ri += 1) {
      const u = ri / ringCount * 0.97;
      c.beginPath();
      for (let si = 0; si <= samples; si += 1) {
        const p = project((si / samples) * 360 + 270, u, 1);
        if (si === 0) c.moveTo(p.x, p.y); else c.lineTo(p.x, p.y);
      }
      c.stroke();
    }

    for (let sp = 0; sp < spokeCount; sp += 1) {
      const lon = (sp / spokeCount) * 360 + 270;
      c.beginPath();
      for (let k = 0; k <= 60; k += 1) {
        const p = project(lon, (k / 60) * 0.97, 1);
        if (k === 0) c.moveTo(p.x, p.y); else c.lineTo(p.x, p.y);
      }
      c.stroke();
    }
    void wellDepth;
  }

  function drawZodiacRing(c) {
    const { cx, cy, ringR } = geom;
    c.save();

    c.strokeStyle = "rgba(232,190,93,.55)";
    c.lineWidth = 1.4;
    c.beginPath(); c.arc(cx, cy, ringR, 0, Math.PI * 2); c.stroke();
    c.strokeStyle = "rgba(232,190,93,.28)";
    c.beginPath(); c.arc(cx, cy, ringR * 0.925, 0, Math.PI * 2); c.stroke();

    for (let s = 0; s < 12; s += 1) {
      const start = s * 30;
      const end = start + 30;
      c.fillStyle = s % 2 === 0 ? "rgba(231,189,99,.05)" : "rgba(39,197,182,.04)";
      c.beginPath();
      c.arc(cx, cy, ringR, start * DEG - 90 * DEG, end * DEG - 90 * DEG);
      c.arc(cx, cy, ringR * 0.925, end * DEG - 90 * DEG, start * DEG - 90 * DEG, true);
      c.closePath();
      c.fill();
    }

    c.font = `${Math.max(15, Math.min(21, ringR * 0.07))}px Inter, system-ui, sans-serif`;
    c.textAlign = "center";
    c.textBaseline = "middle";
    for (let s = 0; s < 12; s += 1) {
      const mid = s * 30 + 15;
      const p = ringPoint(mid, ringR * 0.963);
      c.fillStyle = "rgba(231,189,99,.92)";
      c.fillText(Ephemeris.SIGNS[s][2], p.x, p.y);

      for (let t = 0; t < 30; t += 6) {
        const lon = start(t, s);
        tick(c, lon, t === 0);
      }
    }

    c.fillStyle = "rgba(174,183,200,.75)";
    c.font = `11px Inter, system-ui, sans-serif`;
    const top = ringPoint(0, ringR * 0.83);
    c.fillText("sidereal \u00B7 Lahiri \u00B7 0\u00B0 Mesha at crown", top.x, top.y);
    c.restore();

    function start(t, s) { return s * 30 + t; }
    function ringPoint(lon, r) {
      const a = (lon - 90) * DEG;
      return { x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r };
    }
    function tick(c2, lon, major) {
      const inner = ringPoint(lon, major ? ringR * 0.9 : ringR * 0.925);
      const outer = ringPoint(lon, ringR);
      c2.strokeStyle = major ? "rgba(232,190,93,.65)" : "rgba(232,190,93,.22)";
      c2.lineWidth = major ? 1.4 : 1;
      c2.beginPath();
      c2.moveTo(inner.x, inner.y);
      c2.lineTo(outer.x, outer.y);
      c2.stroke();
    }
  }

  // ------------------------------------------------------------ dynamic sky

  function bodyScreenPos(key, lonSidereal, distAU) {
    if (key === "Moon" || key === "Rahu" || key === "Ketu") {
      const earthP = project(0, 0, 0);
      const a = (lonSidereal - 90) * DEG;
      const rx = geom.moonHalo;
      const ry = geom.moonHalo * TILT_Y;
      return {
        x: earthP.x + Math.cos(a) * rx,
        y: earthP.y + Math.sin(a) * ry,
      };
    }
    const u = auToNorm(distAU);
    return project(lonSidereal, u * 0.94, 1);
  }

  function pushTrail(key, p) {
    let list = state.trails.get(key);
    if (!list) { list = []; state.trails.set(key, list); }
    const last = list[list.length - 1];
    if (!last || Math.hypot(last.x - p.x, last.y - p.y) > 2.2) {
      list.push({ x: p.x, y: p.y });
      if (list.length > 220) list.shift();
    }
  }

  function drawTrail(c, key, color) {
    const list = state.trails.get(key);
    if (!list || list.length < 3) return;
    c.save();
    c.lineWidth = 1.6;
    c.lineCap = "round";
    for (let i = 1; i < list.length; i += 1) {
      c.strokeStyle = color;
      c.globalAlpha = (i / list.length) * 0.4;
      c.beginPath();
      c.moveTo(list[i - 1].x, list[i - 1].y);
      c.lineTo(list[i].x, list[i].y);
      c.stroke();
    }
    c.restore();
  }

  function drawBody(c, g, body) {
    const p = bodyScreenPos(g.key, body.lonSidereal, body.distAU);
    const size = g.key === "Sun" ? 9 : g.key === "Saturn" ? 6 : g.key === "Jupiter" ? 6.5 : g.key === "Moon" ? 5.5 : 5;

    const glow = c.createRadialGradient(p.x, p.y, 0, p.x, p.y, size * 4.4);
    glow.addColorStop(0, hexA(g.color, 0.5));
    glow.addColorStop(0.4, hexA(g.color, 0.14));
    glow.addColorStop(1, hexA(g.color, 0));
    c.fillStyle = glow;
    c.beginPath();
    c.arc(p.x, p.y, size * 4.4, 0, Math.PI * 2);
    c.fill();

    c.fillStyle = g.color;
    c.beginPath();
    c.arc(p.x, p.y, size, 0, Math.PI * 2);
    c.fill();
    c.fillStyle = "rgba(255,255,255,.85)";
    c.beginPath();
    c.arc(p.x - size * 0.25, p.y - size * 0.28, size * 0.32, 0, Math.PI * 2);
    c.fill();

    c.font = "12px Inter, system-ui, sans-serif";
    c.textAlign = "left";
    c.textBaseline = "bottom";
    c.fillStyle = "rgba(246,241,223,.82)";
    c.fillText(g.glyph, p.x + size + 4, p.y - size * 0.4);
    return p;
  }

  function drawEarthAndMoon(c, sky) {
    const e = project(0, 0, 0);

    const halo = c.createRadialGradient(e.x, e.y, 0, e.x, e.y, 26);
    halo.addColorStop(0, "rgba(74,163,255,.34)");
    halo.addColorStop(1, "rgba(74,163,255,0)");
    c.fillStyle = halo;
    c.beginPath();
    c.arc(e.x, e.y, 26, 0, Math.PI * 2);
    c.fill();

    c.fillStyle = "#4aa3ff";
    c.beginPath();
    c.arc(e.x, e.y, 5.4, 0, Math.PI * 2);
    c.fill();

    c.save();
    c.strokeStyle = "rgba(223,231,245,.34)";
    c.setLineDash([3, 4]);
    c.beginPath();
    c.ellipse(e.x, e.y, geom.moonHalo, geom.moonHalo * TILT_Y, 0, 0, Math.PI * 2);
    c.stroke();

    // Shadow axis across the nodes.
    const ra = bodyScreenPos("Rahu", sky.rahu.lonSidereal, 0);
    const ke = bodyScreenPos("Ketu", sky.ketu.lonSidereal, 0);
    c.strokeStyle = "rgba(138,125,255,.4)";
    c.beginPath(); c.moveTo(ra.x, ra.y); c.lineTo(ke.x, ke.y); c.stroke();
    c.restore();

    for (const [key, node] of [["Rahu", sky.rahu], ["Ketu", sky.ketu]]) {
      const g = GRAHAS.find((x) => x.key === key);
      const p = bodyScreenPos(key, node.lonSidereal, 0);
      c.fillStyle = g.color;
      c.beginPath();
      c.arc(p.x, p.y, 3.6, 0, Math.PI * 2);
      c.fill();
      c.font = "10px Inter, system-ui, sans-serif";
      c.textAlign = "center";
      c.textBaseline = "top";
      c.fillStyle = "rgba(246,241,223,.6)";
      c.fillText(g.name, p.x, p.y + 6);
    }
    return e;
  }

  function drawHands(c, sky) {
    const sun = sky.bodies.find((b) => b.key === "Sun");
    const moon = sky.bodies.find((b) => b.key === "Moon");
    hand(c, sun.lonSidereal, geom.ringR * 0.92, "rgba(255,215,122,.5)", 1.6);
    hand(c, moon.lonSidereal, geom.ringR * 0.72, "rgba(39,197,182,.55)", 2.2);
    // Earth is the hub of the clock; no separate centre pin is drawn.

    function hand(c2, lon, len, style, width) {
      const a = (lon - 90) * DEG;
      const tipX = geom.cx + Math.cos(a) * len;
      const tipY = geom.cy + Math.sin(a) * len;
      c2.save();
      c2.strokeStyle = style;
      c2.lineWidth = width;
      c2.shadowColor = style;
      c2.shadowBlur = 6;
      c2.beginPath();
      c2.moveTo(geom.cx, geom.cy);
      c2.lineTo(tipX, tipY);
      c2.stroke();
      c2.restore();
    }
  }

  function hexA(hex, alpha) {
    const n = parseInt(hex.slice(1), 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${alpha})`;
  }

  function renderFrame(sky) {
    ctx.clearRect(0, 0, cssW, cssH);
    ctx.drawImage(staticLayer, 0, 0, cssW, cssH);

    const playingFast = state.mode === "play" && SPEEDS[state.speedIndex].f > 1;

    const screenPos = {};
    for (const g of GRAHAS) {
      const body = sky.bodies.find((b) => b.key === g.key);
      if (!body) continue;
      const p = bodyScreenPos(g.key, body.lonSidereal, body.distAU);
      screenPos[g.key] = p;
      if (playingFast && g.key !== "Rahu" && g.key !== "Ketu") pushTrail(g.key, p);
      drawTrail(ctx, g.key, g.color);
    }

    drawEarthAndMoon(ctx, sky);
    if (state.drishtiOn && state.drishtiChords) drawChords(ctx, screenPos);
    for (const g of GRAHAS) {
      if (g.key === "Rahu" || g.key === "Ketu") continue;
      const body = sky.bodies.find((b) => b.key === g.key);
      if (body) drawBody(ctx, g, body);
    }

    drawHands(ctx, sky);
  }

  // R-2.13 drishti chords: strength-coded sight lines between the grahas.
  function drawChords(c, screenPos) {
    c.save();
    c.setLineDash([5, 5]);
    for (const ch of state.drishtiChords) {
      const a = screenPos[ch.from];
      const b = screenPos[ch.to];
      if (!a || !b) continue;
      const strong = ch.strength >= 1.0;
      c.strokeStyle = strong ? "rgba(232,190,93,.75)" : "rgba(120,150,205,.55)";
      c.globalAlpha = 0.25 + ch.strength * 0.55;
      c.lineWidth = strong ? 1.6 : 1.1;
      c.beginPath();
      c.moveTo(a.x, a.y);
      c.lineTo(b.x, b.y);
      c.stroke();
    }
    c.restore();
  }

  // ------------------------------------------------------------------ panels

  const $ = (id) => document.getElementById(id);

  function fmtClock(ms) {
    return new Date(ms).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }
  function fmtDate(ms) {
    return new Date(ms).toLocaleDateString([], { weekday: "short", year: "numeric", month: "short", day: "numeric" });
  }

  function updatePanels(sky) {
    $("clock-date").textContent = fmtDate(state.simMs);
    $("clock-time").textContent = fmtClock(state.simMs);
    $("clock-jd").textContent = `JD ${sky.jd.toFixed(3)}`;
    const aya = sky.ayanamsa;
    $("clock-aya").textContent = `Ayanamsa ${Math.floor(aya)}\u00B0 ${String(Math.round((aya % 1) * 60)).padStart(2, "0")}\u2032`;

    const badge = $("mode-badge");
    if (state.mode === "live") {
      badge.textContent = "LIVE SKY";
      badge.className = "badge live";
    } else if (state.mode === "play") {
      badge.textContent = `\u25B6 ${SPEEDS[state.speedIndex].label}`;
      badge.className = "badge fast";
    } else {
      badge.textContent = "\u23F8 PAUSED";
      badge.className = "badge paused";
    }

    const tbody = $("legend-body");
    for (const g of GRAHAS) {
      const body = sky.bodies.find((b) => b.key === g.key);
      const node = g.key === "Rahu" ? sky.rahu : g.key === "Ketu" ? sky.ketu : null;
      const lonSid = node ? node.lonSidereal : body.lonSidereal;
      const sign = Ephemeris.wrap360(lonSid);
      const signInfo = (() => {
        const idx = Math.floor(sign / 30) % 12;
        const within = sign - idx * 30;
        const deg = Math.floor(within);
        const min = Math.floor((within - deg) * 60);
        return { glyph: Ephemeris.SIGNS[idx][2], sanskrit: Ephemeris.SIGNS[idx][1], label: `${deg}\u00B0${String(min).padStart(2, "0")}` };
      })();
      const nak = Ephemeris.NAKSHATRAS[Math.floor(sign / (360 / 27)) % 27];
      const retro = node || ((body.retrograde && g.key !== "Sun" && g.key !== "Moon"));

      let row = tbody.querySelector(`[data-key="${g.key}"]`);
      if (!row) {
        row = document.createElement("tr");
        row.dataset.key = g.key;
        row.innerHTML =
          `<td><span class="chip"></span><span class="glyph"></span></td>` +
          `<td><strong class="en"></strong><small class="sa"></small></td>` +
          `<td><span class="sign-glyph"></span> <span class="sign-name"></span></td>` +
          `<td class="deg"></td><td class="err"></td><td class="nak"></td><td class="retro"></td>`;
        tbody.appendChild(row);
      }
      row.querySelector(".chip").style.background = g.color;
      row.querySelector(".glyph").textContent = g.glyph;
      row.querySelector(".glyph").style.color = g.color;
      row.querySelector(".en").textContent = g.key;
      row.querySelector(".sa").textContent = g.name;
      row.querySelector(".sign-glyph").textContent = signInfo.glyph;
      row.querySelector(".sign-name").textContent = signInfo.sanskrit;
      row.querySelector(".deg").textContent = signInfo.label;
      row.querySelector(".err").textContent = `±${ERROR_ARCMIN[g.key] || "?"}`;
      row.querySelector(".nak").textContent = nak;
      row.querySelector(".retro").textContent = retro ? "R" : "";
    }
    updateCalStrip();
  }

  // ------------------------------------------------- remote record (Layer 0/5)

  function maybeFetchRemote() {
    const now = performance.now();
    const movedFar = Math.abs(state.simMs - state.lastFetchedMs) > 1_800_000; // 30 min
    if (now - state.lastFetchAt < 900 || (!movedFar && state.calendars && (state.drishtiChords || !state.drishtiOn))) return;
    state.lastFetchAt = now;
    state.lastFetchedMs = state.simMs;
    const ts = Math.round(state.simMs);
    fetch(`/api/v1/calendars?timestamp_ms_utc=${ts}`)
      .then((r) => r.json())
      .then((cal) => { state.calendars = cal; updateCalStrip(); })
      .catch(() => {});
    if (state.drishtiOn) {
      fetch(`/api/v1/sky?timestamp_ms_utc=${ts}`)
        .then((r) => r.json())
        .then((payload) => {
          const f = (payload.qanun.factors || []).find((x) => x.factor === "drishti");
          state.drishtiChords = f ? f.value : [];
        })
        .catch(() => {});
    }
  }

  function updateCalStrip() {
    const cal = state.calendars;
    if (!cal) return;
    $("cal-hijri").textContent = `${cal.hijri.day} ${cal.hijri.month_name} ${cal.hijri.year}`;
    $("cal-jalali").textContent = `${cal.jalali.day} ${cal.jalali.month_name} ${cal.jalali.year}`;
    $("cal-vikram").textContent = String(cal.vikram_samvat.year);
    $("cal-saka").textContent = `${cal.saka.day} ${cal.saka.month_name} ${cal.saka.year}`;
    $("cal-kali").textContent = String(Math.floor(cal.kali.ahargana_days));
  }

  // ------------------------------------------------------ Tafhīm mode (Layer 4)

  function openLesson(key) {
    const lesson = LESSONS[key];
    if (!lesson) return;
    $("lesson-title").textContent = key;
    $("lesson-q").textContent = lesson.q;
    $("lesson-body").innerHTML = "";
    const p = document.createElement("p");
    p.textContent = lesson[state.lang] || lesson.en;
    $("lesson-body").appendChild(p);
    const tier = document.createElement("p");
    tier.className = "lesson-tier";
    tier.innerHTML = `<span class="badge tier-measured">measured</span> <span class="badge tier-doctrine">doctrine</span> — <a href="/tribunal" style="color:var(--teal)">${I18N[state.lang].see_tribunal}</a>`;
    $("lesson-body").appendChild(tier);
    $("lesson").classList.add("open");
  }

  // ------------------------------------------------------ hilal (Amendment III)

  function fetchHilal() {
    const lat = parseFloat($("hilal-lat").value);
    const lon = parseFloat($("hilal-lon").value);
    const elev = parseFloat($("hilal-elev").value || "0");
    if (Number.isNaN(lat) || Number.isNaN(lon)) return;
    try { localStorage.setItem("ka-observatory", JSON.stringify({ lat, lon, elev })); } catch (e) { void e; }
    const out = $("hilal-out");
    out.textContent = "…";
    const ts = Math.round(state.simMs);
    fetch(`/api/v1/crescent?timestamp_ms_utc=${ts}&lat=${lat}&lon=${lon}&elev_m=${elev}`)
      .then((r) => r.json())
      .then((c) => {
        if (c.error) { out.textContent = c.error; return; }
        const s = c.at_sunset;
        const rows = [
          ["sunset", new Date(c.sunset_ms_utc).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })],
          ["moon alt", `${s.moon_alt_deg}°`],
          ["ARCL", `${s.elongation_arcl_deg}°`],
          ["illum", `${(s.illumination_fraction * 100).toFixed(2)}%`],
          ["age", `${s.moon_age_hours} h`],
          ["lag", c.moonset.lag_minutes === null ? "—" : `${c.moonset.lag_minutes} min`],
        ];
        out.innerHTML = rows.map(([k, v]) => `<div class="row"><small>${k}</small><strong>${v}</strong></div>`).join("") +
          `<div class="row"><small>Yallop q</small><strong>${c.yallop_q.q} · band ${c.yallop_q.band} <span class="badge tier-hypothesis">hypothesis</span></strong></div>`;
      })
      .catch((e) => { out.textContent = e.message; });
  }

  // ------------------------------------------------------------------------- i18n

  function applyI18n(lang) {
    state.lang = lang;
    const dict = I18N[lang] || I18N.en;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.dataset.i18n;
      if (dict[key]) el.innerHTML = dict[key];
    });
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    try { localStorage.setItem("ka-lang", lang); } catch (e) { void e; }
  }

  // ---------------------------------------------------------------- controls

  function setMode(mode) {
    if (mode === "live") state.trails.clear();
    state.mode = mode;
    syncControls();
  }

  function syncControls() {
    $("btn-play").textContent = state.mode === "paused" ? "\u25B6" : "\u23F8";
    $("btn-now").classList.toggle("active", state.mode === "live");
    if (state.mode === "paused") {
      $("datetime").value = toLocalInputValue(state.simMs);
    }
  }

  function toLocalInputValue(ms) {
    const dt = new Date(ms);
    const pad = (n, w = 2) => String(n).padStart(w, "0");
    return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
  }

  function wireControls() {
    const speedSel = $("speed");
    SPEEDS.forEach((s, i) => {
      const opt = document.createElement("option");
      opt.value = String(i);
      opt.textContent = s.label;
      speedSel.appendChild(opt);
    });
    speedSel.value = String(state.speedIndex);
    speedSel.addEventListener("change", () => {
      state.speedIndex = Number(speedSel.value);
      if (state.mode === "live") setMode("play");
    });

    $("btn-play").addEventListener("click", () => {
      if (state.mode === "paused") setMode("play");
      else setMode("paused");
    });

    $("btn-now").addEventListener("click", () => setMode("live"));

    $("datetime").addEventListener("change", () => {
      const v = $("datetime").value;
      if (!v) return;
      const picked = new Date(v).getTime();
      if (!Number.isNaN(picked)) {
        state.simMs = picked;
        setMode("paused");
      }
    });

    window.addEventListener("keydown", (ev) => {
      if (ev.target instanceof HTMLInputElement || ev.target instanceof HTMLSelectElement) return;
      if (ev.code === "Space") { ev.preventDefault(); $("btn-play").click(); }
      const dayShift = ev.code === "ArrowRight" ? 1 : ev.code === "ArrowLeft" ? -1 : 0;
      if (dayShift !== 0) {
        state.simMs += dayShift * 86400000;
        if (state.mode === "live") setMode("paused");
        else syncControls();
      }
    });
  }

  // ------------------------------------------------------------------- loop

  let lastTick = performance.now();
  function tick(now) {
    const dt = Math.min((now - lastTick) / 1000, 0.1);
    lastTick = now;

    if (state.mode === "live") {
      state.simMs = Date.now();
    } else if (state.mode === "play") {
      state.simMs += dt * 1000 * SPEEDS[state.speedIndex].f;
    }

    const sky = Ephemeris.computeSky(state.simMs);
    maybeFetchRemote();
    renderFrame(sky);
    updatePanels(sky);
    requestAnimationFrame(tick);
  }

  function init() {
    wireControls();
    layout();
    if (window.ResizeObserver) {
      new ResizeObserver(layout).observe(stageEl);
    } else {
      window.addEventListener("resize", layout);
    }
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      state.mode = "paused";
    }

    let savedLang = "en";
    try { savedLang = localStorage.getItem("ka-lang") || "en"; } catch (e) { void e; }
    $("lang").value = savedLang;
    applyI18n(savedLang);
    $("lang").addEventListener("change", () => applyI18n($("lang").value));

    $("btn-drishti").addEventListener("click", () => {
      state.drishtiOn = !state.drishtiOn;
      $("btn-drishti").classList.toggle("active", state.drishtiOn);
      if (state.drishtiOn && !state.drishtiChords) {
        state.lastFetchAt = 0; // force a fetch on the next frame
      }
    });

    $("legend-body").addEventListener("click", (ev) => {
      const row = ev.target.closest("tr[data-key]");
      if (row) openLesson(row.dataset.key);
    });
    $("lesson-close").addEventListener("click", () => $("lesson").classList.remove("open"));
    document.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape") $("lesson").classList.remove("open");
    });

    $("hilal-btn").addEventListener("click", fetchHilal);
    try {
      const saved = JSON.parse(localStorage.getItem("ka-observatory") || "null");
      if (saved) {
        $("hilal-lat").value = saved.lat;
        $("hilal-lon").value = saved.lon;
        $("hilal-elev").value = saved.elev;
      }
    } catch (e) { void e; }

    syncControls();
    requestAnimationFrame(tick);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
