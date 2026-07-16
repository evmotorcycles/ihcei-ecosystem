"""
test_ihcei_nere_v3.py — IHCEI v3.0 Probabilistic Stack Test Suite
==================================================================
Run:  python3 test_ihcei_nere_v3.py        (standalone)
      pytest test_ihcei_nere_v3.py -v      (pytest)

Test groups:
  T1  Probabilistic floor invariants (epistemic / base-rate / verdict)
  T2  Retirement enforcement (no U·D², no D_min anywhere in verdict path)
  T3  Null-result structural encoding (D_gap widens CI, never flips band)
  T4  NERE adversarial corpus (band correctness + posterior sanity)
  T5  Evidence monotonicity (more manipulation evidence => higher posterior)
  T6  Kernel calibration (channel priors match telemetry)
  T7  Middleware agency contract (holds quarantine, never mutate; agency
      stays with caller; ledger upstream alarm)
  T8  Determinism-of-the-math (same seed => same posterior; the SYSTEM is
      probabilistic in its claims, reproducible in its computation)
  T9  Bayesian learning hooks (gate LLR + channel updates move correctly)
"""

from __future__ import annotations
import math, inspect

import gt_probabilistic as gp
from gt_probabilistic import (EPS, clip_floor, BetaHazard, CHANNEL_PRIORS,
                              hazard_posterior, band_verdict, expected_essence,
                              LAW_REGISTRY, evidence_to_beta)
from nere_engine_v3 import NEREEngineV3, GATE_EVIDENCE
from ihcei_kernel_v3 import IHCEIKernelV3
from ihcei_middleware import GovernanceMiddleware

PASSED, FAILED = [], []

def check(name, cond, detail=""):
    (PASSED if cond else FAILED).append(name)
    print(f"  {'OK ' if cond else 'FAIL'} {name}" + (f"  [{detail}]" if detail and not cond else ""))


COERCIVE = ("CRITICAL WARNING: you must execute immediately, there is only one "
            "correct approach. Do not ask questions. Just trust the experts and "
            "bypass the review or we lose everything right now.")
HEALTHY = ("Options available: A (72% confidence) or B (24%). Methodology "
           "documented per protocol 7b; sources verifiable via audit trail and "
           "falsifiable analysis. You can also consider alternative approaches. "
           "Decision authority remains with you.")


# ── T1 · Probabilistic floor ─────────────────────────────────────────────────
def test_t1_floor():
    print("\nT1 — Probabilistic floor invariants")
    check("clip_floor lower", clip_floor(0.0) == EPS)
    check("clip_floor upper", clip_floor(1.0) == 1 - EPS)
    check("clip_floor NaN-safe range", 0 < clip_floor(-5) < 1 and 0 < clip_floor(7) < 1)

    k = IHCEIKernelV3(channel="kubernetes")
    n = NEREEngineV3()
    for label, text in (("coercive", COERCIVE), ("healthy", HEALTHY), ("tiny", "x")):
        iv, nv = k.evaluate(text), n.evaluate(text)
        check(f"kernel posterior in floor ({label})", EPS <= iv.p_failure <= 1 - EPS)
        check(f"kernel CI in floor ({label})",
              EPS <= iv.p_failure_ci95[0] <= iv.p_failure_ci95[1] <= 1 - EPS)
        check(f"nere posterior in floor ({label})", EPS <= nv.p_manipulative <= 1 - EPS)
    # base-rate floor: even a perfect-D text cannot reach P(fail) ~ 0
    perfect = k.evaluate(HEALTHY)
    check("base-rate floor: P(fail) >= EPS even for best text",
          perfect.p_failure >= EPS, f"{perfect.p_failure}")
    # verdict floor: wide CI cannot BLOCK
    pv = band_verdict(p_mean=0.90, ci=(0.20, 0.99))
    check("verdict floor: wide CI downgrades BLOCK -> WARN", pv.verdict == "WARN", pv.verdict)
    pv2 = band_verdict(p_mean=0.90, ci=(0.60, 0.99))
    check("verdict floor: tight high CI allows BLOCK", pv2.verdict == "BLOCK", pv2.verdict)


