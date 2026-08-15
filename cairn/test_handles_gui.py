#!/usr/bin/env python3
"""The handles have to reach the screen, not just the JSON.

    python3 -m pytest -q cairn/test_handles_gui.py

Both browser apps are driven for real in headless Chromium with the claim from
the case study, and the test fails if the person is left holding a tick with
nothing behind it.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = {"desk": os.path.join(HERE, "desk.html"), "plain": os.path.join(HERE, "plain.html")}

GREEN_TEA = ("According to a 2023 randomised trial of 240 participants in the UK, "
             "green tea reduced self-reported stress by 12%.")
HOLLOW = "Green tea reduces stress."


def chrome():
    for p in ("/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
              "/opt/pw-browsers/chromium/chrome-linux/chrome"):
        if os.path.exists(p):
            return p
    return shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")


PROBE = """
<script>
setTimeout(function(){
  function run(t){
    var c = document.getElementById("claim");
    c.value = t;
    var b = document.getElementById("check") ||
            document.querySelector("button[id*=check],button[onclick*=check]");
    if (b) b.click(); else if (window.check) window.check();
    return {
      block:  !!document.querySelector(".handles"),
      chips:  Array.prototype.map.call(document.querySelectorAll(".hv em"),
                function(e){ return e.textContent; }),
      line:   (document.getElementById("hline") || {}).value || null,
      note:   (document.querySelector(".hnote") || {}).innerText || null,
      text:   (document.getElementById("out") || {}).innerText || ""
    };
  }
  var out = { rich: run(%s), hollow: run(%s), errors: window.__errs || [] };
  var pre = document.createElement("pre");
  pre.id = "probe";
  pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
}, 500);
</script>
""" % (json.dumps(GREEN_TEA), json.dumps(HOLLOW))


@pytest.fixture(scope="module", params=sorted(PAGES))
def page(request):
    exe = chrome()
    if not exe:
        pytest.skip("no chromium available to drive the page")
    src = open(PAGES[request.param], encoding="utf-8").read()
    src = src.replace("<head>", '<head><script>window.__errs=[];'
                      'window.onerror=function(m){window.__errs.push(String(m));};</script>')
    src = src.replace("</body>", PROBE + "</body>")
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "p.html")
        open(f, "w", encoding="utf-8").write(src)
        dom = subprocess.run(
            [exe, "--headless", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=9000", "--dump-dom", "file://" + f],
            capture_output=True, text=True, timeout=180).stdout
    m = re.search(r'<pre id="probe">(.*?)</pre>', dom, re.S)
    assert m, f"{request.param}: the probe never ran"
    out = json.loads(m.group(1).replace("&quot;", '"').replace("&lt;", "<")
                     .replace("&gt;", ">").replace("&amp;", "&"))
    out["name"] = request.param
    return out


def test_the_handles_reach_the_screen(page):
    assert page["rich"]["block"], f"{page['name']}: no handles panel for a 5/5 claim"


def test_every_load_bearing_span_is_shown(page):
    chips = " ".join(page["rich"]["chips"])
    for handle in ("2023", "240 participants", "12%", "randomised trial", "in the UK"):
        assert handle in chips, f"{page['name']}: {handle!r} is missing from the handles"


def test_the_search_line_is_on_the_page_ready_to_copy(page):
    assert page["rich"]["line"] == "2023 240 participants 12% randomised trial in the UK", \
        f"{page['name']}: {page['rich']['line']!r}"


def test_the_page_still_says_checkable_is_not_true(page):
    low = page["rich"]["text"].lower()
    assert "does not make it true" in low or "not that it is true" in low, \
        f"{page['name']}: the page must not let a full label read as a truth verdict"


def test_a_source_marker_with_nobody_named_is_called_out(page):
    note = page["rich"]["note"] or ""
    assert "nobody is actually named" in note, \
        f"{page['name']}: 'according to a trial' ticks the source row and names no one"


def test_a_hollow_claim_shows_no_handles_rather_than_invented_ones(page):
    assert not page["hollow"]["block"], \
        f"{page['name']}: handles appeared for a claim with nothing in it"


def test_nothing_threw(page):
    assert page["errors"] == [], f"{page['name']}: {page['errors']}"
