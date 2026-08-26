"""
Layer 0 — The Zīj (Sky Record): pure astronomy for the Kingsastrology backend.

Python port of backend/app/web/ephemeris.js (same constants, same algorithms),
so the served record and the visual clock agree to floating-point tolerance:

- Mercury..Saturn + Earth(E-M bary): JPL "approximate positions" Keplerian
  elements, epoch J2000, valid 1800-2050. Outside that window results are
  extrapolation and MUST be tiered accordingly (see zij.py).
- Moon: Schlyter truncated lunar theory (longitude ~0.4 deg worst vs PyEphem).
- Rahu/Ketu: mean lunar node.
- Sidereal: Lahiri (Chitrapaksha) ayanamsa approximation.

Every function here is deterministic and dependency-free. No doctrine lives in
this module — positions are [measured] by construction.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

DEG = math.pi / 180.0

# JPL approximate elements: [a(AU), e, I, L, longPeri, longNode], rates /century.
ELEMENTS: dict[str, tuple[list[float], list[float]]] = {
    "Mercury": (
        [0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593],
        [0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081],
    ),
    "Venus": (
        [0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255],
        [0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418],
    ),
    "Earth": (
        [1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0],
        [0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0],
    ),
    "Mars": (
        [1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891],
        [0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343],
    ),
    "Jupiter": (
        [5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909],
        [-0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106],
    ),
    "Saturn": (
        [9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448],
        [-0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794],
    ),
}

SIGNS = [
    ("Aries", "Mesha", "♈"), ("Taurus", "Vrishabha", "♉"), ("Gemini", "Mithuna", "♊"),
    ("Cancer", "Karka", "♋"), ("Leo", "Simha", "♌"), ("Virgo", "Kanya", "♍"),
    ("Libra", "Tula", "♎"), ("Scorpio", "Vrischika", "♏"), ("Sagittarius", "Dhanu", "♐"),
    ("Capricorn", "Makara", "♑"), ("Aquarius", "Kumbha", "♒"), ("Pisces", "Meena", "♓"),
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Validation constants (PyEphem cross-check, 2026-08-26 10:57 UT) — published
# error bars, not decoration. See docs/16-tafhim-protocol.md and the Tribunal.
VALIDATION_ARCMIN = {
    "Sun": 0.5, "Moon": 22.0, "Mercury": 0.6, "Venus": 0.6,
    "Mars": 0.5, "Jupiter": 1.2, "Saturn": 5.0, "Rahu": 3.0, "Ketu": 3.0,
}

# JPL element-set validity. Outside: tier drops from measured to extrapolated.
VALID_WINDOW_JD = (2378496.5, 2469806.5)  # 1800-01-01 .. 2050-01-01 (approx)


def wrap360(d: float) -> float:
    return d % 360.0


def julian_day(ms_utc: int) -> float:
    return ms_utc / 86400000.0 + 2440587.5


def ms_from_jd(jd: float) -> int:
    return round((jd - 2440587.5) * 86400000.0)


def centuries_j2000(jd: float) -> float:
    return (jd - 2451545.0) / 36525.0


def kepler_e(M: float, e: float) -> float:
    E = M + e * math.sin(M)
    for _ in range(10):
        dE = (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))
        E -= dE
        if abs(dE) < 1e-9:
            break
    return E


def _heliocentric(name: str, T: float) -> tuple[float, float, float, float, float]:
    el, rate = ELEMENTS[name]
    a = el[0] + rate[0] * T
    e = el[1] + rate[1] * T
    I = (el[2] + rate[2] * T) * DEG
    L = (el[3] + rate[3] * T) * DEG
    peri = (el[4] + rate[4] * T) * DEG
    node = (el[5] + rate[5] * T) * DEG

    arg_peri = peri - node
    M = (L - peri) % (2 * math.pi)
    E = kepler_e(M, e)
    xp = a * (math.cos(E) - e)
    yp = a * math.sqrt(1 - e * e) * math.sin(E)

    cw, sw = math.cos(arg_peri), math.sin(arg_peri)
    cn, sn = math.cos(node), math.sin(node)
    ci, si = math.cos(I), math.sin(I)

    x = (cw * cn - sw * sn * ci) * xp + (-sw * cn - cw * sn * ci) * yp
    y = (cw * sn + sw * cn * ci) * xp + (-sw * sn + cw * cn * ci) * yp
    z = sw * si * xp + cw * si * yp
    return x, y, z, a, e


def _lon_of(x: float, y: float) -> float:
    return wrap360(math.atan2(y, x) / DEG)


def _planet_tropical(name: str, T: float) -> tuple[float, float]:
    px, py, pz, _, _ = _heliocentric(name, T)
    ex, ey, ez, _, _ = _heliocentric("Earth", T)
    dx, dy, dz = px - ex, py - ey, pz - ez
    return _lon_of(dx, dy), math.sqrt(dx * dx + dy * dy + dz * dz)


def _sun_tropical(T: float) -> tuple[float, float]:
    ex, ey, ez, _, _ = _heliocentric("Earth", T)
    return _lon_of(-ex, -ey), math.sqrt(ex * ex + ey * ey + ez * ez)


def _moon(d: float) -> tuple[float, float, float]:
    """Schlyter truncated lunar theory. d = JD - 2451543.5.
    Returns (tropical longitude deg, latitude deg, distance Earth-radii)."""
    N = (125.1228 - 0.0529538083 * d) % 360.0
    inc = 5.1454
    w = (318.0634 + 0.1643573223 * d) % 360.0
    a = 60.2666
    e = 0.0549
    Mm = math.radians((115.3654 + 13.0649929509 * d) % 360.0)
    Ms = math.radians((356.0470 + 0.9856002585 * d) % 360.0)

    E = kepler_e(Mm, e)
    xv = a * (math.cos(E) - e)
    yv = a * math.sqrt(1 - e * e) * math.sin(E)
    v = math.atan2(yv, xv)
    r = math.hypot(xv, yv)

    N_r, w_r, i_r = math.radians(N), math.radians(w), math.radians(inc)
    cw, sw = math.cos(w_r), math.sin(w_r)
    cn, sn = math.cos(N_r), math.sin(N_r)
    ci, si = math.cos(i_r), math.sin(i_r)

    xe = (cw * cn - sw * sn * ci) * xv + (-sw * cn - cw * sn * ci) * yv
    ye = (cw * sn + sw * cn * ci) * xv + (-sw * sn + cw * cn * ci) * yv
    ze = sw * si * xv + cw * si * yv

    lon = math.degrees(math.atan2(ye, xe)) % 360.0
    lat = math.degrees(math.asin(max(-1.0, min(1.0, ze / r))))

    Lm = (math.degrees(Mm) + w + N) % 360.0
    Ls = (math.degrees(Ms) + (282.9404 + 4.70935e-5 * d)) % 360.0
    D = math.radians((Lm - Ls) % 360.0)
    F = math.radians((Lm - N) % 360.0)

    pert = (
        -1.274 * math.sin(Mm - 2 * D) + 0.658 * math.sin(2 * D)
        - 0.186 * math.sin(Ms) - 0.059 * math.sin(2 * Mm - 2 * D)
        - 0.057 * math.sin(Mm - 2 * D + Ms) + 0.053 * math.sin(Mm + 2 * D)
        + 0.046 * math.sin(2 * D - Ms) + 0.041 * math.sin(Mm - Ms)
        - 0.035 * math.sin(D) - 0.031 * math.sin(Mm + Ms)
        - 0.015 * math.sin(2 * F - 2 * D) + 0.011 * math.sin(Mm - 4 * D)
    )
    lon = (lon + pert) % 360.0
    return lon, lat, r


def rahu_tropical(T: float) -> float:
    return wrap360(125.04452 - 1934.136261 * T + 0.0020708 * T * T + T ** 3 / 450000.0)


def ayanamsa(jd: float) -> float:
    return 23.85306 + 0.013966 * ((jd - 2451545.0) / 365.25)


def sign_of(lon_sidereal: float) -> dict:
    lon = wrap360(lon_sidereal)
    idx = int(lon // 30) % 12
    within = lon - idx * 30
    deg = int(within)
    minutes = int((within - deg) * 60)
    en, sa, glyph = SIGNS[idx]
    return {
        "index": idx, "name": en, "sanskrit": sa, "glyph": glyph,
        "degree": round(within, 4),
        "label": f"{deg}° {minutes:02d}′",
    }


def nakshatra_of(lon_sidereal: float) -> str:
    return NAKSHATRAS[int(wrap360(lon_sidereal) / (360.0 / 27.0)) % 27]


@dataclass(frozen=True)
class SkyRow:
    jd: float
    ayanamsa: float
    bodies: dict[str, dict]  # name -> {lon_t, lon_s, dist_au, lat?, retro, err_arcmin}
    rahu_lon_s: float
    ketu_lon_s: float
    moon_dist_er: float

    def as_dict(self) -> dict:
        return {
            "jd": round(self.jd, 6),
            "ayanamsa": round(self.ayanamsa, 6),
            "bodies": self.bodies,
            "rahu_lon_s": round(self.rahu_lon_s, 6),
            "ketu_lon_s": round(self.ketu_lon_s, 6),
            "moon_dist_er": round(self.moon_dist_er, 4),
        }


def compute_sky(ms_utc: int) -> SkyRow:
    jd = julian_day(ms_utc)
    T = centuries_j2000(jd)
    d = jd - 2451543.5

    sun_t, sun_d = _sun_tropical(T)
    moon_t, moon_lat, moon_r = _moon(d)
    rahu_t = rahu_tropical(T)
    aya = ayanamsa(jd)

    trop = {"Sun": sun_t, "Moon": moon_t}
    dist = {"Sun": sun_d, "Moon": moon_r * 6371.0088 / 149597870.7}
    for name in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        lon_t, d_au = _planet_tropical(name, T)
        trop[name] = lon_t
        dist[name] = d_au

    # Retrograde by ±12h finite difference.
    fwd = _longitudes_only(ms_utc + 43200000)
    bwd = _longitudes_only(ms_utc - 43200000)

    bodies: dict[str, dict] = {}
    for name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        delta = (fwd[name] - bwd[name] + 540.0) % 360.0 - 180.0
        retro = delta < 0 and name not in ("Sun", "Moon")
        lon_s = wrap360(trop[name] - aya)
        bodies[name] = {
            "lon_t": round(trop[name], 6),
            "lon_s": round(lon_s, 6),
            "dist_au": round(dist[name], 8),
            "retro": retro,
            "err_arcmin": VALIDATION_ARCMIN[name],
            "sign": sign_of(lon_s),
            "nakshatra": nakshatra_of(lon_s),
        }
    rahu_s = wrap360(rahu_t - aya)
    ketu_s = wrap360(rahu_t + 180.0 - aya)
    bodies["Rahu"] = {
        "lon_t": round(rahu_t, 6), "lon_s": round(rahu_s, 6), "dist_au": None,
        "retro": True, "err_arcmin": VALIDATION_ARCMIN["Rahu"],
        "sign": sign_of(rahu_s), "nakshatra": nakshatra_of(rahu_s),
    }
    bodies["Ketu"] = {
        "lon_t": round(wrap360(rahu_t + 180.0), 6), "lon_s": round(ketu_s, 6), "dist_au": None,
        "retro": True, "err_arcmin": VALIDATION_ARCMIN["Ketu"],
        "sign": sign_of(ketu_s), "nakshatra": nakshatra_of(ketu_s),
    }

    return SkyRow(jd=jd, ayanamsa=aya, bodies=bodies,
                  rahu_lon_s=rahu_s, ketu_lon_s=ketu_s, moon_dist_er=moon_r)


def _longitudes_only(ms_utc: int) -> dict[str, float]:
    jd = julian_day(ms_utc)
    T = centuries_j2000(jd)
    d = jd - 2451543.5
    out = {"Sun": _sun_tropical(T)[0], "Moon": _moon(d)[0]}
    for name in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        out[name] = _planet_tropical(name, T)[0]
    return out


def fast_longitudes(ms_utc: int) -> dict[str, float]:
    """Public fast path for event scanning: tropical longitudes only
    (no retrograde finite-difference, no sign/nakshatra decoration)."""
    return _longitudes_only(ms_utc)


# --------------------------------------------------------------------------
# Topocentric observables (for the crescent module and observatory-grade entry).
# --------------------------------------------------------------------------

def moon_ecliptic(ms_utc: int) -> tuple[float, float, float]:
    """Geocentric tropical (lon, lat, distance Earth-radii) of the Moon."""
    return _moon(julian_day(ms_utc) - 2451543.5)


def sun_ecliptic(ms_utc: int) -> float:
    return _sun_tropical(centuries_j2000(julian_day(ms_utc)))[0]


def ecliptic_to_equatorial(lon_deg: float, lat_deg: float) -> tuple[float, float]:
    """Ecliptic (of-date approximation) -> equatorial RA/dec. Obliquity 23.4367°."""
    eps = 23.4367 * DEG
    lon, lat = lon_deg * DEG, lat_deg * DEG
    ra = math.atan2(
        math.sin(lon) * math.cos(eps) - math.tan(lat) * math.sin(eps),
        math.cos(lon),
    )
    dec = math.asin(max(-1.0, min(1.0, math.sin(lat) * math.cos(eps) + math.cos(lat) * math.sin(eps) * math.sin(lon))))
    return wrap360(math.degrees(ra)), math.degrees(dec)


def gmst_deg(jd: float) -> float:
    T = centuries_j2000(jd)
    g = wrap360(280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T * T - T ** 3 / 38710000.0)
    return g


def altaz(ra_deg: float, dec_deg: float, jd: float, lat_deg: float, lon_deg: float) -> tuple[float, float]:
    """Top-of-atmosphere altitude/azimuth for an observer. Azimuth from North, East-positive."""
    lst = wrap360(gmst_deg(jd) + lon_deg)
    ha = math.radians((lst - ra_deg + 180.0) % 360.0 - 180.0)
    dec, lat = dec_deg * DEG, lat_deg * DEG
    sin_alt = math.sin(dec) * math.sin(lat) + math.cos(dec) * math.cos(lat) * math.cos(ha)
    alt = math.asin(max(-1.0, min(1.0, sin_alt)))
    az = math.atan2(
        -math.sin(ha),
        math.cos(dec) * math.tan(lat) - math.sin(dec) * math.cos(ha),
    )
    return math.degrees(alt), wrap360(math.degrees(az) + 180.0)


def topocentric_alt(alt_deg: float, dist_er: float) -> float:
    """Dip of altitude due to lunar/solar parallax (simple flat-parallax form)."""
    parallax_deg = math.degrees(math.asin(6378.14 / (dist_er * 6371.0088)))
    return alt_deg - parallax_deg * math.cos(alt_deg * DEG)


def refraction_corrected(alt_deg: float) -> float:
    """Bennett's refraction formula, deg. Valid near/above the horizon."""
    if alt_deg < -2.0:
        return alt_deg
    h = alt_deg + 7.31 / (alt_deg + 4.4)
    return alt_deg + (0.97 / math.tan(math.radians(h))) / 60.0


def find_event(
    ms_start: int, ms_end: int, altitude_fn, target_alt: float, rising: bool,
) -> int | None:
    """Bisection search for the moment altitude_fn(ms) crosses target_alt."""
    lo, hi = ms_start, ms_end
    f_lo = altitude_fn(lo) - target_alt
    f_hi = altitude_fn(hi) - target_alt
    if f_lo * f_hi > 0:
        return None
    for _ in range(40):
        mid = (lo + hi) // 2
        f_mid = altitude_fn(mid) - target_alt
        if f_lo * f_mid <= 0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid
        if hi - lo < 2000:
            break
    return (lo + hi) // 2
