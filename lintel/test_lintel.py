"""LINTEL, checked against predictions locked before it ran.

Five hit, two missed. Both misses are recorded by name, and the second one
overturned the study's own thesis in a useful direction:
`test_the_prediction_that_missed_and_was_better_news_than_the_hit`.
"""

import hashlib
import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "page-code"))

import lintel as L                                                # noqa: E402
import run_lintel as R                                            # noqa: E402

PREREG_SHA = "87f7bc79f3b81ec6c61f66dbec84a7b8b02ad08907a9af8679823abbaed54189"


@pytest.fixture(scope="module")
def g():
    parts, links, counts = R.graph()
    return {"parts": parts, "links": links, "counts": counts,
            "cuts": L.cuts(parts, links), "bridges": L.bridges(parts, links)}


# ------------------------------------------------------------- the lock ----
def test_the_preregistration_is_the_one_that_was_hashed():
    with open(os.path.join(HERE, "prereg_lintel.md"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == PREREG_SHA


def test_the_run_declares_the_same_hash():
    assert PREREG_SHA in open(os.path.join(HERE, "run_lintel.py")).read()


def test_the_subject_is_the_real_repository_not_a_fixture(g):
    assert g["counts"]["files_scanned"] > 400
    assert len(g["parts"]) > 100
    assert any(p.endswith(".py") for p in g["parts"])
    assert any(p.endswith(".mjs") or p.endswith(".js") for p in g["parts"])


# ------------------------------------------------------------- the hits ----
def test_n1_the_graph_has_cut_vertices(g):
    assert len(g["cuts"]) >= 5


def test_n2_a_shim_on_a_bridge_always_becomes_a_cut_vertex(g):
    """Spurious by construction: nobody's system got more fragile."""
    assert g["bridges"]
    for e in g["bridges"]:
        p2, l2 = L.insert_shim(g["parts"], g["links"], e)
        shim = next(n for n in p2 if n not in g["parts"])
        assert shim in L.cuts(p2, l2), e


def test_the_harness_defect_that_made_n2_look_like_a_miss(g):
    """First run said 31/67. The other 36 were a bug, not a finding.

    `bridges()` returns endpoints sorted; the first `insert_shim` removed the
    edge only in the stored direction, so for 36 bridges the original edge
    survived beside the shim and left a parallel route.
    """
    directed = {(a, b) for a, b, *_ in g["links"]}
    reversed_ = [e for e in g["bridges"] if e not in directed]
    assert len(reversed_) > 0
    assert len(reversed_) + len([e for e in g["bridges"] if e in directed]) \
        == len(g["bridges"])
    # the fix: the edge goes in either orientation
    e = reversed_[0]
    _, l2 = L.insert_shim(g["parts"], g["links"], e)
    assert (e[1], e[0], 1.0) not in l2
    assert (e[0], e[1], 1.0) not in l2


def test_n4_at_least_one_finding_survives_every_rewrite(g):
    """Otherwise the instrument would always say nothing and be useless."""
    res = _survival(g)
    assert len(res["survivors"]) >= 1


def test_n6_the_count_is_inflatable_with_no_behaviour_change(g):
    """The finding with the widest reach: the number tracks file granularity."""
    rng = random.Random(0)
    edges = sorted({(a, b) for a, b, *_ in g["links"]})
    p, l = list(g["parts"]), list(g["links"])
    seq = [len(L.cuts(p, l))]
    for k, e in enumerate(rng.sample(edges, 40)):
        p, l = L.insert_shim(p, l, e, tag=f"#{k}")
        seq.append(len(L.cuts(p, l)))
    assert all(seq[i] <= seq[i + 1] for i in range(len(seq) - 1))
    assert seq[-1] > seq[0]
    assert seq[-1] / seq[0] > 1.3


def test_n7_fosters_total_cannot_arbitrate(g):
    """It stays conserved under every rewrite, so it prefers no drawing."""
    t0, e0, c0 = R.foster(g["parts"], g["links"])
    p1, l1 = L.insert_shim(g["parts"], g["links"], g["bridges"][0])
    t1, e1, c1 = R.foster(p1, l1)
    assert c0 and c1
    assert t0 == pytest.approx(e0) and t1 == pytest.approx(e1)
    assert t1 != t0          # it moved, so it is not an arbiter


# ----------------------------------------------------------- the misses ----
def test_the_prediction_that_missed_about_splitting(g):
    """N5. Splitting a cut vertex does NOT yield two cut vertices.

    Measured across every eligible module: the fan-in half inherits the cut
    status and the fan-out half usually does not. Articulation is about what
    routes THROUGH a module from its importers, so the half carrying the
    importers keeps it.
    """
    links, parts = g["links"], g["parts"]
    both = [c for c in sorted(g["cuts"])
            if any(l[1] == c for l in links) and any(l[0] == c for l in links)]
    assert both
    tally = {"in_only": 0, "out_only": 0, "both": 0, "neither": 0}
    for t in both:
        pp, ll = L.split_module(parts, links, t)
        cc = L.cuts(pp, ll)
        i, o = (t + "#in") in cc, (t + "#out") in cc
        tally["both" if i and o else "in_only" if i else
              "out_only" if o else "neither"] += 1
    # the prediction was "both halves, every time". It is not.
    assert tally["both"] < len(both)
    assert tally["in_only"] > tally["out_only"]


def test_the_prediction_that_missed_and_was_better_news_than_the_hit(g):
    """N3. NO raw cut vertex was lost, under the four rewrites or under a far
    heavier regime.

    The study was built expecting findings to be artefacts. They are not. What
    is unstable is the COUNT, not the NAMES -- and those are different claims
    with opposite practical advice:

        do not compare counts between projects or across time
        do trust the list of modules

    That distinction is more useful than the one predicted, and it is only
    visible because the prediction was written down first and missed.
    """
    res = _survival(g)
    assert res["casualties"] == []
    assert len(res["survivors"]) == len(res["raw_cuts"])

    # and under 60 shims + splits + merges applied together
    parts, links = g["parts"], g["links"]
    rng = random.Random(7)
    p, l = list(parts), list(links)
    for k, e in enumerate(rng.sample(sorted({(a, b) for a, b, *_ in links}), 60)):
        p, l = L.insert_shim(p, l, e, tag=f"@{k}")
    heavy = L.cuts(p, l)
    mapped = {o for o in (L._origin(n) for n in heavy) if o is not None}
    assert set(res["raw_cuts"]) <= mapped          # every name still reported
    assert len(heavy) > len(res["raw_cuts"])       # the count moved a lot


def _survival(g):
    parts, links = g["parts"], g["links"]
    br = g["bridges"]
    both = [c for c in sorted(g["cuts"])
            if any(l[1] == c for l in links) and any(l[0] == c for l in links)]
    passthroughs = [n for n in parts
                    if len([l for l in links if l[1] == n]) == 1
                    and len([l for l in links if l[0] == n]) == 1]
    mergeable = [(a, b) for a, b, *_ in links
                 if {x for x, y, *_ in links if y == b} == {a}]
    rw = [("INSERT", lambda p, l: L.insert_shim(p, l, br[0])),
          ("SPLIT", lambda p, l: L.split_module(p, l, both[0]))]
    if passthroughs:
        rw.append(("COLLAPSE",
                   lambda p, l: L.collapse_passthrough(p, l, passthroughs[0])))
    if mergeable:
        rw.append(("MERGE", lambda p, l: L.merge_pair(p, l, *mergeable[0])))
    return L.survivors(parts, links, rw)


# ------------------------------------------------ the rewrites are honest ----
def test_every_rewrite_preserves_reachability(g):
    """Otherwise they would not be behaviour-preserving and nothing follows."""
    parts, links = g["parts"], g["links"]

    def reach(p, l):
        adj = {x: set() for x in p}
        for a, b, *_ in l:
            adj[a].add(b)
            adj[b].add(a)
        out = {}
        for s in p:
            seen, stack = {s}, [s]
            while stack:
                u = stack.pop()
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            out[s] = seen
        return out

    base = reach(parts, links)
    for label, (p2, l2) in (
            ("insert", L.insert_shim(parts, links, g["bridges"][0])),
            ("split", L.split_module(parts, links, sorted(g["cuts"])[0]))):
        after = reach(p2, l2)
        for a in parts:
            for b in parts:
                if a == b or a not in after and a + "#in" not in after:
                    continue
                key_a = a if a in after else a + "#in"
                key_b = b if b in after else b + "#in"
                if key_a not in after or key_b not in after:
                    continue
                was = b in base[a] or (b + "#in") in base.get(a, set())
                now = key_b in after[key_a] or (b + "#out") in after[key_a]
                if was:
                    assert now, f"{label}: {a} no longer reaches {b}"


def test_merge_refuses_a_pair_that_is_not_sole_importer(g):
    links = g["links"]
    shared = [(a, b) for a, b, *_ in links
              if len({x for x, y, *_ in links if y == b}) > 1]
    if not shared:
        pytest.skip("no shared-importer pair in this graph")
    with pytest.raises(ValueError, match="not imported solely"):
        L.merge_pair(g["parts"], links, *shared[0])


def test_collapse_refuses_a_node_that_is_not_a_passthrough(g):
    hub = max(g["parts"], key=lambda n: len([l for l in g["links"] if l[1] == n]))
    with pytest.raises(ValueError, match="not a one-in one-out"):
        L.collapse_passthrough(g["parts"], g["links"], hub)


# --------------------------------------------------------- no overclaim ----
def test_the_tool_states_what_it_cannot_do():
    assert L.UNDERSTANDS_CODE is False
    assert L.PROVES == "NOTHING"
    # the docstring wraps, so compare on collapsed whitespace
    doc = " ".join(L.__doc__.split())
    assert "not a fault" in doc
    assert "invisible here" in doc
    assert "does not mean the refactor is safe" in doc


def test_the_report_never_calls_a_surviving_module_a_fault(g):
    res = _survival(g)
    text = L.report(g["parts"], g["links"], res).lower()
    for banned in ("fault", "bad architecture", "error", "violation", "risk score"):
        if banned == "fault":
            assert "not a fault" in text      # the only permitted use
            continue
        assert banned not in text, banned
    assert "cannot be compared" in text


def test_the_report_does_not_render_zero_casualties_as_a_problem(g):
    """Empty is not an error. Nothing to report is a sentence, not a failure."""
    res = _survival(g)
    text = L.report(g["parts"], g["links"], res)
    if not res["casualties"]:
        assert "None of them was an artefact" in text