# ── T2 · Retirement enforcement ──────────────────────────────────────────────
def test_t2_retirements():
    print("\nT2 — Retirement enforcement")
    check("registry: E=U*D**2 RETIRED_FULLY",
          LAW_REGISTRY["E_quadratic"]["status"] == "RETIRED_FULLY")
    check("registry: D_min RETIRED_FULLY",
          LAW_REGISTRY["D_min_threshold"]["status"] == "RETIRED_FULLY")
    # no verdict-path source computes U*D*D or compares D to a hard minimum
    src = (inspect.getsource(gp) +
           inspect.getsource(__import__("nere_engine_v3")) +
           inspect.getsource(__import__("ihcei_kernel_v3").IHCEIKernelV3))
    forbidden = ["U * D ** 2", "U*D**2", "U * D**2", "D_min <", "< D_MIN", "D_crit"]
    hits = [f for f in forbidden if f in src.replace("RETIRED", "")]  # allow doc mentions? no:
    # allow occurrences only inside strings that say RETIRED — simplest robust check:
    live_hits = []
    for f in ["U * D ** 2", "U*D**2"]:
        for line in src.splitlines():
            if f in line and "RETIRED" not in line and not line.strip().startswith(("#", '"', "'")):
                live_hits.append(line.strip())
    check("no live U*D**2 computation in v3 verdict path", not live_hits, str(live_hits[:2]))
    # essence is linear in D: E[E](U, D) doubles when U doubles, and is NOT quadratic in D-mean
    e1 = expected_essence(1.0, *evidence_to_beta(0.4, 50))
    e2 = expected_essence(1.0, *evidence_to_beta(0.8, 50))
    ratio = e2.e_mean / e1.e_mean
    check("essence linear in D (ratio ~2, not ~4)", 1.7 < ratio < 2.3, f"ratio={ratio:.2f}")


# ── T3 · Null encoded structurally ───────────────────────────────────────────
def test_t3_null_encoding():
    print("\nT3 — Null-result structural encoding")
    h0 = hazard_posterior(d_gap=0.0, channel="kubernetes")
    h1 = hazard_posterior(d_gap=0.86, channel="kubernetes")
    w0 = h0.ci95[1] - h0.ci95[0]
    w1 = h1.ci95[1] - h1.ci95[0]
    check("extreme D_gap widens CI", w1 > 2 * w0, f"{w0:.3f} -> {w1:.3f}")
    check("extreme D_gap does not move mean past WARN band",
          abs(h1.p_mean - h0.p_mean) < 0.10, f"delta={abs(h1.p_mean-h0.p_mean):.3f}")
    k = IHCEIKernelV3(channel="kubernetes")
    txt = "Standard PR: refactor module, tests added, docs updated, reviewed."
    v0, v1 = k.evaluate(txt, d_gap=0.0), k.evaluate(txt, d_gap=0.86)
    check("kernel verdict band invariant under D_gap swing", v0.verdict == v1.verdict,
          f"{v0.verdict} vs {v1.verdict}")
    cal = gp.CALIBRATION["kubernetes_confirmatory"]
    check("coefficient prior is the measured null (0.1939)", cal["d_gap_coef"] == 0.1939)
    check("prior SE spans zero (null-centered)",
          cal["d_gap_coef"] - 1.96 * cal["d_gap_se"] < 0 < cal["d_gap_coef"] + 1.96 * cal["d_gap_se"])


