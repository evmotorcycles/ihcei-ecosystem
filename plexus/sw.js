/* sw.js -- Plexus offline.
 *
 * One page and its icon, cached on install, served cache-first. There is
 * nothing to fetch at runtime because there is no runtime: no API, no account,
 * no telemetry. A service worker for an app like this exists only so the
 * platform will let it be installed and opened without a network.
 */
/* Bump CACHE whenever a shipped file changes. The old cache is deleted on
 * activate, so a stale page cannot survive a deploy. */
var CACHE = "plexus-v12";
var FILES = ["./", "./index.html", "./topology.html", "./manifold.html",
             "./flint.html", "./commons.html", "./gate.html", "./packs.html", "./press.html", "./metaphor.html", "./intercept.html",
             "./manifest.webmanifest", "./icon.svg",
             "./icon-192.png", "./icon-512.png", "./icon-180.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); })
    .then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; })
      .map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

/* Cache first, because there is nothing to be fresh about: no API, no account,
 * no telemetry. A navigation that misses the cache falls back to the page
 * itself, so a deep link opened offline still lands somewhere real rather than
 * on the browser's dinosaur. */
self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  var url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(function (hit) {
      if (hit) return hit;
      return fetch(e.request).catch(function () {
        return e.request.mode === "navigate"
          ? caches.match("./index.html") : Response.error();
      });
    })
  );
});
