#!/usr/bin/env python3
"""build.py -- render Plexus: one file to open, plus the files that make it
installable.

    python3 plexus/build.py

Writes:
    plexus/index.html             the page a server serves. Identical bytes to
                                  app.html; a test asserts that.
    plexus/app.html               the same file under the name you double-click.
    plexus/manifest.webmanifest   so a browser will offer "Add to Home Screen"
    plexus/sw.js                  so it keeps working once installed
    plexus/vercel.json            static routing and the cache headers a PWA
                                  needs -- notably SHORT ones on the page, the
                                  worker and the manifest
    plexus/topology.html          the Elastic Topology Interface: the same
                                  structures drawn as space, where distance IS
                                  sqrt(bearing/strength). A skin over the same
                                  engines, checked by plexus/test_eti.py.
    plexus/icon.svg               the favicon
    plexus/icon-{192,512,180}.png real icons, because SVG is not enough

WHY PNG ICONS EXIST HERE
A data URI in the manifest is not a reliable icon. Chrome's install criteria
want a fetchable icon of at least 192x192, and iOS does not read manifest icons
AT ALL for Add to Home Screen -- it reads <link rel="apple-touch-icon">, and it
does not accept SVG there. An SVG-only, data-URI-only build installs on an
iPhone with a blank icon. The PNGs are rendered by plexus/make_icons.py.

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
  "id": "/",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "display_override": ["standalone", "minimal-ui"],
  "orientation": "any",
  "background_color": "#0F1418",
  "theme_color": "#0F1418",
  "categories": ["utilities", "productivity"],
  "icons": [
    { "src": "./icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "./icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "./icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" },
    { "src": "./icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any" }
  ]
}
"""

# connect-src 'self' in the CSP below is NOT optional, and the reason is worth
# keeping next to it: without it the service worker registers and then never
# activates. Its own caches.addAll() during install is a same-origin fetch,
# default-src 'none' blocks it, install rejects, and the site ships with offline
# silently not working while every page-level check still passes.
#
# That note used to live in the rendered JSON as a "_comment" key. Vercel
# validates vercel.json against a schema that forbids unknown properties in a
# header rule and REJECTS THE WHOLE DEPLOYMENT -- so the explanation of one
# deploy-breaking bug became a second one. It belongs here, in the generator,
# where it documents the config without being shipped as part of it. A test
# asserts the rendered file carries no key Vercel does not accept.
VERCEL = """{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/sw.js",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" },
        { "key": "Service-Worker-Allowed", "value": "/" }
      ]
    },
    {
      "source": "/manifest.webmanifest",
      "headers": [
        { "key": "Content-Type", "value": "application/manifest+json" },
        { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" }
      ]
    },
    {
      "source": "/(index.html)?",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" }
      ]
    },
    {
      "source": "/icon-(.*).png",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "no-referrer" },
        { "key": "Permissions-Policy",
          "value": "geolocation=(), camera=(), microphone=(), interest-cohort=()" },
        { "key": "Content-Security-Policy",
          "value": "default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; manifest-src 'self'; worker-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'" }
      ]
    }
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
/* Bump CACHE whenever a shipped file changes. The old cache is deleted on
 * activate, so a stale page cannot survive a deploy. */
var CACHE = "plexus-v5";
var FILES = ["./", "./index.html", "./topology.html", "./manifold.html",
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

    for name in ("app.html", "index.html"):
        open(os.path.join(HERE, name), "w", encoding="utf-8").write(out)

    # The topology view inlines a THIRD script, eti.js, on top of the same two
    # engines. It is a skin: every number it draws comes from those engines, and
    # test_eti.py checks them against the Python rather than trusting the view.
    eti = open(os.path.join(HERE, "eti.js"), encoding="utf-8").read()
    top = open(os.path.join(HERE, "topology_template.html"), encoding="utf-8").read()
    topo = (top.replace("{{LMD}}", lmd)
               .replace("{{ENGINES}}", eng)
               .replace("{{ETI}}", eti)
               .replace("{{ICON}}", icon_uri)
               .replace("</body>", REGISTER + "</body>"))
    assert "{{" not in topo, "unfilled placeholder left in topology.html"
    open(os.path.join(HERE, "topology.html"), "w", encoding="utf-8").write(topo)

    # The manifold inlines a fourth script on top of the same stack. Apps, AI and
    # data are nodes; intent raises coupling; the tested metric decides the space.
    man = open(os.path.join(HERE, "manifold.js"), encoding="utf-8").read()
    mtpl = open(os.path.join(HERE, "manifold_template.html"), encoding="utf-8").read()
    mani = (mtpl.replace("{{LMD}}", lmd)
                .replace("{{ENGINES}}", eng)
                .replace("{{ETI}}", eti)
                .replace("{{MANIFOLD}}", man)
                .replace("{{ICON}}", icon_uri)
                .replace("</body>", REGISTER + "</body>"))
    assert "{{" not in mani, "unfilled placeholder left in manifold.html"
    open(os.path.join(HERE, "manifold.html"), "w", encoding="utf-8").write(mani)
    open(os.path.join(HERE, "manifest.webmanifest"), "w", encoding="utf-8").write(MANIFEST)
    open(os.path.join(HERE, "sw.js"), "w", encoding="utf-8").write(SW)
    open(os.path.join(HERE, "vercel.json"), "w", encoding="utf-8").write(VERCEL)
    open(os.path.join(HERE, "icon.svg"), "w", encoding="utf-8").write(ICON)

    print("wrote plexus/index.html and app.html  (%.1f KB each, identical bytes)"
          % (len(out) / 1024))
    print("wrote topology.html                    (%.1f KB)" % (len(topo) / 1024))
    print("wrote manifold.html                    (%.1f KB)" % (len(mani) / 1024))
    print("wrote manifest.webmanifest, sw.js, vercel.json, icon.svg")
    missing = [f for f in ("icon-192.png", "icon-512.png", "icon-180.png")
               if not os.path.exists(os.path.join(HERE, f))]
    if missing:
        print("MISSING ICONS: " + ", ".join(missing) + " — run plexus/make_icons.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
