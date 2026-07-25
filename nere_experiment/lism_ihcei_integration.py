#!/usr/bin/env python3
"""
lism_ihcei_integration.py — how LISM plugs into IHCEI, and what it adds
======================================================================
IHCEI is a PROBABILISTIC governance layer that sits between LLMs and AI
infrastructure: every message gets a posterior + credible interval answering
"does this preserve or erode the receiver's agency?" It is a delivery vehicle —
it needs (a) a coupling law for how fidelity maps to outcome, (b) a base-rate
signal per channel, and (c) a discipline that stops it over-claiming.

LISM supplies exactly those three, and this test shows each one live inside the
shipped IHCEI stack:

  T1  LINEAR COUPLING  — IHCEI's essence math IS LISM's law: E = U·D (linear),
                          with E=U·D² and D_min RETIRED_FULLY. Verified numerically.
  T2  tau_v -> CHANNEL — LISM's enforcement-latency sensor is the LABELLING
                          function that defines "failure" and seeds IHCEI's Beta
                          channel prior (the calibration hook). Verified with the
                          live 18-repo cohort.
  T3  METHODOLOGY FLOOR — LISM's non-test/anti-over-read discipline is enforced by
                          IHCEI's probabilistic floor: extreme evidence widens the
                          CI instead of flipping the verdict. Verified.

Run:  python3 lism_ihcei_integration.py
"""
import os, sys

STACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ihcei_stack", "ihcei_v3")
sys.path.insert(0, STACK)

from gt_probabilistic import (LAW_REGISTRY, CHANNEL_PRIORS, expected_essence,
                              evidence_to_beta, hazard_posterior, band_verdict)
from ihcei_kernel_v3 import IHCEIKernelV3

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'OK ' if cond else 'FAIL'} {name}" + (f"   [{detail}]" if detail else ""))


# ── T1 · LISM's linear coupling law lives inside IHCEI ───────────────────────
def t1_linear_coupling():
    print("\nT1 — LISM linear coupling (E = U·D) is IHCEI's essence math")
    check("E=U·D² RETIRED_FULLY in IHCEI registry",
          LAW_REGISTRY["E_quadratic"]["status"] == "RETIRED_FULLY")
    check("D_min hard floor RETIRED_FULLY in IHCEI registry",
          LAW_REGISTRY["D_min_threshold"]["status"] == "RETIRED_FULLY")
    # doubling the fidelity evidence doubles essence (linear), does NOT quadruple it
    e_lo = expected_essence(1.0, *evidence_to_beta(0.4, 50)).e_mean
    e_hi = expected_essence(1.0, *evidence_to_beta(0.8, 50)).e_mean
    ratio = e_hi / e_lo
    check("essence linear in D (ratio ~2, not ~4)", 1.7 < ratio < 2.3, f"ratio={ratio:.3f}")
    # essence scales linearly in U too
    e_u2 = expected_essence(2.0, *evidence_to_beta(0.8, 50)).e_mean
    check("essence linear in U (double U -> double E)", abs(e_u2 / e_hi - 2.0) < 1e-6)


# ── T2 · tau_v is the failure-labelling function that seeds an IHCEI channel ──
def t2_tauv_channel():
    print("\nT2 — tau_v seeds an IHCEI channel prior (the calibration bridge)")
    # Live-validated 18-repo cohort (TAUV_VALIDATION.md): dormant carry the high
    # tau_v backlog (LISM's failure signal), active are the survivors.
    #   dormant/high-tau_v  -> failures ;  active/low-tau_v -> successes
    dormant, active = 13, 5             # from the live health reclassification
    observed_rate = dormant / (dormant + active)   # 0.722
    start_mean = CHANNEL_PRIORS["oss_default"].mean  # the weak fallback prior
    d = IHCEIKernelV3.update_channel("github_live_tauv", failures=dormant, successes=active)
    check("channel prior created from tau_v labels", "github_live_tauv" in CHANNEL_PRIORS)
    # correct Bayesian behaviour: the tau_v evidence MOVES the prior toward the
    # observed failure rate (a posterior, not a raw rate) ...
    check("tau_v evidence moves the channel prior toward the observed failure rate",
          start_mean < d["mean"] < observed_rate,
          f"{start_mean:.3f} -> {d['mean']:.3f} (toward {observed_rate:.3f})")
    # ... and converges to it as more tau_v-labelled repos arrive (100x the counts,
    # swamping the weak fallback prior's pseudo-counts)
    d100 = IHCEIKernelV3.update_channel("github_live_tauv_100x", failures=1300, successes=500)
    check("channel base-rate converges to tau_v-observed rate with more evidence",
          abs(d100["mean"] - observed_rate) < 0.05, f"prior_100x={d100['mean']:.3f} vs {observed_rate:.3f}")
    # IHCEI's per-item hazard now runs on the tau_v-calibrated channel
    h = hazard_posterior(d_gap=0.0, channel="github_live_tauv")
    check("hazard_posterior consumes the tau_v-seeded base rate",
          abs(h.base_rate - CHANNEL_PRIORS["github_live_tauv"].mean) < 1e-9,
          f"base_rate={h.base_rate:.3f}")
    check("posterior respects the probabilistic floor [0.01,0.99]",
          0.01 <= h.p_mean <= 0.99)


# ── T3 · LISM's methodology discipline is enforced by the probabilistic floor ─
def t3_methodology_floor():
    print("\nT3 — LISM non-test / anti-over-read discipline, enforced at runtime")
    h0 = hazard_posterior(d_gap=0.0, channel="kubernetes")
    h1 = hazard_posterior(d_gap=0.86, channel="kubernetes")   # extreme 'evidence'
    w0, w1 = h0.ci95[1] - h0.ci95[0], h1.ci95[1] - h1.ci95[0]
    check("extreme evidence WIDENS the CI (uncertainty, not false certainty)", w1 > w0,
          f"{w0:.3f} -> {w1:.3f}")
    check("extreme evidence does NOT move the mean across a band",
          abs(h1.p_mean - h0.p_mean) < 0.10, f"delta={abs(h1.p_mean-h0.p_mean):.3f}")
    # a wide credible interval cannot BLOCK — the firewall refusing to over-read
    wide = band_verdict(p_mean=0.90, ci=(0.20, 0.99))
    tight = band_verdict(p_mean=0.90, ci=(0.60, 0.99))
    check("wide CI downgrades BLOCK -> WARN (non-test triage at runtime)", wide.verdict == "WARN")
    check("tight high CI still allows BLOCK (real signal passes)", tight.verdict == "BLOCK")


def main():
    print("=" * 76)
    print(" LISM x IHCEI INTEGRATION — the three contributions, live in the stack")
    print("=" * 76)
    t1_linear_coupling()
    t2_tauv_channel()
    t3_methodology_floor()
    print("\n" + "=" * 76)
    print(f" RESULT: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print(" FAILED:", FAIL)
    print("\n WHAT LISM ADDS TO IHCEI")
    print(" - Linear coupling law  : the SUPPORTED essence form (E=U·D); retires the")
    print("                          quadratic and the hard D_min floor.")
    print(" - tau_v sensor         : a cheap, domain-general failure-labelling function")
    print("                          that calibrates each channel's base rate.")
    print(" - Methodology firewall : the discipline (VIF gate, non-test triage, locked")
    print("                          rule) that IHCEI's floor enforces so it never")
    print("                          over-reads a collapsed or sparse signal.")
    print("=" * 76)
    raise SystemExit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
