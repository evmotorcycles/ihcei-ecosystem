#!/usr/bin/env python3
"""make_icons.py -- render the PNG icons a real install needs.

    python3 plexus/make_icons.py [path-to-chrome]

Why PNGs at all, when the app already has an SVG:

  * Chrome's install criteria want a fetchable icon of at least 192x192. A data
    URI in the manifest is not reliably honoured.
  * iOS does not read manifest icons for Add to Home Screen. It reads
    <link rel="apple-touch-icon">, and it does not accept SVG there. An
    SVG-only build installs on an iPhone with a blank icon.

Rendered with the headless browser rather than a raster library so the build
needs nothing beyond what is already here. The icon is drawn FULL BLEED with the
mark inside the middle 60%, so a platform that crops to a circle or a squircle
cuts only background.
"""
import base64
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SIZES = (192, 512, 180)

PAGE = """<!doctype html><meta charset="utf-8">
<style>html,body{margin:0;padding:0;width:100%;height:100%;
background:#0F1418;overflow:hidden}svg{display:block;width:100%;height:100%}</style>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"
     preserveAspectRatio="xMidYMid meet">
<rect x="0" y="0" width="64" height="64" fill="#0F1418"/>
<g fill="none" stroke-linecap="round">
<path d="M32 19 L21 33 M32 19 L43 33 M21 33 L32 47 M43 33 L32 47 M21 33 L43 33"
      stroke="#33434F" stroke-width="2.2"/>
<path d="M32 19 L21 33 M21 33 L32 47" stroke="#E2664B" stroke-width="3.2"/>
</g>
<g fill="#EDF3F7">
<circle cx="32" cy="19" r="4.1"/><circle cx="21" cy="33" r="4.1"/>
<circle cx="43" cy="33" r="4.1"/><circle cx="32" cy="47" r="4.1"/>
</g></svg>
"""

CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "google-chrome", "chromium", "chromium-browser",
]


def find_chrome(argv):
    if len(argv) > 1:
        return argv[1]
    for c in CANDIDATES:
        p = c if os.path.isabs(c) else shutil.which(c)
        if p and os.path.exists(p):
            return p
    raise SystemExit("no chrome found; pass the path as an argument")


def png_size(path):
    with open(path, "rb") as fh:
        return struct.unpack(">II", fh.read(24)[16:24])


def main(argv):
    chrome = find_chrome(argv)
    tmp = tempfile.mkdtemp(prefix="plexus-icons-")
    page = os.path.join(tmp, "icon.html")
    open(page, "w", encoding="utf-8").write(PAGE)

    # Driven over the devtools protocol rather than with --screenshot: the flag
    # captures before layout settles on small viewports and silently writes a
    # blank square. That happened at 192x192 and the file looked fine (537
    # bytes, correct dimensions) until it was opened.
    port = 9455
    proc = subprocess.Popen(
        [chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
         "--remote-debugging-port=%d" % port, "--hide-scrollbars", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        target = None
        for _ in range(80):
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port,
                                            timeout=1) as r:
                    tabs = json.load(r)
                target = next((t for t in tabs if t.get("type") == "page"), None)
                if target:
                    break
            except Exception:
                pass
            time.sleep(0.25)
        if not target:
            raise SystemExit("the browser never came up")

        import http.client
        ws = target["webSocketDebuggerUrl"]
        del http.client, ws
        # A websocket client is not in the standard library, so the capture is
        # done by re-launching per size with a virtual time budget instead --
        # slower, dependency-free, and it waits.
    finally:
        proc.terminate()

    for n in SIZES:
        out = os.path.join(HERE, "icon-%d.png" % n)
        subprocess.run(
            [chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
             "--hide-scrollbars", "--force-device-scale-factor=1",
             "--virtual-time-budget=4000", "--run-all-compositor-stages-before-draw",
             "--screenshot=" + out, "--window-size=%d,%d" % (n, n),
             "file://" + page],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        if not os.path.exists(out):
            raise SystemExit("chrome wrote no file for %dx%d" % (n, n))
        w, h = png_size(out)
        blank = os.path.getsize(out) < 1000
        print("  icon-%d.png  %dx%d  %d bytes%s"
              % (n, w, h, os.path.getsize(out), "   BLANK — REJECTED" if blank else ""))
        if (w, h) != (n, n) or blank:
            raise SystemExit(
                "icon-%d.png did not render. A blank icon has the right "
                "dimensions and the wrong content, so this check is on bytes "
                "as well as size." % n)
    shutil.rmtree(tmp, ignore_errors=True)
    print("  all icons rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
