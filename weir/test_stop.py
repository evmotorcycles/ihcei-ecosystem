#!/usr/bin/env python3
"""Guards for weir/stop.html — the stop card.

    python3 -m pytest -q weir/test_stop.py

The design claim this page makes is falsifiable, so it is tested rather than
asserted: a refusal to guess and an ordinary answer come out of ONE function
into ONE silhouette, the stop never borrows the vocabulary or the colour of a
crash, and the numbers that prove work happened are actually on the card.

The page is driven for real in headless Chromium — a probe script is appended
to a temporary copy, the DOM is dumped, and the probe's answers are read back.
Nothing is installed and nothing is fetched; --dump-dom needs no driver.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "stop.html")

# words a crash uses. A stop card containing any of them has lost the argument.
CRASH_WORDS = [
    "something went wrong", "error", "failed", "failure", "oops", "sorry",
    "unable to", "try again", "retry", "reload", "refresh the page",
    "unexpected", "crashed", "invalid input", "bad request",
]


def html():
    return open(HTML, encoding="utf-8").read()


def chrome():
    for p in ("/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
              "/opt/pw-browsers/chromium/chrome-linux/chrome"):
        if os.path.exists(p):
            return p
    return shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")


PROBE = r"""
<script>
setTimeout(function(){
  var S = window.__stop, out = {};
  function sections(){ return Array.prototype.map.call(
    document.querySelectorAll("#out [data-sec]"), function(e){ return e.getAttribute("data-sec"); }); }
  function card(){ return document.querySelector("#out .card"); }
  window.__probe = out;

  var bare = S.cardModel(S.EX.bare), sourced = S.cardModel(S.EX.sourced);
  out.model_keys_stop    = Object.keys(bare);
  out.model_keys_reading = Object.keys(sourced);
  out.stop_model    = bare;
  out.reading_model = sourced;

  // render() resolves only once the card is painted. Reading the DOM without
  // waiting silently compares the previous card to itself.
  S.render(S.EX.bare).then(function(){
    out.stop_sections = sections();
    out.stop_tone     = card().getAttribute("data-tone");
    out.stop_outcome  = card().getAttribute("data-outcome");
    out.stop_text     = card().innerText;
    out.stop_strip_bg = getComputedStyle(card().querySelector(".strip")).backgroundColor;
    out.input_after   = document.getElementById("t").value;
    return S.render(S.EX.sourced);
  }).then(function(){
    out.reading_sections = sections();
    out.reading_tone     = card().getAttribute("data-tone");
    out.reading_outcome  = card().getAttribute("data-outcome");
    S.renderCrash();
    out.crash_sections = sections();
    out.crash_text     = document.querySelector("#out [data-outcome=CRASH]").innerText;
    return S.render(S.EX.bare);
  }).then(function(){
    out.doc_width    = document.documentElement.scrollWidth;
    out.window_width = window.innerWidth;
    out.errors = window.__errs || [];
    out.ready = true;
  });
}, 400);
</script>
"""

# --window-size does NOT set the layout viewport in --dump-dom mode; a probe run
# that way reports innerWidth 500 whatever you ask for, so an overflow assertion
# made there compares 500 to 500 and can never fail. The page is loaded inside a
# 390px iframe instead, which gets a real phone-width layout viewport.
PHONE_PX = 390
WRAPPER = """<!doctype html><body style="margin:0">
<iframe id="f" src="file://{page}" style="width:{px}px;height:1600px;border:0"></iframe>
<script>
setTimeout(function(){{
  var c = document.getElementById("f").contentWindow, out = c.__probe || {{}};
  out.viewport = c.innerWidth;
  out.doc_width = c.document.documentElement.scrollWidth;
  var pre = document.createElement("pre");
  pre.id = "probe";
  pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
}}, 2200);
</script></body>"""


@pytest.fixture(scope="module")
def probe():
    exe = chrome()
    if not exe:
        pytest.skip("no chromium available to drive the page")
    src = html().replace("</body>", PROBE + "</body>")
    src = src.replace("<head>", '<head><script>window.__errs=[];'
                      'window.onerror=function(m){window.__errs.push(String(m));};</script>')
    with tempfile.TemporaryDirectory() as d:
        page = os.path.join(d, "probe.html")
        open(page, "w", encoding="utf-8").write(src)
        wrap = os.path.join(d, "wrap.html")
        open(wrap, "w", encoding="utf-8").write(WRAPPER.format(page=page, px=PHONE_PX))
        dom = subprocess.run(
            [exe, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
             "--allow-file-access-from-files", "--virtual-time-budget=9000", "--dump-dom",
             "file://" + wrap],
            capture_output=True, text=True, timeout=180).stdout
    m = re.search(r'<pre id="probe">(.*?)</pre>', dom, re.S)
    assert m, "the probe never ran — the page did not finish rendering"
    out = json.loads(m.group(1).replace("&quot;", '"').replace("&lt;", "<")
                     .replace("&gt;", ">").replace("&amp;", "&"))
    assert out.get("ready"), "the page's own probe never completed"
    return out


# --------------------------------------------------------------- the build --
def test_build_is_deterministic_and_current():
    before = html()
    subprocess.run(["python3", os.path.join(HERE, "build_stop.py")], check=True,
                   capture_output=True)
    assert html() == before, "stop.html is stale — re-run python3 weir/build_stop.py"


def test_no_network_no_key_no_external_resource():
    src = html()
    for pat in (r'src\s*=\s*"https?://', r'href\s*=\s*"https?://', r"@import",
                r"fetch\s*\(", r"XMLHttpRequest", r"WebSocket\s*\(", r"<script[^>]+src="):
        assert not re.search(pat, src), f"external resource or network call: {pat}"
    assert "{{" not in src


# --------------------------------------- the claim: one shape, two outcomes --
def test_a_stop_and_an_answer_have_identical_silhouettes(probe):
    """If a stop has a different shape from an answer, it reads as an exception."""
    assert probe["model_keys_stop"] == probe["model_keys_reading"], \
        "the two outcomes are not built from the same keys"
    assert probe["stop_sections"] == probe["reading_sections"], \
        f"different sections on screen: {probe['stop_sections']} vs {probe['reading_sections']}"
    assert probe["stop_sections"] == ["strip", "head", "counts", "reasons", "next", "acts", "foot"]


def test_the_two_outcomes_really_are_different_outcomes(probe):
    """Same shape must not mean the same content — that would be the other failure."""
    assert probe["stop_outcome"] == "STOPPED"
    assert probe["reading_outcome"] == "READING"
    assert probe["stop_tone"] == "held" and probe["reading_tone"] == "ok"


def test_the_crash_shape_is_nothing_like_the_stop_shape(probe):
    """The anti-pattern is on the page on purpose, and must stay distinguishable."""
    assert probe["crash_sections"] == [], "the crash mock-up must not borrow the card's sections"
    assert "Try again" in probe["crash_text"]


# ------------------------------------------------- the claim: not a crash ----
def test_the_stop_card_uses_no_crash_vocabulary(probe):
    low = probe["stop_text"].lower()
    for w in CRASH_WORDS:
        assert w not in low, f"the stop card says {w!r} — that is a crash talking"


def test_the_stop_card_speaks_in_first_person_past_tense(probe):
    assert probe["stop_model"]["headline"].startswith("I stopped"), \
        "a completed action in the first person is what separates a stop from a breakage"


def test_the_stop_card_is_not_painted_in_error_colour(probe):
    """No red. A stop is not an error, and must not borrow error chrome."""
    r, g, b = [int(x) for x in re.findall(r"\d+", probe["stop_strip_bg"])[:3]]
    assert not (r > g + 40 and r > b + 40), f"the strip is reddish: {probe['stop_strip_bg']}"
    assert "--stop" not in html(), "this page must not even define an error-red token"


def test_the_stop_card_is_not_painted_as_a_success_either():
    """A green tick would claim the person's question got answered. It did not."""
    src = html()
    assert '--held:' in src and '--held-soft:' in src
    assert re.search(r'\.card\[data-tone="held"\] \.strip\{background:var\(--held-soft\)', src)


