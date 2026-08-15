/* sw.js -- Plexus offline.
 *
 * One page and its icon, cached on install, served cache-first. There is
 * nothing to fetch at runtime because there is no runtime: no API, no account,
 * no telemetry. A service worker for an app like this exists only so the
 * platform will let it be installed and opened without a network.
 */
var CACHE = "plexus-v1";
var FILES = ["./app.html", "./icon.svg", "./manifest.webmanifest"];

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

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  e.respondWith(caches.match(e.request).then(function (hit) {
    return hit || fetch(e.request);
  }));
});
