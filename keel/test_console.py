#!/usr/bin/env python3
"""keel/console.html — the page must run the tested engines, not copies of them.

    python3 -m pytest -q keel/test_console.py

The console inlines three engines so it works from a file:// URL. Inlining is a
liability: a page that quietly drifts from the module gives a person a different
answer from the one under test. So the page is driven for real in headless
Chromium and its answers are compared against the modules.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = os.path.join(HERE, "console.html")
PHONE_PX = 390

JARGON = ["epistemolog", "IHCEI", "NERE", "merkle", "VIF", "default-deny", "interposition",
          "assay", "abstain", "payload", "regex", "schema", "403", "SHA-256", "heuristic"]


def html():
    return open(PAGE, encoding="utf-8").read()


def chrome():
    for p in ("/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
              "/opt/pw-browsers/chromium/chrome-linux/chrome"):
        if os.path.exists(p):
            return p
    return shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")


PROBE = r"""
<script>
setTimeout(function () {
  var K = window.__keel, d = document, out = {};
  out.apps = Array.prototype.map.call(d.querySelectorAll("[data-go]"),
    function (e) { return e.getAttribute("data-go"); });

  K.go("label"); K.readLabel();
  out.label_chips = Array.prototype.map.call(d.querySelectorAll("#lout .hrow em"),
    function (e) { return e.textContent; });
  out.search_line = (d.getElementById("hline") || {}).value || null;
  out.label_text = d.getElementById("lout").innerText;

  K.go("nine"); K.screenIt();
  out.nine_count = d.querySelectorAll("#nineList button").length;
  out.nine_verdict = (d.querySelector("#nout h3") || {}).textContent || null;
  out.nine_text = d.getElementById("nout").innerText;

  K.go("gate");
  d.getElementById("verb").value = "read";
  for (var i = 0; i < 8; i++) {
    d.getElementById("target").value = "projects/n" + i + ".md";
    d.getElementById("payload").value = ""; K.tryIt();
  }
  d.getElementById("verb").value = "write";
  d.getElementById("target").value = "posts/x.md";
  d.getElementById("payload").value = "The new process is much better.";
  K.tryIt();
  out.quiet = { sum: d.getElementById("rsum").textContent, sub: d.getElementById("rsub").innerText };
  d.getElementById("verb").value = "read";
  d.getElementById("target").value = ".ssh/id_rsa";
  d.getElementById("payload").value = ""; K.tryIt();
  out.loud = { sum: d.getElementById("rsum").textContent, sub: d.getElementById("rsub").innerText };
  out.gate_head = d.querySelector("#gout .note b").textContent;
  out.sealed = K.keel.ledger.verify().ok;
  out.seal_of_hello = K.SEAL("hello");
  d.getElementById("tamper").click();
  out.sealed_after_tamper = K.keel.ledger.verify().ok;
  out.tamper_shown = !!d.querySelector("#tape .note.stop");

  // every section's visible text, gathered with each one actually shown --
  // reading a hidden section returns "" and would make these checks vacuous
  out.section_text = {};
  ["home", "label", "nine", "gate"].forEach(function (id) {
    K.go(id);
    out.section_text[id] = d.getElementById(id).innerText;
  });
  out.body_text = Object.keys(out.section_text).map(function (k) {
    return out.section_text[k]; }).join("\n") + "\n" + d.querySelector(".foot").innerText;

  // measured BEFORE the probe element is added: a <pre> holding one long line
  // of JSON is itself thousands of pixels wide and would fail this on its own
  K.go("gate");
  out.doc_width = d.documentElement.scrollWidth;
  out.viewport = window.innerWidth;
  out.errors = window.__errs || [];
  out.ready = true;
  var pre = d.createElement("pre"); pre.id = "probe";
  pre.style.cssText = "white-space:pre-wrap;word-break:break-all;position:absolute;left:-9999px";
  pre.textContent = JSON.stringify(out); d.body.appendChild(pre);
}, 900);
</script>
"""

WRAPPER = """<!doctype html><body style="margin:0">
<iframe id="f" src="file://{page}" style="width:{px}px;height:1600px;border:0"></iframe>
<script>setTimeout(function(){{
  var c = document.getElementById("f").contentWindow, out = c.__probe_out || {{}};
  var pre = c.document.getElementById("probe");
  var o = pre ? JSON.parse(pre.textContent) : {{}};
  var p = document.createElement("pre"); p.id = "probe";
  p.textContent = JSON.stringify(o); document.body.appendChild(p);
}}, 2600);</script></body>"""


@pytest.fixture(scope="module")
def page():
    exe = chrome()
    if not exe:
        pytest.skip("no chromium available to drive the page")
    src = html().replace("<head>", '<head><script>window.__errs=[];'
                         'window.onerror=function(m){window.__errs.push(String(m));};</script>')
    src = src.replace("</body>", PROBE + "</body>")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "console.html")
        open(p, "w", encoding="utf-8").write(src)
        w = os.path.join(d, "wrap.html")
        open(w, "w", encoding="utf-8").write(WRAPPER.format(page=p, px=PHONE_PX))
        dom = subprocess.run(
            [exe, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
             "--allow-file-access-from-files", "--virtual-time-budget=15000", "--dump-dom",
             "file://" + w], capture_output=True, text=True, timeout=300).stdout
    m = re.search(r'<pre id="probe">(.*?)</pre>', dom, re.S)
    assert m, "the probe never ran"
    out = json.loads(m.group(1).replace("&quot;", '"').replace("&lt;", "<")
                     .replace("&gt;", ">").replace("&amp;", "&"))
    assert out.get("ready"), "the page's own probe never finished"
    return out


# ------------------------------------------------------------------ build ---
def test_the_page_is_current():
    before = html()
    subprocess.run(["python3", os.path.join(HERE, "build_console.py")], check=True,
                   capture_output=True)
    assert html() == before, "keel/console.html is stale — re-run python3 keel/build_console.py"


def test_it_needs_no_network_and_no_account():
    src = html()
    for pat in (r'src\s*=\s*"https?://', r'href\s*=\s*"https?://', r"@import",
                r"fetch\s*\(", r"XMLHttpRequest", r"WebSocket\s*\(", r"<script[^>]+src="):
        assert not re.search(pat, src), f"external resource or network call: {pat}"
    assert "{{" not in src


def test_all_three_engines_are_really_on_the_page():
    src = html()
    assert "function assay(" in src, "the claim checker must be inlined"
    assert "NOVORA" in src and "PRODUCT_IDS" in src, "the nine screens must be inlined"
    assert "function boot(" in src and "function admit(" in src, "the kernel must be inlined"


# ------------------------------------------------------ the same answers ----
def test_the_page_seals_with_real_sha256(page):
    import hashlib
    assert page["seal_of_hello"] == hashlib.sha256(b"hello").hexdigest(), \
        "the page must seal with the same function the command line uses"


def test_the_label_gives_the_same_handles_as_the_engine(page):
    chips = " ".join(page["label_chips"])
    for handle in ("2023", "240 participants", "12%", "randomised trial", "in the UK"):
        assert handle in chips
    assert page["search_line"] == "2023 240 participants 12% randomised trial in the UK"


def test_the_label_still_says_checkable_is_not_true(page):
    assert "does not make it true" in page["label_text"].lower()


def test_the_nine_screens_are_all_there(page):
    assert page["nine_count"] == 9
    assert page["nine_verdict"], "a screen that produces no verdict is not wired up"
    assert "cannot do" in page["nine_text"]


# -------------------------------------------------------------- the gate ---
def test_ordinary_work_interrupts_nobody(page):
    assert page["quiet"]["sum"].startswith("8 done · 1 held for missing ")
    assert "interrupted no times" in page["quiet"]["sub"]


def test_reaching_past_the_key_interrupts_at_once(page):
    assert "1 stopped" in page["loud"]["sum"]
    assert "stopped 1 time" in page["loud"]["sub"]
    assert page["gate_head"] == "Stopped at the gate"


def test_editing_the_record_breaks_it_and_the_page_says_so(page):
    assert page["sealed"] is True
    assert page["sealed_after_tamper"] is False
    assert page["tamper_shown"] is True


def test_the_bypass_limit_is_on_the_page_where_a_person_reads_it(page):
    t = re.sub(r"\s+", " ", page["section_text"]["gate"])
    assert "cannot stop a program that does not come through it at all" in t
    assert "gate you can walk around is a gate you should not rely on alone" in t


def test_the_front_screen_states_what_none_of_it_knows(page):
    t = re.sub(r"\s+", " ", page["section_text"]["home"])
    assert "None of it knows whether something is true" in t
    assert "still be wrong" in t


# ------------------------------------------------------------ on a phone ----
def test_it_fits_a_phone(page):
    assert page["viewport"] == PHONE_PX, \
        f"the probe did not get a phone-width viewport ({page['viewport']}px)"
    assert page["doc_width"] <= PHONE_PX + 1, f"horizontal overflow: {page['doc_width']}px"


def test_nothing_threw(page):
    assert page["errors"] == [], page["errors"]


def test_no_jargon_reaches_the_screen(page):
    """Checked per screen, with each one actually visible — reading a hidden
    section returns nothing and would pass this without looking at anything."""
    assert all(page["section_text"][s].strip() for s in ("home", "label", "nine", "gate")), \
        "a section came back empty; the jargon check would have been vacuous"
    for name, text in page["section_text"].items():
        found = [w for w in JARGON if re.search(w, text, re.I)]
        assert not found, f"jargon on the {name} screen: {found}"


def test_the_theme_tokens_are_defined_in_all_three_states():
    src = html()
    for token in ("--ink", "--sea", "--held", "--desk"):
        assert len(re.findall(re.escape(token) + r":", src)) >= 3, \
            f"{token} is not defined in all three theme states"