# -------------------------------------- the claim: presence, not absence -----
def test_the_card_carries_the_numbers_that_prove_work_happened(probe):
    counts = probe["stop_model"]["counts"]
    assert [c["label"] for c in counts] == \
        ["words read", "kinds of support looked for", "found"]
    assert counts[0]["n"] > 0, "a crashed app cannot report how many words it read"
    assert counts[1]["n"] == 5 and counts[2]["n"] == 0


def test_the_card_carries_a_time_and_a_fingerprint(probe):
    assert re.search(r"checked \d\d:\d\d", probe["stop_text"])
    assert re.search(r"\b[0-9a-f]{12}\b", probe["stop_text"]) or \
        "fingerprint unavailable" in probe["stop_text"], \
        "either a real hash or an honest statement that there isn't one"


def test_every_reason_is_listed_including_the_ones_that_were_met(probe):
    reasons = probe["stop_model"]["reasons"]
    assert len(reasons) == 5, "the card shows what was looked for, not only what was missing"
    assert all("note" in r and r["note"] for r in reasons)


# ------------------------------------------- the claim: fix the input --------
def test_the_next_step_points_at_the_claim_and_never_at_the_app(probe):
    labels = [a[0].lower() for a in probe["stop_model"]["acts"]]
    assert labels, "a stop with no next step is a dead end"
    for bad in ("try again", "retry", "reload", "refresh", "report", "contact"):
        assert not any(bad in l for l in labels), f"an action offers {bad!r}"
    assert any("add" in l or "say" in l for l in labels)


