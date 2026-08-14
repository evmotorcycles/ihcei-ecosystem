#!/usr/bin/env python3
"""Guards for novora-suite/suite.html — the offline nine-product browser GUI.

    python3 -m pytest -q novora-suite/test_suite_html.py
"""
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "suite.html")
BUNDLE = os.path.join(HERE, "engine.bundle.js")

PRODUCTS = ["pages", "pulse", "lens", "voice", "mark", "stand", "weigh", "bridge", "rise"]


def html():
    return open(HTML, encoding="utf-8").read()


def test_build_is_current():
    before = html()
    subprocess.run(["python3", os.path.join(HERE, "build_bundle.py")], check=True, capture_output=True)
    subprocess.run(["python3", os.path.join(HERE, "build_suite.py")], check=True, capture_output=True)
    assert html() == before, (
        "suite.html is stale — re-run build_bundle.py then build_suite.py and commit")


def test_all_nine_products_present_and_no_tenth_invented():
    src = html()
    ids = set(re.findall(r'id:"(\w+)"', src))
    assert ids == set(PRODUCTS), f"UI product ids drifted from the engine: {ids}"


def test_no_network_no_api_key():
    """The prototype called a paid API from the browser. This must never do that."""
    src = html()
    for pat in (r'src\s*=\s*"https?://', r'href\s*=\s*"https?://', r"fetch\s*\(",
                r"XMLHttpRequest", r"api\.anthropic\.com", r"ANTHROPIC_API_KEY",
                r"WebSocket\s*\(", r"navigator\.sendBeacon"):
        assert not re.search(pat, src), f"suite.html must stay offline; found {pat}"
    assert "{{" not in src


def test_the_paid_endpoint_is_mentioned_nowhere_the_user_can_see_it():
    """`/api/analyse` survives inside the inlined engine's `analysis` string. It is
    inert — nothing calls it — but an offline page must not advertise a paid
    endpoint to a reader either, so the UI must never render `r.analysis`."""
    src = html()
    ui = src.split("root.NOVORA =")[-1]          # everything after the engine bundle
    assert "/api/analyse" not in ui, "the page's own UI code must not mention the paid endpoint"
    assert "r.analysis" not in ui, (
        "the UI must not render the engine's analysis string — it points at deep mode, "
        "which this offline build cannot and must not call")


def test_score_is_hidden_when_the_engine_says_it_is_not_a_judgement():
    """Regression lock. Eight of the nine products used to return a confident
    number for an EMPTY box — LENS called an empty contract 0.75 BALANCED. The
    engine now abstains, and the UI must honour display_score."""
    src = html()
    assert "r.display_score !== false" in src
    assert "dress a non-judgement as a verdict" in src


def test_engine_abstains_on_thin_input_for_every_product():
    out = subprocess.run(
        ["node", "-e", f"""
        require({BUNDLE!r});
        const bad=[];
        for (const id of NOVORA.PRODUCT_IDS) {{
          for (const t of ['', 'hi', 'ok thanks']) {{
            const r = NOVORA.screen(id, t);
            if (r.insufficient_evidence !== true || r.display_score !== false) bad.push(id+'/'+t);
          }}
        }}
        console.log(bad.join(',') || 'OK');
        """], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "OK", f"products failed to abstain: {out.stdout}"


def test_the_screen_not_a_judge_caveat_is_on_the_page():
    flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html()))
    for phrase in [
        "These are screens , not judges" .replace(" , ", ", "),
        "they cannot tell whether it is true, legal, or safe",
        'A high score means "nothing obvious was caught", never "this is fine"',
    ]:
        assert phrase in flat, f"missing caveat: {phrase!r}"


def test_result_disclaims_judging_the_person():
    src = html()
    assert "not a judgement about the person" in src
    assert "does not read meaning" in src


def test_dark_and_light_themes_both_defined():
    src = html()
    assert "prefers-color-scheme:dark" in src
    assert ':root[data-theme="dark"]' in src
    assert ':root:not([data-theme="light"])' in src


def test_navigation_uses_the_hash_so_browser_back_works():
    src = html()
    assert "hashchange" in src
    assert 'display="inline-block"' in src or 'display = "inline-block"' in src or \
           'style.display="inline-block"' in src


def test_the_suite_links_to_the_rest_of_the_stack_and_they_all_exist():
    """The nine read text. Three other screens do something else, and the suite
    now says so — a link that points at nothing is worse than no link."""
    import re as _re
    src = html()
    hrefs = _re.findall(r'<a class="card" href="([^"]+)"', src)
    assert {"../keel/console.html", "../smi/app.html", "../weir/panel.html"} <= set(hrefs)
    for h in hrefs:
        target = os.path.normpath(os.path.join(HERE, h))
        assert os.path.exists(target), f"the suite links to nothing: {h}"


def test_the_standalone_jax_file_runs_by_itself():
    """smi/lmd_jax.py is meant to be copied away and run. It must not need the
    rest of the repository to do that."""
    import subprocess
    path = os.path.join(os.path.dirname(HERE), "smi", "lmd_jax.py")
    src = open(path, encoding="utf-8").read()
    for banned in ("from smi", "import smi", "from .", "sys.path"):
        assert banned not in src, f"the standalone file reaches into the repo: {banned}"
    r = subprocess.run(["python3", path], capture_output=True, text=True,
                       timeout=300, cwd="/tmp")
    assert r.returncode == 0, r.stderr[-600:]
    assert "slope -0.500000" in r.stdout
    assert "identity, not a result" in r.stdout
