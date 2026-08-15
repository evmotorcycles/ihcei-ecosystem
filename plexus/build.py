#!/usr/bin/env python3
"""build.py -- render Plexus: one file to open, plus the files that make it
installable.

    python3 plexus/build.py

Writes:
    plexus/app.html               one self-contained file. Open it from a phone,
                                  a laptop, a USB stick. No server, no account,
                                  no network. Works in aeroplane mode.
    plexus/manifest.webmanifest   so a browser will offer "Add to Home Screen"
    plexus/sw.js                  so it keeps working once installed
    plexus/icon.svg               the icon, inline everywhere it is needed

BEING HONEST ABOUT "INSTALLABLE"
Opening app.html from a file gives the whole app, offline, on every platform.
Installing it to a home screen or dock needs the page served over https (or from
localhost) because that is what browsers require before they register a service
worker. That is a browser rule, not a limitation of this app, and there is no
version of the app that gets round it. Both paths are provided rather than
claiming one covers the other.

The engines inlined here are smi/lmd.js -- parity-checked against the JAX engine
over fourteen graphs -- and plexus/engines.js, parity-checked against spar/ and
fathom/ by plexus/test_plexus.py. The thing in your hand and the thing under test
are the same arithmetic.
"""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

ICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#0F1418"/>
<g fill="none" stroke-linecap="round">
<path d="M32 15 L18 34 M32 15 L46 34 M18 34 L32 50 M46 34 L32 50 M18 34 L46 34"
      stroke="#33434F" stroke-width="2.4"/>
<path d="M32 15 L18 34 M18 34 L32 50" stroke="#E2664B" stroke-width="3.4"/>
</g>
<g fill="#EDF3F7">
<circle cx="32" cy="15" r="4.6"/><circle cx="18" cy="34" r="4.6"/>
<circle cx="46" cy="34" r="4.6"/><circle cx="32" cy="50" r="4.6"/>
</g></svg>"""

MANIFEST = """{
  "name": "Plexus",
  "short_name": "Plexus",
  "description": "See what a thing is made of, what is holding it up, and what it rests on.",
  "start_url": "./app.html",
  "scope": "./",
  "display": "standalone",
  "orientation": "any",
  "background_color": "#0F1418",
  "theme_color": "#0F1418",
  "icons": [
    { "src": "./icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable" }
  ]
}
"""

SW = """/* sw.js -- Plexus offline.
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
"""

REGISTER = """
<script>
/* Registers only when the page is served (https or localhost). Opened straight
   from a file there is no service worker, and the app works anyway -- it is one
   file with everything already in it. */
if ("serviceWorker" in navigator && location.protocol.indexOf("http") === 0) {
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("sw.js").catch(function () {});
  });
}
</script>
"""


def main():
    tpl = open(os.path.join(HERE, "app_template.html"), encoding="utf-8").read()
    lmd = open(os.path.join(ROOT, "smi", "lmd.js"), encoding="utf-8").read()
    eng = open(os.path.join(HERE, "engines.js"), encoding="utf-8").read()
    icon_uri = "data:image/svg+xml;base64," + base64.b64encode(
        ICON.encode("utf-8")).decode("ascii")

    out = (tpl.replace("{{LMD}}", lmd)
              .replace("{{ENGINES}}", eng)
              .replace("{{ICON}}", icon_uri)
              .replace("</body>", REGISTER + "</body>"))
    assert "{{" not in out, "unfilled placeholder left in app.html"

    open(os.path.join(HERE, "app.html"), "w", encoding="utf-8").write(out)
    open(os.path.join(HERE, "manifest.webmanifest"), "w", encoding="utf-8").write(MANIFEST)
    open(os.path.join(HERE, "sw.js"), "w", encoding="utf-8").write(SW)
    open(os.path.join(HERE, "icon.svg"), "w", encoding="utf-8").write(ICON)

    print("wrote plexus/app.html            (%.1f KB) — open it anywhere, offline"
          % (len(out) / 1024))
    print("wrote plexus/manifest.webmanifest, sw.js, icon.svg — for install-to-home-screen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
