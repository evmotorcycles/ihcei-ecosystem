"""The scaffold layer, and the two things it must never do.

These are not tests of the graph engine. `lens-graph.js` is a byte-exact lift
of app-2.html's two script blocks, which are themselves ports checked against
the Python by `smi/test_parity.py` and `plexus/test_plexus.py`. Re-testing the
arithmetic here would compare a copy to itself.

What is tested is the layer above it: **when the interface is allowed to draw a
mesh at all**, and whether any jargon reached a user-facing string.
"""

from __future__ import annotations

import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UPLOAD = None  # set below if the source prototype is reachable


def node(js):
    """Run a snippet with both engine files loaded, return parsed JSON."""
    boot = (
        "var g={};"
        "(new Function('globalThis','module',require('fs').readFileSync("
        + json.dumps(os.path.join(HERE, "lens-graph.js")) + ",'utf8')))(g,undefined);"
        "(new Function('globalThis','module',require('fs').readFileSync("
        + json.dumps(os.path.join(HERE, "wires.js")) + ",'utf8')))(g,undefined);"
        "var LMD=g.LMD,PLEXUS=g.PLEXUS,WIRES=g.WIRES;"
    )
    r = subprocess.run(["node", "-e", boot + js], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


# ------------------------------------------------- the port is a lift ----
def test_the_engine_is_lifted_verbatim_not_retyped():
    """A hand-copy would be a THIRD implementation that nothing checks."""
    src = os.path.join(ROOT, "lens-graph", "lens-graph.js")
    text = open(src, encoding="utf-8").read()
    # the two engines are present and carry their own provenance comments
    assert "lmd.js -- the LMD metric engine" in text
    assert "engines.js -- SPAR and FATHOM in the browser" in text
    assert "LIFTED VERBATIM" in text
    # and nothing here re-derives a resistance
    body = text.split("*/", 1)[1]
    assert body.count("function metricFromLaplacian") == 1


def test_foster_still_holds_through_the_lift():
    """The one arithmetic check kept: bearings sum to parts - pieces, exactly.
    If the lift were corrupted this is what would go first."""
    out = node("""
      var b=PLEXUS.bearings(['a','b','c','d'],[['a','b',1],['b','c',1],['c','d',1]]);
      console.log(JSON.stringify({total:b.total,expected:b.expected,ok:b.conserved}));
    """)
    assert out["ok"] is True
    assert abs(out["total"] - out["expected"]) < 1e-9


# ------------------------------------- the two refusals that matter ----
def test_no_wires_means_no_mesh():
    """A list of steps is not a structure. Drawing one would be a picture of
    nothing wearing the shape of a measurement."""
    out = node("""
      console.log(JSON.stringify(WIRES.meshEarnsItsPlace(['a','b','c'],[],'c')));
    """)
    assert out["draw"] is False and out["why"] == "nothing-declared"


def test_a_star_is_refused_because_it_degenerates_to_one_over_n():
    """MEASURED, not assumed: five supports wired straight to one conclusion
    each return dependence exactly 0.2. That is counting to five."""
    out = node("""
      var p=['s1','s2','s3','s4','s5','end'];
      var w=['s1','s2','s3','s4','s5'].map(function(s){return [s,'end',1];});
      var s=PLEXUS.sound(p,w,['s1','s2','s3','s4','s5'],'end');
      console.log(JSON.stringify({
        deps:s.bySource.map(function(r){return +r.dependence.toFixed(6);}),
        gate:WIRES.meshEarnsItsPlace(p,w,'end')}));
    """)
    assert out["deps"] == [0.2] * 5, out["deps"]
    assert out["gate"]["draw"] is False and out["gate"]["why"] == "star"


def test_the_same_five_wired_to_each_other_do_separate():
    """The control that makes the refusal meaningful: it is the STAR that is
    degenerate, not the engine."""
    out = node("""
      var p=['s1','s2','s3','s4','s5','end'];
      var w=[['s1','s3',1],['s3','s2',1],['s2','end',1],['s4','end',1],
             ['s5','s4',1],['s1','end',1]];
      var s=PLEXUS.sound(p,w,['s1','s2','s3','s4','s5'],'end');
      console.log(JSON.stringify({
        deps:s.bySource.map(function(r){return +r.dependence.toFixed(6);}),
        draw:WIRES.meshEarnsItsPlace(p,w,'end').draw}));
    """)
    assert out["draw"] is True
    assert len(set(out["deps"])) > 1, "the wired case must not be uniform too"


def test_what_falls_is_computed_by_removal_not_asserted():
    """The mobile metaphor is only honest if the fall is measured."""
    out = node("""
      var p=['a','b','c','d'];
      var w=[['a','b',1],['b','c',1],['c','d',1]];
      console.log(JSON.stringify(WIRES.whatFalls(p,w,1,'d')));
    """)
    assert sorted(out) == ["a", "b"], out


# --------------------------------------------------------- the words ----
JARGON = ["epistemic", "audit", "claim", "assay", "verdict", "checkable",
          "laplacian", "eigen", "resistance", "topology", "node", "vertex",
          "graph", "matrix"]


def _user_facing_strings(path):
    """Strings a person can actually read: visible HTML text plus the copy
    inside the two UI modules. Code identifiers and comments are excluded --
    a variable named `node` is not something anyone reads."""
    html = open(path, encoding="utf-8").read()
    body = html.split("<body>", 1)[1].split("</body>", 1)[0]
    body = re.sub(r"<script[\s\S]*?</script>", " ", body)
    body = re.sub(r"<style[\s\S]*?</style>", " ", body)
    text = re.sub(r"<[^>]+>", " ", body)
    return " ".join(text.split())


def test_no_jargon_reaches_the_visible_page():
    text = _user_facing_strings(os.path.join(HERE, "planner.html")).lower()
    assert text, "nothing visible was extracted; the check would prove nothing"
    hits = [w for w in JARGON if re.search(r"(?<![\w/\\])" + w + r"(?![\w/\\])", text)]
    assert hits == [], f"jargon on the visible page: {hits}\n{text[:400]}"


def test_the_copy_the_engine_emits_carries_no_jargon_either():
    """The refusal and reading sentences are user-facing even though they live
    in a .js file."""
    js = open(os.path.join(HERE, "wires.js"), encoding="utf-8").read()
    quoted = re.findall(r'"((?:[^"\\]|\\.){12,})"', js)
    blob = " ".join(quoted).lower()
    assert blob, "no copy found to check"
    hits = [w for w in JARGON if re.search(r"(?<![\w/\\])" + w + r"(?![\w/\\])", blob)]
    assert hits == [], f"jargon in emitted copy: {hits}"


def test_the_limit_is_present_and_is_not_smaller_than_the_promise():
    """CLAUDE.md: state the limit in the same size type as the promise."""
    css = open(os.path.join(HERE, "planner.html"), encoding="utf-8").read()
    promise = re.search(r"\.answer p\{[^}]*font-size:([\d.]+)rem", css)
    limit = re.search(r"\.limit\{[^}]*font-size:([\d.]+)rem", css)
    assert promise and limit, "could not find both sizes"
    assert float(limit.group(1)) >= float(promise.group(1)), (
        f"limit {limit.group(1)}rem is smaller than promise {promise.group(1)}rem")
    text = _user_facing_strings(os.path.join(HERE, "planner.html"))
    assert "What this cannot tell you" in text


def test_the_limit_says_a_well_drawn_wrong_mesh_looks_identical():
    """Checked on the RUNTIME VALUE, not the source text.

    The first draft grepped wires.js for the sentence and failed: the string is
    built by concatenation, so the source carries `... mesh of " + "right ones`
    and the substring never appears on disk. Source text is not what the user
    reads; the evaluated string is. Same lesson as a sentence that wraps across
    a line, one level down.
    """
    out = node("console.log(JSON.stringify(WIRES.LIMIT));")
    assert ("mesh of wrong steps looks exactly like a perfectly drawn mesh of "
            "right ones") in out
    assert "cannot tell you whether any step is worth doing" in out


def test_the_empty_state_is_never_styled_as_an_error():
    """Truthfulness is not truth. Nothing to draw is not a failure."""
    css = open(os.path.join(HERE, "planner.html"), encoding="utf-8").read()
    empty = re.search(r"\.empty\{([^}]*)\}", css)
    assert empty, "no empty-state rule found"
    assert "--hold" not in empty.group(1), "the empty state uses the alarm colour"
    text = _user_facing_strings(os.path.join(HERE, "planner.html")).lower()
    for bad in ("error", "failed", "invalid", "warning"):
        assert bad not in text, bad


def test_nothing_is_rendered_as_success_or_sound():
    text = _user_facing_strings(os.path.join(HERE, "planner.html")).lower()
    for bad in ("success", "sound", "verified", "safe", "passed", "healthy"):
        assert bad not in text, f"{bad!r} reads as a grade on an unchecked structure"
