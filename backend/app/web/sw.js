/* Kingsastrology service worker — offline pack for Today + Spacetime Clock.
   Caches the shell on install, keeps the zīj/sky APIs fresh on every online visit.
   Offline fallback: the last cached shell still renders with the engine's
   local ephemeris (visual clock + tithi/nakshatra not dependent on network). */

const CACHE = "kings-pwa-1";
const SHELL = [
  "/today",
  "/clock",
  "/tribunal",
  "/manifest.json",
  "/assets/today.html",
  "/assets/today.css",
  "/assets/today.js",
  "/assets/clock.html",
  "/assets/clock.css",
  "/assets/clock.js",
  "/assets/ephemeris.js",
  "/assets/tribunal.html",
];

self.addEventListener("install", (ev) => {
  self.skipWaiting();
  ev.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL).catch(() => {})));
});

self.addEventListener("activate", (ev) => {
  ev.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (ev) => {
  const url = new URL(ev.request.url);
  const isApi = url.pathname.startsWith("/api/");

  if (isApi) {
    // Network-first for API: fresh sky truth, cached fallback.
    ev.respondWith(
      fetch(ev.request)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(ev.request, copy));
          return res;
        })
        .catch(() => caches.match(ev.request))
    );
    return;
  }

  // Shell + assets: cache-first, network updates cache in background.
  ev.respondWith(
    caches.match(ev.request).then((hit) => {
      if (hit) {
        ev.waitUntil(fetch(ev.request).then((res) => {
          if (res.ok) caches.open(CACHE).then((c) => c.put(ev.request, res));
        }).catch(() => {}));
        return hit;
      }
      return fetch(ev.request).then((res) => {
        if (res.ok) caches.open(CACHE).then((c) => c.put(ev.request, res.clone()));
        return res;
      });
    })
  );
});
