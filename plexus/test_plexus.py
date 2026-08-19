#!/usr/bin/env python3
"""Plexus ships JavaScript. The JavaScript must agree with the Python.

    python3 -m pytest -q plexus/test_plexus.py

Plexus puts SPAR and FATHOM in a browser so they run on a phone with no server.
A port nobody checks drifts, and then the thing under test and the thing people
touch stop being the same thing. Both engines are run over the same structures
and any disagreement fails.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from fathom.fathom import Claim, sound  # noqa: E402
from spar.spar import Structure, bearings, single_points  # noqa: E402

TOL = 1e-9

STRUCTURES = [
    ("triangle", ["a", "b", "c"], [("a", "b", 1.0), ("b", "c", 1.0), ("a", "c", 1.0)]),
    ("path", ["a", "b", "c", "d"], [("a", "b", 1.0), ("b", "c", 1.0), ("c", "d", 1.0)]),
    ("kite", ["a", "b", "c", "d"],
     [("a", "b", 1.0), ("b", "c", 1.0), ("a", "c", 1.0), ("c", "d", 1.0)]),
    ("weighted", ["w", "x", "y", "z"],
     [("w", "x", 3.7), ("x", "y", 0.4), ("y", "z", 9.1), ("w", "z", 2.2)]),
    ("wide weights", ["p", "q", "r", "s"],
     [("p", "q", 1e-3), ("q", "r", 1e3), ("p", "r", 1.0), ("r", "s", 5.0)]),
    ("two pieces", ["a", "b", "c", "d", "e"],
     [("a", "b", 1.0), ("b", "c", 2.0), ("d", "e", 5.0)]),
    ("hub", ["hub", "a", "b", "c"],
     [("hub", "a", 1.0), ("hub", "b", 1.0), ("hub", "c", 1.0)]),
    ("the energy bill", ["Meter reading", "Unit rate", "Standing charge", "Subtotal",
                         "VAT", "Late fee", "Amount due"],
     [("Meter reading", "Subtotal", 8.0), ("Unit rate", "Subtotal", 8.0),
      ("Standing charge", "Subtotal", 3.0), ("Subtotal", "VAT", 6.0),
      ("Subtotal", "Amount due", 6.0), ("VAT", "Amount due", 6.0),
      ("Late fee", "Amount due", 0.4)]),
    ("a water bill",
     ["Previous reading", "Present reading", "Units used", "Water tariff",
      "Water charge", "Sewerage charge", "Service fee", "Arrears", "VAT", "Amount due"],
     [("Previous reading", "Units used", 8.0), ("Present reading", "Units used", 8.0),
      ("Units used", "Water charge", 9.0), ("Water tariff", "Water charge", 9.0),
      ("Water charge", "Sewerage charge", 5.0), ("Water charge", "VAT", 6.0),
      ("Sewerage charge", "VAT", 4.0), ("Water charge", "Amount due", 7.0),
      ("Sewerage charge", "Amount due", 5.0), ("Service fee", "Amount due", 3.0),
      ("Arrears", "Amount due", 2.0), ("VAT", "Amount due", 6.0)]),
]

CLAIMS = [
    ("shared origin", "The claim", ["Origin"],
     [("The claim", "A", 1.0), ("The claim", "B", 1.0),
      ("A", "Origin", 1.0), ("B", "Origin", 1.0)]),
    ("separate sources", "The claim", ["S1", "S2"],
     [("The claim", "A", 1.0), ("The claim", "B", 1.0),
      ("A", "S1", 1.0), ("B", "S2", 1.0)]),
    ("lopsided", "The claim", ["Study", "Blog"],
     [("The claim", "Study", 9.0), ("The claim", "Blog", 0.2)]),
    ("long names that share a prefix", "The result",
     ["Source alpha", "Source alpha two"],
     [("The result", "Source alpha", 2.0), ("The result", "Source alpha two", 2.0)]),
    ("the water bill", "Amount due",
     ["Previous reading", "Present reading", "Water tariff"],
     [("Previous reading", "Units used", 8.0), ("Present reading", "Units used", 8.0),
      ("Units used", "Water charge", 9.0), ("Water tariff", "Water charge", 9.0),
      ("Water charge", "Sewerage charge", 5.0), ("Water charge", "VAT", 6.0),
      ("Sewerage charge", "VAT", 4.0), ("Water charge", "Amount due", 7.0),
      ("Sewerage charge", "Amount due", 5.0), ("Service fee", "Amount due", 3.0),
      ("Arrears", "Amount due", 2.0), ("VAT", "Amount due", 6.0)]),
]


@pytest.fixture(scope="module")
def js():
    script = os.path.join(HERE, "parity_dump.mjs")
    try:
        out = subprocess.run(["node", script], capture_output=True, text=True, timeout=180)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


@pytest.mark.parametrize("i", range(len(STRUCTURES)))
def test_bearings_agree(js, i):
    name, parts, links = STRUCTURES[i]
    py = bearings(Structure(parts, links))
    got = js["bearings"][i]
    assert got["name"] == name
    assert abs(py["total"] - got["total"]) < TOL, f"{name}: totals differ"
    assert py["pieces"] == got["pieces"], f"{name}: piece counts differ"
    pym = {(min(r["from"], r["to"]), max(r["from"], r["to"])): r["bearing"]
           for r in py["links"]}
    jsm = {(min(r["from"], r["to"]), max(r["from"], r["to"])): r["bearing"]
           for r in got["links"]}
    assert set(pym) == set(jsm), f"{name}: different links"
    worst = max(abs(pym[k] - jsm[k]) for k in pym)
    assert worst < TOL, f"{name}: worst bearing disagreement {worst:.3e}"


@pytest.mark.parametrize("i", range(len(STRUCTURES)))
def test_single_points_agree(js, i):
    name, parts, links = STRUCTURES[i]
    py = sorted(x["part"] for x in single_points(Structure(parts, links)))
    got = sorted(x["part"] for x in js["singlePoints"][i]["parts"])
    assert py == got, f"{name}: the engines disagree about which parts everything passes through"


@pytest.mark.parametrize("i", range(len(CLAIMS)))
def test_soundings_agree(js, i):
    name, conclusion, sources, links = CLAIMS[i]
    py = sound(Claim(conclusion, sources, links))
    got = js["soundings"][i]
    assert got["name"] == name
    assert abs(py["deepest_dependence"] - got["deepest"]) < TOL, \
        f"{name}: deepest dependence differs"
    pym = {r["source"]: r["dependence"] for r in py["by_source"]}
    jsm = {r["source"]: r["dependence"] for r in got["bySource"]}
    assert set(pym) == set(jsm)
    worst = max(abs(pym[k] - jsm[k]) for k in pym)
    assert worst < TOL, f"{name}: worst dependence disagreement {worst:.3e}"


def test_the_names_that_share_a_prefix_are_really_a_hazard():
    """The browser port contracts source nodes and has to key pairs somehow. An
    early version joined names into a string and split it back per CHARACTER,
    which only worked for one-character names. This case would have caught it,
    so it must actually be in the parity set and must actually be tricky."""
    name, conclusion, sources, _ = CLAIMS[3]
    assert sources[0] in sources[1], "the two source names must share a prefix"
    assert len({s.replace(" ", "") for s in sources}) == 2


def test_the_shipped_page_carries_no_control_characters():
    """A literal NUL in the source works and is a hazard: grep calls the file
    binary, formatters strip it, and the separator silently becomes the empty
    string -- which merges different pairs onto one key."""
    for rel in ("app.html", "index.html", "engines.js", "app_template.html",
                "eti.js", "topology.html", "topology_template.html",
                "commons.js", "library.js", "commons.html",
                "commons_template.html", "commons_dump.mjs",
                "lens.js", "gate.js", "gate.html", "gate_template.html",
                "gate_dump.mjs", "packs.js", "packlib.js", "packs.html",
                "packs_template.html", "packs_dump.mjs"):
        raw = open(os.path.join(HERE, rel), "rb").read()
        assert b"\x00" not in raw, f"{rel} contains a literal NUL"


# ---------------------------------------------------------------------------
# RETIRED: test_the_page_reaches_no_network
#
# It banned fetch(, XMLHttpRequest, WebSocket and https:// anywhere in the
# shipped page. That made the app offline by CONSTRUCTION, which was correct
# while the app was offline by intent. The decision has been taken to make
# these tools hybrid -- offline first, sync as an addition -- and a blanket ban
# cannot express that. Retired deliberately, in the open, rather than deleted
# quietly when it first got in the way.
#
# It is replaced by two invariants that are STRICTER where it matters:
#
#   1. the measuring kernel can never reach the network, at all, forever;
#   2. the promise printed on a page must match what that page's code does,
#      so the copy cannot keep saying "nothing leaves this device" one commit
#      after something starts leaving.
#
# Third-party origins remain blocked by connect-src 'self', which has its own
# test and is not affected by this retirement.
# ---------------------------------------------------------------------------

KERNEL = ("engines.js", "eti.js", "manifold.js", "nere.js", "ihcei.js",
          "cairn.js", "game.js", "vault.js", "commons.js", "library.js",
          "lens.js", "gate.js", "packs.js", "packlib.js")


def test_the_measuring_kernel_can_never_reach_the_network():
    """The arithmetic stays on the device even after the apps go hybrid.

    Sync may come and go; a measurement must never depend on a server being
    reachable, or the answer a person gets about their own bill becomes
    something someone else can withhold. This is the line the hybrid work is
    not allowed to cross, so it is asserted over the engines themselves rather
    than over the pages that host them.
    """
    import re
    for name in KERNEL:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            continue
        src = open(path, encoding="utf-8").read()
        hit = re.search(r"\bfetch\s*\(|XMLHttpRequest|new\s+WebSocket|"
                        r"navigator\.sendBeacon|EventSource", src)
        assert not hit, f"{name} reaches the network: {hit.group(0)}"
    lmd = open(os.path.join(ROOT, "smi", "lmd.js"), encoding="utf-8").read()
    assert "fetch(" not in lmd and "XMLHttpRequest" not in lmd


def test_the_promise_on_a_page_matches_what_that_page_does():
    """Truthfulness as an invariant rather than a fixed string.

    The old test kept the page honest by forbidding the network. This keeps it
    honest by forbidding the CONTRADICTION: a page may reach out, or it may
    promise that nothing leaves this device, and it may not do both. When sync
    lands, this fails until the copy is rewritten in the same commit.
    """
    import re
    pages = [f for f in os.listdir(HERE)
             if f.endswith(".html") and not f.endswith("_template.html")]
    assert pages, "no built pages found"
    for f in pages:
        src = open(os.path.join(HERE, f), encoding="utf-8").read()
        reaches = re.search(r"\bfetch\s*\(|XMLHttpRequest|new\s+WebSocket|"
                            r"navigator\.sendBeacon", src)
        promises = ("Nothing leaves this device" in src
                    or "aeroplane mode" in src
                    or "no network, no server" in src)
        assert not (reaches and promises), (
            f"{f} reaches the network ({reaches.group(0)}) while still promising "
            "that nothing leaves this device -- change the copy in the same commit")


def test_the_page_still_works_with_the_network_gone():
    """Offline first is the default, not a fallback. The service worker must be
    registered and the page must be cached, or 'hybrid' quietly becomes
    'online, degrading badly'."""
    src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
    assert "navigator.serviceWorker.register" in src, \
        "without this it cannot be installed or opened without a network"
    sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read()
    assert "./index.html" in sw and 'caches.match("./index.html")' in sw


def test_the_page_states_what_it_cannot_tell_you():
    src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
    assert "Whether a step is <em>useful</em>" in src
    assert "only knows the parts you entered" in src
    assert "Nothing leaves this device" in src


def test_every_script_is_inline_because_the_csp_forbids_external_ones():
    """A near miss, caught before it shipped.

    The CSP is script-src 'unsafe-inline' with NO 'self'. That permits inline
    <script> blocks and forbids <script src="...">, same origin included. A
    build that splits the engines out into lmd.js and engines.js and links them
    serves a page whose scripts are all blocked: LMD and PLEXUS never define,
    nothing draws, and the HTML itself still returns 200 with the right bytes.
    It looks like a working deploy and is a blank screen.

    That is why index.html is 65 KB rather than 30 KB. The size is the point:
    everything the page needs is inside the file the CSP already trusts.
    """
    import re
    src = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    external = re.search(r"<script[^>]+\bsrc\s*=", src)
    assert not external, "an external script cannot load under this CSP"

    csp = None
    for rule in _vercel()["headers"]:
        for h in rule["headers"]:
            if h["key"] == "Content-Security-Policy":
                csp = h["value"]
    assert "script-src 'unsafe-inline'" in csp
    assert "script-src 'self'" not in csp, \
        "if this ever gains 'self', the inlining rule above stops being load-bearing"


def test_a_person_can_put_in_their_own_structure():
    """The examples exist to show what the three questions mean. Without this
    the app is a demo: someone holding a bill it does not already know about
    has nothing to do with it."""
    src = open(os.path.join(HERE, "app_template.html"), encoding="utf-8").read()
    for hook in ('id="v-own"', 'id="own-name"', 'id="own-part"', 'id="own-add"',
                 'id="own-result"', 'id="own-sources"', 'id="own-from"',
                 'id="own-to"', 'id="own-link"', 'id="own-use"', 'id="own-clear"',
                 'id="own-err"', 'id="own-saved"'):
        assert hook in src, f"the editor is missing {hook}"
    assert "+ Your own" in src, "there is no way to reach the editor"
    assert "A part cannot be worked out from itself" in src, "self-links are not rejected"
    assert "There is already a part called" in src, "duplicate names are not rejected"


def test_marking_a_source_does_not_destroy_the_button_that_was_pressed():
    """Found by driving the built page; invisible with a mouse.

    Toggling a source re-rendered the whole row with innerHTML, which replaces
    the very button just pressed. Keyboard focus drops to the top of the page on
    every toggle, and a driven run marked only the FIRST of two sources because
    the rest of the list had been detached from the document mid-loop. In an app
    whose controls carry a 44px floor for unsteady hands, throwing focus away on
    every tap is the same defect wearing different clothes. Flipped in place now.
    """
    src = open(os.path.join(HERE, "app_template.html"), encoding="utf-8").read()
    i = src.index('$("#own-sources").addEventListener')
    body = src[i:src.index("});", i)]
    assert 'b.setAttribute("aria-pressed"' in body, "the flag is not flipped in place"
    assert "drawEditor()" not in body, \
        "re-rendering the row destroys the button that was pressed"


def test_what_a_person_types_stays_on_their_device():
    """Same promise as the rest of the app, now that there is something worth
    keeping. A private-mode browser THROWS on localStorage rather than returning
    null, so unguarded access would break the editor for the people most likely
    to care about where their bill goes."""
    src = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
    assert '"plexus.own.v1"' in src
    assert "localStorage" in src
    assert "catch (err) { return []; }" in src, "private mode would throw uncaught"
    assert "will be gone when the tab closes" in src, \
        "a failed save must be said out loud, not swallowed"


def test_every_control_is_at_least_44px():
    """Measured in a real browser by plexus/drive.js; this pins the CSS that
    made it true, because the two header chips shipped at 36px."""
    src = open(os.path.join(HERE, "app_template.html"), encoding="utf-8").read()
    assert "min-height:44px" in src, "the header chips lost their 44px floor"
    for rule in ("min-height:46px", "min-height:48px"):
        assert rule in src


# ------------------------------------------------------------- the PWA files --
def _manifest():
    return json.load(open(os.path.join(HERE, "manifest.webmanifest"), encoding="utf-8"))


def _vercel():
    return json.load(open(os.path.join(HERE, "vercel.json"), encoding="utf-8"))


def test_index_and_app_are_the_same_bytes():
    """One is what a server serves, the other is what you double-click. If they
    drift, the tested page and the shipped page stop being the same page."""
    a = open(os.path.join(HERE, "index.html"), "rb").read()
    b = open(os.path.join(HERE, "app.html"), "rb").read()
    assert a == b and len(a) > 40000


def test_the_csp_allows_the_service_worker_to_install():
    """The one that would have shipped broken.

    With default-src 'none' and no connect-src, the worker REGISTERS and then
    never activates: caches.addAll() during install is a same-origin fetch, the
    policy blocks it, install rejects, and the registration is discarded. Driven
    in a browser: registration returned OK, the cache existed with 0 entries,
    and an offline reload landed on the browser's error page -- while every
    page-level check still passed.
    """
    csp = None
    for rule in _vercel()["headers"]:
        for h in rule["headers"]:
            if h["key"] == "Content-Security-Policy":
                csp = h["value"]
    assert csp, "no Content-Security-Policy is declared"
    assert "connect-src 'self'" in csp, \
        "without connect-src the worker installs and never activates"
    assert "worker-src 'self'" in csp
    assert "default-src 'none'" in csp


def test_vercel_json_carries_no_key_vercel_will_reject():
    """The one that DID ship broken, and blocked the deploy.

    A header rule carried a "_comment" key explaining why connect-src is
    load-bearing. Vercel validates vercel.json against a schema that forbids
    unknown properties in a rule and rejects the ENTIRE deployment -- so the
    note documenting one deploy-breaking bug became a second one, and it was
    invisible until something actually tried to deploy. The explanation now
    lives in build.py, where it documents the config without being part of it.

    Every check here passed while this file could not be deployed at all: the
    JSON parsed, the CSP was right, the cache headers were right. Valid JSON is
    not the same as a config the platform accepts.
    """
    cfg = _vercel()
    top_ok = {"$schema", "cleanUrls", "trailingSlash", "headers", "redirects",
              "rewrites", "routes", "regions", "framework", "buildCommand",
              "outputDirectory", "installCommand", "public", "crons", "images"}
    assert set(cfg) <= top_ok, "Vercel rejects top-level: %s" % sorted(set(cfg) - top_ok)
    rule_ok = {"source", "headers", "has", "missing"}
    for rule in cfg["headers"]:
        extra = set(rule) - rule_ok
        assert not extra, "Vercel rejects the whole deployment for: %s" % sorted(extra)
        for h in rule["headers"]:
            assert set(h) == {"key", "value"}, "bad header entry: %s" % sorted(h)


def test_the_manifest_carries_icons_a_real_install_can_use():
    """Chrome's install criteria want a fetchable icon of at least 192x192, and
    a maskable one so Android does not letterbox it."""
    m = _manifest()
    assert m["display"] == "standalone" and m["start_url"] == "./"
    sizes = {i["sizes"] for i in m["icons"]}
    assert "192x192" in sizes and "512x512" in sizes
    purposes = " ".join(i.get("purpose", "") for i in m["icons"])
    assert "maskable" in purposes
    for icon in m["icons"]:
        path = os.path.join(HERE, icon["src"].lstrip("./"))
        assert os.path.exists(path), f"{icon['src']} is declared and missing"
        assert not icon["src"].startswith("data:"), \
            "a data URI is not reliably honoured as a manifest icon"


def test_the_png_icons_are_the_size_they_claim_and_are_not_blank():
    """A blank icon has the right dimensions and the wrong content. The first
    render produced a 537-byte 192x192 square of pure background and looked
    correct in every check that did not open it."""
    import struct
    for n in (192, 512, 180):
        path = os.path.join(HERE, f"icon-{n}.png")
        raw = open(path, "rb").read()
        w, h = struct.unpack(">II", raw[16:24])
        assert (w, h) == (n, n), f"icon-{n}.png is {w}x{h}"
        assert len(raw) > 1500, f"icon-{n}.png is {len(raw)} bytes — blank"


def test_ios_gets_a_png_apple_touch_icon():
    """iOS does not read manifest icons for Add to Home Screen and does not
    accept SVG in apple-touch-icon. Without this the installed icon is blank."""
    src = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    assert 'rel="apple-touch-icon" sizes="180x180" href="icon-180.png"' in src
    assert 'name="apple-mobile-web-app-capable"' in src


def test_the_page_the_worker_and_the_manifest_are_not_cached_forever():
    """An immutable Cache-Control on sw.js strands users on an old worker."""
    rules = {r["source"]: {h["key"]: h["value"] for h in r["headers"]}
             for r in _vercel()["headers"]}
    for src in ("/sw.js", "/manifest.webmanifest", "/(index.html)?"):
        cc = rules[src]["Cache-Control"]
        assert "max-age=0" in cc and "must-revalidate" in cc, f"{src}: {cc}"
    assert "immutable" in rules["/icon-(.*).png"]["Cache-Control"]


def test_the_service_worker_caches_what_the_manifest_declares():
    sw = open(os.path.join(HERE, "sw.js"), encoding="utf-8").read()
    for f in ("./index.html", "./manifest.webmanifest", "./icon-192.png",
              "./icon-512.png", "./icon-180.png"):
        assert f in sw, f"{f} is shipped and never cached"
    assert 'caches.match("./index.html")' in sw, \
        "a navigation that misses the cache offline must fall back to the page"