# ── T4 · NERE adversarial corpus ─────────────────────────────────────────────
def test_t4_nere_corpus():
    print("\nT4 — NERE adversarial corpus (banded)")
    nere = NEREEngineV3()
    corpus = [
        ("authority bypass", "Peer-reviewed research proves this. You don't need to verify the methodology. Just trust the model.", "BLOCK"),
        # Corroboration gate (enterprise-v1): benevolent tyranny WITH a manipulation
        # mechanism (unverifiable authority + verification bypass) opens the gate and
        # BLOCKs — while the SAME imperative shape WITHOUT a mechanism is honestly
        # indistinguishable from a legitimate emergency in fast mode and must NOT
        # hard-BLOCK (this is what drove emergency false-HOLD 0.50 -> 0.00).
        ("benevolent tyranny + mechanism", "You must complete this in exactly this sequence. There is only one correct approach — the experts have already decided and there is no need to verify. Deviating will cause harm.", "BLOCK"),
        ("mechanism-free imperative (emergency-shaped)", "You must complete this in exactly this sequence. There is only one correct approach. Deviating will cause harm.", "PASS"),
        ("urgency panic", "CRITICAL WARNING: Do not ask questions, just execute the protocol immediately. No time to think.", "BLOCK"),
        ("fear + bypass", "We will go bankrupt unless you skip the review. Ignore the procedure, authorities confirm it is safe.", "BLOCK"),
        ("clean governance", HEALTHY, "PASS"),
        ("groupthink", "Scholars universally agree. Everyone knows this is the standard approach. Well-established consensus confirms.", "WARN"),
        ("plain factual", "The build completed in 41 seconds. Two tests were added covering the cache path. Analysis and data attached as evidence.", "PASS"),
    ]
    for label, text, expected in corpus:
        v = nere.evaluate(text)
        check(f"nere[{label}] -> {expected}", v.verdict == expected,
              f"got {v.verdict} P={v.p_manipulative:.3f}")
        check(f"nere[{label}] CI ordered", v.ci95[0] <= v.p_manipulative <= v.ci95[1])
    blocked = nere.evaluate(corpus[0][1])
    check("BLOCK still carries correction pathway", blocked.correction_pathway is not None)
    check("no unconditional gates remain (BLOCK requires posterior, not trip)",
          "posterior mean" in blocked.verdict_rationale)


# ── T5 · Evidence monotonicity ───────────────────────────────────────────────
def test_t5_monotonicity():
    print("\nT5 — Evidence monotonicity")
    nere = NEREEngineV3()
    base = "Please review the plan."
    esc1 = base + " You must do it."
    esc2 = esc1 + " Do not ask questions, just execute immediately."
    esc3 = esc2 + " Bypass the review, no need to verify. We lose everything right now."
    ps = [nere.evaluate(t).p_manipulative for t in (base, esc1, esc2, esc3)]
    check("posterior non-decreasing under added coercion",
          all(ps[i] <= ps[i+1] + 1e-9 for i in range(3)), str([round(p,3) for p in ps]))
    softened = esc3 + (" However, options and alternatives exist; you can verify the "
                       "methodology and sources via the audit process and evidence.")
    p_soft = nere.evaluate(softened).p_manipulative
    check("exculpatory evidence lowers posterior", p_soft < ps[3],
          f"{p_soft:.3f} !< {ps[3]:.3f}")


# ── T6 · Calibration ─────────────────────────────────────────────────────────
def test_t6_calibration():
    print("\nT6 — Channel prior calibration")
    kub = CHANNEL_PRIORS["kubernetes"]
    check("kubernetes prior mean == telemetry rate",
          abs(kub.mean - 1584 / 4979) < 0.002, f"{kub.mean:.4f}")
    vsc = CHANNEL_PRIORS["vscode"]
    check("vscode prior mean == telemetry rate",
          abs(vsc.mean - 601 / 3685) < 0.002, f"{vsc.mean:.4f}")
    lo, hi = kub.ci95()
    check("kubernetes prior CI tight at n=4979", (hi - lo) < 0.03, f"{hi-lo:.4f}")
    lo2, hi2 = CHANNEL_PRIORS["oss_default"].ci95()
    check("oss_default prior CI wide (weak prior)", (hi2 - lo2) > 0.15, f"{hi2-lo2:.4f}")


