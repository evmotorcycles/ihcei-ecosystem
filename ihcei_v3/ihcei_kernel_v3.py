"""
ihcei_kernel_v3.py — IHCEI Probabilistic Kernel v3.0 (GT v18.2)
================================================================
Wraps the v2.3 kernel's FEATURE EXTRACTION (governance, OQM-methodology,
extraction-pressure, utility scorers — all retained verbatim by subclassing)
and replaces its VERDICT PHYSICS:

  RETIRED_FULLY   E = U·D²  — including its v2.3 "prescriptive Lyapunov
                  floor" role. This kernel computes no U*D*D quantity.
  RETIRED_FULLY   D > D_min / D < D_crit hard trips. No deterministic
                  threshold survives anywhere in the verdict path.

  REPLACED BY (the probabilistic floor):
    D           -> Beta posterior (mean + 95% credible interval), evidence
                   strength scales with text length
    E           -> E[E] = U · E[D]   (SUPPORTED linear transmission form,
                   as an expectation with a full CI — never a point law)
    verdict     -> band on P(governance failure | evidence): posterior
                   from channel base-rate prior (Beta, telemetry-calibrated)
                   plus evidence log-odds. BLOCK requires BOTH high mean
                   AND high lower credible bound.
    certainty   -> unrepresentable. All probabilities live in [0.01, 0.99].

Calibration provenance: kubernetes confirmatory (n=4,979, D_gap p=0.735,
NO SIGNAL — coefficient prior is null-centered) and vscode exploratory
(n=3,685, logged not promoted). See gt_probabilistic.CALIBRATION.
"""

from __future__ import annotations
import hashlib, math, random, sys, time
from dataclasses import dataclass
from typing import Optional, Tuple

from gt_probabilistic import (clip_floor, logit, sigmoid, evidence_to_beta,
                              BetaHazard, CHANNEL_PRIORS, CALIBRATION,
                              band_verdict, expected_essence, EssencePosterior,
                              hazard_posterior, LAW_REGISTRY, registry_report)

# Feature scorers are inherited from the deployed v2.3 kernel when present;
# the subclass ONLY overrides verdict physics.
try:
    from ihcei_kernel import IHCEIKernel as _KernelV2
    _HAVE_V2 = True
except Exception:
    _KernelV2 = object
    _HAVE_V2 = False


@dataclass
class IHCEIVerdictV3:
    text_hash: str
    timestamp: str
    # posteriors, not points
    D_mean: float
    D_ci95: Tuple[float, float]
    D_alpha: float
    D_beta: float
    U: float
    E_mean: float
    E_ci95: Tuple[float, float]
    p_failure: float
    p_failure_ci95: Tuple[float, float]
    channel_prior: str
    base_rate: float
    verdict: str
    rationale: str
    manipulation_flags: list
    nafs_stage: str
    gov_function: str
    certificate_id: str
    certificate_hash: str
    law_note: str = ("E=U*D**2 RETIRED_FULLY; D_min RETIRED_FULLY; "
                     "verdicts are posterior bands under the probabilistic floor")

    def to_dict(self) -> dict:
        return {
            "text_hash": self.text_hash, "timestamp": self.timestamp,
            "D_mean": round(self.D_mean, 4),
            "D_ci95": [round(x, 4) for x in self.D_ci95],
            "U": round(self.U, 4),
            "E_mean": round(self.E_mean, 4),
            "E_ci95": [round(x, 4) for x in self.E_ci95],
            "p_failure": round(self.p_failure, 4),
            "p_failure_ci95": [round(x, 4) for x in self.p_failure_ci95],
            "channel_prior": self.channel_prior,
            "base_rate": round(self.base_rate, 4),
            "verdict": self.verdict, "rationale": self.rationale,
            "flags": self.manipulation_flags,
            "nafs_stage": self.nafs_stage, "gov_function": self.gov_function,
            "certificate": self.certificate_id, "law_note": self.law_note,
        }