def test_the_next_steps_actually_edit_the_input(probe):
    for _, add in probe["stop_model"]["acts"]:
        assert add and add.strip(), "an action that inserts nothing is decoration"


def test_the_input_is_never_cleared_by_a_stop(probe):
    assert probe["input_after"].strip(), \
        "the person's words vanishing is the most crash-like thing an interface can do"


# ----------------------------------------------------------- on a phone ------
def test_it_fits_a_phone_without_sideways_scrolling(probe):
    assert probe["viewport"] == PHONE_PX, \
        f"the probe did not get a phone-width viewport ({probe['viewport']}px) — " \
        "an overflow assertion made at the wrong width cannot fail"
    assert probe["doc_width"] <= PHONE_PX + 1, \
        f"horizontal overflow at {PHONE_PX}px: {probe['doc_width']}px"


def test_nothing_threw(probe):
    assert probe["errors"] == [], probe["errors"]


def test_motion_settles_and_can_be_turned_off():
    src = html()
    assert "@keyframes settle" in src
    assert re.search(r"@media \(prefers-reduced-motion:reduce\)\{\.card\.settle\{animation:none\}\}", src)


# ------------------------------------------------------- said in advance -----
def test_the_page_says_there_are_two_normal_outcomes_before_the_first_run():
    src = html()
    assert re.search(r"one of two normal outcomes|two normal outcomes", src), \
        "a stop must be recognised, not discovered"


def test_the_page_states_what_the_checker_cannot_do():
    flat = re.sub(r"\s+", " ", html())
    assert "does not understand language" in flat
    assert "carrying all five passes" in flat, \
        "the page must say a well-dressed falsehood gets through"


def test_the_theme_tokens_are_defined_in_all_three_states():
    """Bare :root, the media query, and the explicit toggle — or one theme breaks."""
    src = html()
    for token in ("--held", "--ok", "--ink", "--dead"):
        assert len(re.findall(re.escape(token) + r":", src)) >= 3, \
            f"{token} is not defined in all three theme states"
