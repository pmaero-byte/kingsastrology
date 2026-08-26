/*
 * Kingsastrology — Spacetime Clock ephemeris.
 *
 * Visualization-grade geocentric astronomy, dependency-free:
 *   - Mercury..Saturn + Earth(E-M bary): JPL "approximate positions" Keplerian
 *     elements (Table 1, valid 1800-2050), heliocentric -> geocentric.
 *   - Moon: Schlyter's truncated lunar theory (~2 arcmin).
 *   - Rahu/Ketu: mean lunar node; Ketu = Rahu + 180 deg.
 *   - Sidereal longitudes via Lahiri (Chitrapaksha) ayanamsa approximation.
 *
 * Provenance contract (charter pillar II): this module feeds DISPLAY ONLY.
 * It makes no doctrinal claims; when the Phase-0 Swiss Ephemeris engine (A1)
 * lands it becomes the source of truth and this module is retired to fallback.
 */
"use strict";

const Ephemeris = (() => {
  const DEG = Math.PI / 180;

  // JPL approximate elements, epoch J2000, rates per Julian century.
  // [a(AU), e, I(deg), L(deg), longPeri(deg), longNode(deg)]
  const ELEMENTS = {
    Mercury: {
      el: [0.38709927, 0.20563593, 7.00497902, 252.2503235, 77.45779628, 48.33076593],
      rate: [0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081],
    },
    Venus: {
      el: [0.72333566, 0.00677672, 3.39467605, 181.9790995, 131.60246718, 76.67984255],
      rate: [0.0000039, -0.00004107, -0.0007889, 58517.81538729, 0.00268329, -0.27769418],
    },
    Earth: {
      el: [1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0],
      rate: [0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0],
    },
    Mars: {
      el: [1.52371034, 0.0933941, 1.84969142, -4.55343205, -23.94362959, 49.55953891],
      rate: [0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343],
    },
    Jupiter: {
      el: [5.202887, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909],
      rate: [-0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106],
    },
    Saturn: {
      el: [9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448],
      rate: [-0.0012506, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794],
    },
  };

  function wrap360(d) {
    return ((d % 360) + 360) % 360;
  }

  function wrapPi(r) {
    return ((r % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
  }

  function julianDay(msUtc) {
    return msUtc / 86400000 + 2440587.5;
  }

  function centuriesJ2000(jd) {
    return (jd - 2451545.0) / 36525;
  }

  // Solve Kepler's equation E - e sinE = M (radians), Newton iteration.
  function keplerE(M, e) {
    let E = M + e * Math.sin(M);
    for (let i = 0; i < 10; i += 1) {
      const dE = (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
      E -= dE;
      if (Math.abs(dE) < 1e-9) break;
    }
    return E;
  }

  // Heliocentric ecliptic rectangular coordinates (AU) for a JPL element set.
  function heliocentric(name, T) {
    const { el, rate } = ELEMENTS[name];
    const a = el[0] + rate[0] * T;
    const e = el[1] + rate[1] * T;
    const I = (el[2] + rate[2] * T) * DEG;
    const L = (el[3] + rate[3] * T) * DEG;
    const peri = (el[4] + rate[4] * T) * DEG;
    const node = (el[5] + rate[5] * T) * DEG;

    const argPeri = peri - node;
    const M = wrapPi(L - peri);
    const E = keplerE(M, e);

    const xp = a * (Math.cos(E) - e); // in orbital plane
    const yp = a * Math.sqrt(1 - e * e) * Math.sin(E);

    const cw = Math.cos(argPeri);
    const sw = Math.sin(argPeri);
    const cn = Math.cos(node);
    const sn = Math.sin(node);
    const ci = Math.cos(I);
    const si = Math.sin(I);

    return {
      x: (cw * cn - sw * sn * ci) * xp + (-sw * cn - cw * sn * ci) * yp,
      y: (cw * sn + sw * cn * ci) * xp + (-sw * sn + cw * cn * ci) * yp,
      z: sw * si * xp + cw * si * yp,
      a,
      e,
    };
  }

  function longitudeOf(vec) {
    return wrap360(Math.atan2(vec.y, vec.x) / DEG);
  }

  // Geocentric apparent-ish ecliptic longitude of a planet (tropical, J2000
  // ecliptic; light-time/aberration neglected at visualization tolerance).
  function planetLongitude(name, T) {
    const p = heliocentric(name, T);
    if (name === "Earth") return null;
    const earth = heliocentric("Earth", T);
    return {
      lonTropical: longitudeOf({ x: p.x - earth.x, y: p.y - earth.y }),
      distAU: Math.hypot(p.x - earth.x, p.y - earth.y, p.z - earth.z),
    };
  }

  // Sun geocentric = anti-Earth vector.
  function sunLongitude(T) {
    const earth = heliocentric("Earth", T);
    return { lonTropical: longitudeOf({ x: -earth.x, y: -earth.y }), distAU: Math.hypot(earth.x, earth.y, earth.z) };
  }

  /*
   * Moon: Schlyter truncated lunar theory. d = days since 1999-12-31 00:00 UT.
   * Returns tropical geocentric ecliptic longitude (deg) and distance (Earth radii).
   */
  function moon(d) {
    const rad = DEG;
    const N = wrap360(125.1228 - 0.0529538083 * d) * rad;
    const inc = 5.1454 * rad;
    const w = wrap360(318.0634 + 0.1643573223 * d) * rad;
    const a = 60.2666; // Earth radii
    const e = 0.0549;
    const Mm = wrapPi(wrap360(115.3654 + 13.0649929509 * d) * rad);
    const Ms = wrapPi(wrap360(356.047 + 0.9856002585 * d) * rad);

    const E0 = keplerE(Mm, e);
    const xv = a * (Math.cos(E0) - e);
    const yv = a * Math.sqrt(1 - e * e) * Math.sin(E0);
    const v = Math.atan2(yv, xv);
    const r = Math.hypot(xv, yv);

    const cw = Math.cos(w);
    const sw = Math.sin(w);
    const cn = Math.cos(N);
    const sn = Math.sin(N);
    const ci = Math.cos(inc);
    const si = Math.sin(inc);

    const xe = (cw * cn - sw * sn * ci) * xv + (-sw * cn - cw * sn * ci) * yv;
    const ye = (cw * sn + sw * cn * ci) * xv + (-sw * sn + cw * cn * ci) * yv;
    const ze = sw * si * xv + cw * si * yv;

    let lon = wrap360(Math.atan2(ye, xe) / rad);

    // Major perturbations (deg): evection, variation, yearly equation, ...
    const Lm = wrap360((Mm + w + N) / rad);
    const Ls = wrap360(Ms / rad + wrap360(282.9404 + 4.70935e-5 * d));
    const D = wrapPi((Lm - Ls) * rad);
    const F = wrapPi((Lm - wrap360(N / rad)) * rad);

    const pert =
      -1.274 * Math.sin(Mm - 2 * D) +
      0.658 * Math.sin(2 * D) -
      0.186 * Math.sin(Ms) -
      0.059 * Math.sin(2 * Mm - 2 * D) -
      0.057 * Math.sin(Mm - 2 * D + Ms) +
      0.053 * Math.sin(Mm + 2 * D) +
      0.046 * Math.sin(2 * D - Ms) +
      0.041 * Math.sin(Mm - Ms) -
      0.035 * Math.sin(D) -
      0.031 * Math.sin(Mm + Ms) -
      0.015 * Math.sin(2 * F - 2 * D) +
      0.011 * Math.sin(Mm - 4 * D);

    lon = wrap360(lon + pert);
    return { lonTropical: lon, distER: r };
  }

  // Mean ascending node of the Moon (Rahu), tropical, deg.
  function rahuLongitude(T) {
    return wrap360(
      125.04452 - 1934.136261 * T + 0.0020708 * T * T + (T * T * T) / 450000,
    );
  }

  // Lahiri (Chitrapaksha) ayanamsa approximation, deg. ~arcmin-level near 1950-2050.
  function ayanamsa(jd) {
    const yearsSince2000 = (jd - 2451545.0) / 365.25;
    return 23.85306 + 0.013966 * yearsSince2000;
  }

  const SIGNS = [
    ["Aries", "Mesha", "\u2648"],
    ["Taurus", "Vrishabha", "\u2649"],
    ["Gemini", "Mithuna", "\u264A"],
    ["Cancer", "Karka", "\u264B"],
    ["Leo", "Simha", "\u264C"],
    ["Virgo", "Kanya", "\u264D"],
    ["Libra", "Tula", "\u264E"],
    ["Scorpio", "Vrischika", "\u264F"],
    ["Sagittarius", "Dhanu", "\u2650"],
    ["Capricorn", "Makara", "\u2651"],
    ["Aquarius", "Kumbha", "\u2652"],
    ["Pisces", "Meena", "\u2653"],
  ];

  const NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
  ];

  function signOf(lonSidereal) {
    const idx = Math.floor(wrap360(lonSidereal) / 30) % 12;
    const within = wrap360(lonSidereal) - idx * 30;
    const deg = Math.floor(within);
    const min = Math.floor((within - deg) * 60);
    return {
      index: idx,
      name: SIGNS[idx][0],
      sanskrit: SIGNS[idx][1],
      glyph: SIGNS[idx][2],
      degree: within,
      label: `${deg}\u00B0 ${String(min).padStart(2, "0")}\u2032`,
    };
  }

  function nakshatraOf(lonSidereal) {
    const span = 360 / 27;
    return NAKSHATRAS[Math.floor(wrap360(lonSidereal) / span) % 27];
  }

  // Full sky snapshot at a UTC epoch (ms).
  function computeSky(msUtc) {
    const jd = julianDay(msUtc);
    const T = centuriesJ2000(jd);
    const d = jd - 2451543.5; // Schlyter day count

    const sun = sunLongitude(T);
    const moonPos = moon(d);
    const rahuTrop = rahuLongitude(T);
    const aya = ayanamsa(jd);

    const bodies = [];
    bodies.push({
      key: "Sun",
      lonTropical: sun.lonTropical,
      distAU: sun.distAU,
    });
    bodies.push({
      key: "Moon",
      lonTropical: moonPos.lonTropical,
      distAU: (moonPos.distER * 6371.0088) / 149597870.7,
    });
    for (const name of ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]) {
      const pos = planetLongitude(name, T);
      bodies.push({ key: name, lonTropical: pos.lonTropical, distAU: pos.distAU });
    }
    for (const body of bodies) {
      body.lonSidereal = wrap360(body.lonTropical - aya);
    }

    // Retrograde by finite difference on sidereal longitude (+/-12h).
    const epsMs = 43200000;
    const fwd = computeLongitudesOnly(msUtc + epsMs);
    const bwd = computeLongitudesOnly(msUtc - epsMs);
    for (const body of bodies) {
      const delta = fwd[body.key] - bwd[body.key];
      const wrapped = ((delta + 540) % 360) - 180;
      body.retrograde = wrapped < 0 && body.key !== "Sun" && body.key !== "Moon";
      body.sign = signOf(body.lonSidereal);
      body.nakshatra = nakshatraOf(body.lonSidereal);
    }

    return {
      jd,
      ayanamsa: aya,
      bodies,
      rahu: { lonTropical: rahuTrop, lonSidereal: wrap360(rahuTrop - aya) },
      ketu: { lonTropical: wrap360(rahuTrop + 180), lonSidereal: wrap360(rahuTrop + 180 - aya) },
      moonDistER: moonPos.distER,
    };

    function computeLongitudesOnly(epochMs) {
      const j = julianDay(epochMs);
      const t = centuriesJ2000(j);
      const dd = j - 2451543.5;
      const map = { Sun: sunLongitude(t).lonTropical, Moon: moon(dd).lonTropical };
      for (const name of ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]) {
        map[name] = planetLongitude(name, t).lonTropical;
      }
      return map;
    }
  }

  return Object.freeze({
    computeSky,
    julianDay,
    ayanamsa,
    SIGNS,
    NAKSHATRAS,
    wrap360,
  });
})();