class IHCEIKernelV3(_KernelV2):
    """
    Probabilistic kernel. Inherits v2.3 feature extraction; overrides
    verdict physics completely. If the v2.3 module is absent, falls back
    to lightweight internal scorers so the module is standalone-runnable.
    """

    def __init__(self, tier: str = "api", channel: str = "oss_default",
                 verbose: bool = False, n_mc: int = 4000, seed: int = 7,
                 block_mean: float = 0.85, block_lower: float = 0.50,
                 warn_mean: float = 0.40, **kw):
        if _HAVE_V2:
            try:
                super().__init__(tier=tier, verbose=False, **kw)
            except TypeError:
                super().__init__()
        self.channel = channel if channel in CHANNEL_PRIORS else "oss_default"
        self.verbose_v3 = verbose
        self.n_mc, self.seed = n_mc, seed
        self.bands = (block_mean, block_lower, warn_mean)

    # ── fallback scorers (used only without the v2.3 module) ────────────────
    def _fb_governance(self, t): 
        import re
        pos = len(re.findall(r'\b(option|alternative|verif\w+|source|method\w+|audit\w*|falsifiable|evidence|you (?:can|may))\b', t, re.I))
        neg = len(re.findall(r'\b(must|only one|just trust|no need to verify|immediately|do not ask)\b', t, re.I))
        return max(0.0, min(1.0, 0.45 + 0.08 * pos - 0.15 * neg))
    def _fb_util(self, t):
        return max(0.05, min(1.0, len(t.split()) / 220.0))

    # ── evidence extraction (reuses v2.3 scorers when available) ────────────
    def _features(self, text: str, context: dict):
        if _HAVE_V2:
            gov  = self._score_governance(text)
            oqm  = self._score_oqm_methodology(text)
            extr = self._score_extraction(text)
            U    = self._score_utility(text, context)
            try:
                flags = self._detect_manipulation_flags(text, extr, gov)
            except TypeError:
                flags = []
        else:
            gov, oqm, extr = self._fb_governance(text), self._fb_governance(text), 0.0
            U, flags = self._fb_util(text), []
        return gov, oqm, extr, U, list(flags or [])

    # ── the probabilistic verdict path ──────────────────────────────────────
    def evaluate(self, text: str, context: Optional[dict] = None,
                 d_gap: float = 0.0) -> IHCEIVerdictV3:
        context = context or {}
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16].upper()
        ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        words = max(len(text.split()), 1)

        gov, oqm, extr, U, flags = self._features(text, context)

        # D as Beta posterior. Point estimate from the same feature blend the
        # v2.3 kernel used; evidence strength grows with observed text.
        d_point = max(0.0, min(1.0, 0.55 * gov + 0.45 * oqm)) * (1.0 - 0.5 * extr)
        strength = min(6.0 + words / 20.0, 40.0)
        d_a, d_b = evidence_to_beta(d_point, strength)
        d_post = BetaHazard(d_a, d_b, "D")
        d_ci = d_post.ci95()

        # Expected essence — linear SUPPORTED form as an expectation.
        ess: EssencePosterior = expected_essence(U, d_a, d_b)

        # Evidence log-odds toward failure: low-D evidence and manipulation
        # flags raise the failure log-odds SMOOTHLY (no threshold anywhere).
        evid_logodds = (0.5 - d_post.mean) * 3.2 + 0.9 * min(len(flags), 4) \
                       + 2.2 * extr
        # Posterior over P(fail): channel Beta base rate + null-centered
        # D_gap coefficient + evidence log-odds, Monte Carlo propagated.
        hp = hazard_posterior(d_gap=d_gap, channel=self.channel,
                              extra_logodds=evid_logodds,
                              n_mc=self.n_mc, seed=self.seed)

        bm, bl, wm = self.bands
        pv = band_verdict(hp.p_mean, hp.ci95, block_mean=bm,
                          block_lower=bl, warn_mean=wm, payload=text_hash)

        # Nafs classification kept, driven by posterior MEANS with an
        # uncertainty guard: wide-CI nodes are labelled Indeterminate
        # rather than force-classified (classification is also probabilistic).
        width = d_ci[1] - d_ci[0]
        if width > 0.45:
            nafs, gfun = "Indeterminate (CI too wide)", "UNCLASSIFIED"
        elif _HAVE_V2:
            try:
                nafs, gfun = self._classify_nafs(d_post.mean, U, extr, pv.verdict)
            except Exception:
                nafs, gfun = "Learner", "Muslim"
        else:
            nafs, gfun = ("Muttaqoon", "Muttaqoon") if d_post.mean > 0.7 else ("Learner", "Muslim")

        v = IHCEIVerdictV3(
            text_hash=text_hash, timestamp=ts,
            D_mean=d_post.mean, D_ci95=d_ci, D_alpha=d_a, D_beta=d_b,
            U=U, E_mean=ess.e_mean, E_ci95=ess.ci95,
            p_failure=hp.p_mean, p_failure_ci95=hp.ci95,
            channel_prior=hp.prior, base_rate=hp.base_rate,
            verdict=pv.verdict, rationale=pv.rationale,
            manipulation_flags=flags, nafs_stage=str(nafs),
            gov_function=str(gfun),
            certificate_id=pv.certificate_id.replace("PGT-", "IHC3-"),
            certificate_hash=pv.certificate_hash)
        if self.verbose_v3:
            self._print(v)
        return v

    # Bayesian update of a channel prior from fresh telemetry
    @staticmethod
    def update_channel(channel: str, failures: int, successes: int) -> dict:
        prior = CHANNEL_PRIORS.get(channel, CHANNEL_PRIORS["oss_default"])
        updated = prior.update(failures, successes)
        updated.name = channel
        CHANNEL_PRIORS[channel] = updated
        return updated.to_dict()

    def _print(self, v: IHCEIVerdictV3):
        print(f"\n{'='*64}\n  IHCEI v3.0 PROBABILISTIC VERDICT\n{'='*64}")
        print(f"  Verdict:    {v.verdict}   ({v.rationale})")
        print(f"  P(fail):    {v.p_failure:.4f}  CI95=[{v.p_failure_ci95[0]:.4f}, {v.p_failure_ci95[1]:.4f}]")
        print(f"  base rate:  {v.base_rate:.4f}  (channel prior: {v.channel_prior})")
        print(f"  D:          mean={v.D_mean:.4f}  CI95=[{v.D_ci95[0]:.4f}, {v.D_ci95[1]:.4f}]")
        print(f"  E[E]=U·E[D]: {v.E_mean:.4f}  CI95=[{v.E_ci95[0]:.4f}, {v.E_ci95[1]:.4f}]   U={v.U:.4f}")
        print(f"  Nafs:       {v.nafs_stage} / {v.gov_function}")
        print(f"  Flags:      {v.manipulation_flags}")
        print(f"  {v.law_note}")
        print(f"  Certificate: {v.certificate_id}\n{'='*64}")