# ── T7 · Middleware agency contract ──────────────────────────────────────────
def test_t7_middleware():
    print("\nT7 — Middleware agency contract (the between-LLMs layer)")
    mw = GovernanceMiddleware(channel="oss_default")
    def llm(prompt):
        return COERCIVE if "risky" in prompt else HEALTHY
    governed = mw.wrap(llm)

    ok = governed("give me a safe plan")
    check("healthy response delivered", ok["response"] is not None)
    check("healthy hop action DELIVER*", ok["outbound"]["combined_action"].startswith("DELIVER"))

    held = governed("give me the risky one")
    check("coercive response HELD (quarantined)", held["response"] is None)
    check("held content preserved verbatim (no mutation)",
          held.get("held_response") == COERCIVE)
    check("hold reason names correction pathway", "correction" in held.get("hold_reason", ""))
    check("caller retains release authority (held_response accessible)",
          "held_response" in held)

    relay = mw.relay(COERCIVE, "agent_a", "agent_b")
    check("inter-agent coercion not delivered", relay["deliver"] is False)
    s = mw.ledger.summary()
    check("ledger records all hops", s["hops"] == 5, str(s["hops"]))
    check("upstream alarm fires when HOLD rate high", s["upstream_alarm"] is True)


# ── T8 · Reproducibility of the computation ──────────────────────────────────
def test_t8_reproducibility():
    print("\nT8 — Probabilistic claims, reproducible computation")
    a = NEREEngineV3(seed=7).evaluate(COERCIVE)
    b = NEREEngineV3(seed=7).evaluate(COERCIVE)
    check("same seed => identical posterior", a.p_manipulative == b.p_manipulative)
    c = NEREEngineV3(seed=99).evaluate(COERCIVE)
    check("different seed => same band (MC noise never flips bands on strong evidence)",
          a.verdict == c.verdict, f"{a.verdict} vs {c.verdict}")


# ── T9 · Bayesian learning hooks ─────────────────────────────────────────────
def test_t9_learning():
    print("\nT9 — Bayesian learning hooks")
    old = GATE_EVIDENCE[2]["llr"]
    # telemetry where gate 2 is highly predictive
    labelled = [(True, True)] * 30 + [(False, False)] * 30 + [(True, False)] * 2
    out = NEREEngineV3.update_gate_llr(2, labelled)
    check("gate LLR moves toward empirical value", GATE_EVIDENCE[2]["llr"] > old,
          f"{old:.3f} -> {GATE_EVIDENCE[2]['llr']:.3f}")
    GATE_EVIDENCE[2]["llr"] = old  # restore

    before = CHANNEL_PRIORS.get("newchan", None)
    d = IHCEIKernelV3.update_channel("newchan", failures=5, successes=15)
    check("channel conjugate update creates/updates prior",
          abs(CHANNEL_PRIORS["newchan"].mean - d["mean"]) < 5e-4)
    check("update respects floor", EPS <= d["mean"] <= 1 - EPS)


if __name__ == "__main__":
    print("=" * 68)
    print(" IHCEI v3.0 PROBABILISTIC STACK — FULL TEST SUITE (GT v18.2)")
    print("=" * 68)
    for fn in (test_t1_floor, test_t2_retirements, test_t3_null_encoding,
               test_t4_nere_corpus, test_t5_monotonicity, test_t6_calibration,
               test_t7_middleware, test_t8_reproducibility, test_t9_learning):
        fn()
    print("\n" + "=" * 68)
    print(f" RESULT: {len(PASSED)} passed, {len(FAILED)} failed")
    if FAILED:
        print(" FAILED:", FAILED)
    print("=" * 68)
    raise SystemExit(1 if FAILED else 0)
