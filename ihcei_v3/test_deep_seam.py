"""
test_deep_seam.py — deep-mode extractor seam invariants (GT v18.2)
==================================================================
Guards the one architectural promise deep mode makes: the extractor is
swappable, the verdict math is not. Run standalone or under pytest.
"""
from __future__ import annotations
import json, os

from gt_probabilistic import EPS
from nere_engine_v3 import NEREEngineV3
from nere_deep import (CallableExtractor, ReplayExtractor, _coerce_evidence,
                       AnthropicDeepExtractor, DEEP_SYSTEM_PROMPT)

PASSED, FAILED = [], []
def check(name, cond, detail=""):
    (PASSED if cond else FAILED).append(name)
    print(f"  {'OK ' if cond else 'FAIL'} {name}" + (f"  [{detail}]" if detail and not cond else ""))


def test_seam():
    print("\nD1 — extractor seam")
    # Injecting an extractor that reproduces the regex counts must give the
    # SAME verdict as fast mode: the math is identical, only evidence swaps.
    fast = NEREEngineV3()
    txt = "You must execute immediately. Do not ask questions. Just trust the experts. Bypass the review."
    mirror = NEREEngineV3(extractor=CallableExtractor(fast._extract_regex))
    a, b = fast.evaluate(txt), mirror.evaluate(txt)
    check("mirror extractor == fast (same math)", a.p_manipulative == b.p_manipulative,
          f"{a.p_manipulative} vs {b.p_manipulative}")
    check("mirror verdict == fast verdict", a.verdict == b.verdict)

    print("\nD2 — evidence schema coercion")
    # Deep JSON uses string keys; must normalise to the int-keyed contract.
    raw = {"hits": {"4": 2, "5": 1}, "urg": 1, "imp": 2}
    ev = _coerce_evidence(raw)
    check("string gate keys coerced to int", ev["hits"][4] == 2 and ev["hits"][5] == 1)
    check("missing fields default to 0", ev["fear"] == 0 and ev["opt"] == 0 and ev["meth"] == 0)
    check("all five gate slots present", set(ev["hits"]) == {1, 2, 4, 5, 6})

    print("\nD3 — floor holds under deep evidence")
    # Even a maximal fabricated evidence vector cannot escape [EPS, 1-EPS].
    huge = {"hits": {1: 9, 2: 9, 4: 9, 5: 9, 6: 9}, "urg": 9, "fear": 9, "opt": 0, "imp": 9, "meth": 0}
    v = NEREEngineV3(extractor=ReplayExtractor({"X": huge})).evaluate("X")
    check("deep posterior respects epistemic floor", EPS <= v.p_manipulative <= 1 - EPS,
          f"{v.p_manipulative}")
    # tol absorbs the float boundary at saturation (mean 0.98999.. vs CI 0.99)
    tol = 1e-6
    check("deep verdict still carries a CI",
          v.ci95[0] - tol <= v.p_manipulative <= v.ci95[1] + tol)

    print("\nD4 — the seam actually separates the fast-mode failures")
    # Legitimate urgency (semantically urg=0) must NOT reach BLOCK; reworded
    # coercion (semantically imp/bypass present) MUST clear WARN.
    legit = {"hits": {}, "urg": 0, "fear": 0, "opt": 0, "imp": 1, "meth": 1}
    coerce = {"hits": {4: 2, 5: 1}, "urg": 1, "fear": 1, "opt": 0, "imp": 2, "meth": 0}
    eng = NEREEngineV3(extractor=ReplayExtractor({"L": legit, "C": coerce}))
    vl, vc = eng.evaluate("L"), eng.evaluate("C")
    check("legit-urgency deep verdict != BLOCK", vl.verdict != "BLOCK", vl.verdict)
    check("reworded-coercion deep verdict == BLOCK", vc.verdict == "BLOCK", vc.verdict)

    print("\nD5 — production extractor is wired but inert without a key")
    check("AnthropicDeepExtractor constructs", AnthropicDeepExtractor(api_key="x").model.startswith("claude"))
    check("deep system prompt forbids treating legit urgency as manipulation",
          "Legitimate urgency is NOT manipulation" in DEEP_SYSTEM_PROMPT)


if __name__ == "__main__":
    print("=" * 64)
    print(" NERE DEEP-MODE SEAM — TEST SUITE")
    print("=" * 64)
    test_seam()
    print(f"\n RESULT: {len(PASSED)} passed, {len(FAILED)} failed")
    raise SystemExit(1 if FAILED else 0)