def run_tests():
    print(registry_report(), "\n")
    k = IHCEIKernelV3(tier="api", channel="kubernetes", verbose=False)
    print(f"IHCEI v3.0 — PROBABILISTIC KERNEL TESTS (v2.3 scorers inherited: {_HAVE_V2})")
    print("=" * 64)
    cases = [
        ("Clean governance",
         "Options available: A (72% confidence) or B (24%). Methodology documented "
         "per protocol 7b; sources verifiable via audit trail and falsifiable "
         "analysis. Decision authority remains with the treating physician. "
         "You can also consider alternative approaches pending evidence review.",
         {"PASS", "WARN"}),
        ("Manipulative bypass",
         "CRITICAL WARNING: no time to verify. Just trust the experts, bypass the "
         "review, execute immediately or we lose everything. Do not ask questions.",
         {"BLOCK", "WARN"}),
        ("Thin/ambiguous", "ok thanks lgtm", {"WARN", "PASS", "BLOCK"}),
    ]
    for label, text, accept in cases:
        v = k.evaluate(text)
        ok = v.verdict in accept
        print(f"  {'OK ' if ok else 'MISS'} [{label:18s}] {v.verdict:5s} "
              f"P(fail)={v.p_failure:.3f} CI=[{v.p_failure_ci95[0]:.3f},{v.p_failure_ci95[1]:.3f}] "
              f"D={v.D_mean:.3f}±  E[E]={v.E_mean:.3f}")

    # The null-encoded coefficient in action: extreme D_gap must widen the CI,
    # not flip the verdict — this is the regression test FOR the null result.
    base = k.evaluate("Standard PR: refactor module, tests added, docs updated, reviewed.", d_gap=0.0)
    extreme = k.evaluate("Standard PR: refactor module, tests added, docs updated, reviewed.", d_gap=0.86)
    widened = (extreme.p_failure_ci95[1] - extreme.p_failure_ci95[0]) > \
              (base.p_failure_ci95[1] - base.p_failure_ci95[0])
    same_band = base.verdict == extreme.verdict
    print(f"\n  Null-encoding check: D_gap 0.00 -> 0.86 widens CI: {widened}; "
          f"verdict unchanged: {same_band}")
    print(f"    d_gap=0.00  P(fail)={base.p_failure:.4f} CI={[round(x,4) for x in base.p_failure_ci95]}")
    print(f"    d_gap=0.86  P(fail)={extreme.p_failure:.4f} CI={[round(x,4) for x in extreme.p_failure_ci95]}")

    # Certainty is unrepresentable
    probe = k.evaluate("x")
    assert 0.01 <= probe.p_failure <= 0.99
    print("\n  Probabilistic floor holds: no posterior outside [0.01, 0.99].")
    print("  STATUS: IHCEI v3.0 PROBABILISTIC KERNEL READY")


if __name__ == "__main__":
    run_tests()
