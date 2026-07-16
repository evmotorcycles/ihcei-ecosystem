"""
gt_probabilistic.py — GT v18.2 Probabilistic Core (IHCEI v3.0)
================================================================
THE NULL-RESULT PIVOT (July 2026)

Confirmatory evidence (pre-registered, kubernetes/kubernetes, PRs 1-50 pages):
    n = 4,979 human-authored PRs, 1,584 failures (base hazard 0.3181)
    D_gap coefficient = +0.1939, 95% CI [-0.9286, +1.3164], p = 0.735
    Robustness (unpressed): +0.0218, CI [-1.1666, +1.2102], p = 0.971
    VERDICT: [NO SIGNAL] — twice, pressed and unpressed.

Exploratory evidence (microsoft/vscode, n = 3,685, 601 failures, base 0.1631):
    Univariate logit: D_gap -> merge coef = -1.9661, p = 0.0012.
    NOT confirmatory: 77% of rows sit at D_gap == 0 (degenerate mass),
    multivariate fit separates (p = nan). Per the epistemic firewall,
    the pre-registered kubernetes test governs. Logged, not promoted.

WHAT THE NULL LICENSES (and what it does not):
  LICENSED   : Retiring every deterministic D-threshold claim. A hard law
               "D_gap > x  =>  failure" predicts signal; none appeared at
               n = 4,979. Deterministic D-gates are dead as descriptive OR
               prescriptive physics.
  LICENSED   : Modeling channel outcomes as base-rate stochastic processes
               in which D-variables enter as covariates whose coefficient
               priors are CENTERED ON THE MEASURED NULL.
  NOT LICENSED (Layer-3 honesty): the null does not positively prove
               "reality is probabilistic." Absence of a deterministic
               signal is consistent with probabilistic dynamics; it is
               also consistent with unmeasured deterministic causes.
               We adopt the probabilistic model because it is the one
               the data does not contradict. Status: SUPPORTED-BY-NULL.

RETIREMENTS (v3.0 — full, not partial):
  E = U·D²          RETIRED_FULLY. No longer a descriptive law (v2.3
                    already retired that) and no longer a "prescriptive
                    Lyapunov floor" either. The kernel keeps NO quantity
                    computed as U*D*D.
  D > D_min         RETIRED_FULLY. No hard fidelity threshold anywhere.
                    Replaced by the PROBABILISTIC FLOOR (below).
  UNCONDITIONAL     RETIRED. NERE Gates 3 and 7 are no longer certainty
  GATES             switches; they are high-weight evidence.

THE PROBABILISTIC FLOOR (replaces D_min):
  1. Epistemic floor  : no posterior is ever reported as 0.0 or 1.0.
                        All probabilities are clipped to [EPS, 1-EPS].
                        The system is structurally incapable of claiming
                        certainty — that IS the floor.
  2. Base-rate floor  : every channel carries an irreducible Beta-
                        distributed failure hazard calibrated from
                        telemetry. No D value drives P(fail) to 0.
  3. Verdict floor    : BLOCK/WARN/PASS are bands on the POSTERIOR with
                        credible intervals, never point-threshold trips.

Expected-essence replaces essence law:
  E[E] = U · E[D | evidence]     (transmission regime, SUPPORTED linear
                                  form retained as an EXPECTATION, with a
                                  full posterior on D — never a point)
"""

from __future__ import annotations
import hashlib, math, time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# 0. Constants: the probabilistic floor
# ─────────────────────────────────────────────────────────────────────────────

EPS = 0.01                      # epistemic floor: certainty is unrepresentable
Z95 = 1.959963984540054

def clip_floor(p: float) -> float:
    """Enforce the epistemic floor: p in [EPS, 1-EPS], always."""
    return max(EPS, min(1.0 - EPS, float(p)))

def logit(p: float) -> float:
    p = clip_floor(p)
    return math.log(p / (1.0 - p))

def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x); return clip_floor(1.0 / (1.0 + z))
    z = math.exp(x);      return clip_floor(z / (1.0 + z))


# ─────────────────────────────────────────────────────────────────────────────
# 1. Law registry v3 — statuses after the null
# ─────────────────────────────────────────────────────────────────────────────

class LawStatus:
    SUPPORTED         = "SUPPORTED"           # multi-domain, pre-registered
    SUPPORTED_BY_NULL = "SUPPORTED_BY_NULL"   # adopted because data refutes rival
    HYPOTHESIS        = "HYPOTHESIS"          # post-hoc; locked predictions untested
    RETIRED_FULLY     = "RETIRED_FULLY"       # removed from descriptive AND
                                              # prescriptive service

LAW_REGISTRY: Dict[str, dict] = {
    "E_expected": {
        "form": "E[E] = U * E[D | evidence]",
        "regime": "TRANSMISSION",
        "status": LawStatus.SUPPORTED,
        "note": "Linear transmission form retained as an expectation over a "
                "posterior D distribution. Point-valued D is no longer emitted.",
    },
    "hazard_model": {
        "form": "P(fail | x) = sigma(b0 + b·x),  b0 ~ from Beta base rate, "
                "b_Dgap ~ Normal(0.1939, 0.5727)  [null-centered prior]",
        "regime": "ANY",
        "status": LawStatus.SUPPORTED_BY_NULL,
        "note": "Coefficient prior centered on the measured kubernetes "
                "confirmatory estimate; its CI spans zero, so D_gap carries "
                "~no predictive weight until data moves it.",
    },
    "E_quadratic": {
        "form": "E = U * D**2",
        "status": LawStatus.RETIRED_FULLY,
        "note": "v2.3 kept it as a prescriptive Lyapunov floor; v3.0 removes "
                "it entirely. No kernel quantity is computed as U*D*D.",
    },
    "D_min_threshold": {
        "form": "D > D_min  (hard gate)",
        "status": LawStatus.RETIRED_FULLY,
        "note": "Replaced by the probabilistic floor: posterior bands with "
                "credible intervals; no deterministic trip-wire survives.",
    },
    "correction_pump": {
        "form": "E_c = U * kappa * (1 - D_in) * q",
        "regime": "CORRECTION",
        "status": LawStatus.HYPOTHESIS,
        "note": "Unchanged from v2.3. Predictions P1-P4 remain locked/untested.",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 2. Calibration — priors measured from the July 2026 telemetry
# ─────────────────────────────────────────────────────────────────────────────

CALIBRATION: Dict[str, dict] = {
    "kubernetes_confirmatory": {
        "spec_sha256": "7a74ea544c3e40e4ce81fe1490273e07e9f74458a8d73de465c9bec9a8e17a46",
        "n": 4979, "failures": 1584,
        "d_gap_coef": 0.1939, "d_gap_se": 0.5727,   # SE from CI width / (2*1.96)
        "p_value": 0.735, "verdict": "NO_SIGNAL",
        "role": "CONFIRMATORY — governs the coefficient prior",
    },
    "vscode_exploratory": {
        "n": 3685, "failures": 601,
        "univariate_coef_on_merge": -1.9661, "p_value": 0.0012,
        "degenerate_zero_mass": 0.77,
        "role": "EXPLORATORY — logged, not promoted (epistemic firewall)",
    },
}

class BetaHazard:
    """
    Beta-Bernoulli base-rate hazard for a channel. This IS the base-rate
    floor: the posterior never concentrates at 0 or 1, and its mean is the
    irreducible failure probability no fidelity score can erase.
    """
    def __init__(self, alpha: float = 1.0, beta: float = 1.0, name: str = "uninformed"):
        self.a, self.b, self.name = float(alpha), float(beta), name

    @classmethod
    def from_telemetry(cls, failures: int, n: int, name: str) -> "BetaHazard":
        return cls(alpha=failures + 1.0, beta=(n - failures) + 1.0, name=name)

    def update(self, failures: int, successes: int) -> "BetaHazard":
        return BetaHazard(self.a + failures, self.b + successes, self.name)

    @property
    def mean(self) -> float:
        return clip_floor(self.a / (self.a + self.b))

    @property
    def var(self) -> float:
        s = self.a + self.b
        return (self.a * self.b) / (s * s * (s + 1.0))

    def ci95(self) -> Tuple[float, float]:
        sd = math.sqrt(self.var)
        return (clip_floor(self.mean - Z95 * sd), clip_floor(self.mean + Z95 * sd))

    def to_dict(self) -> dict:
        lo, hi = self.ci95()
        return {"name": self.name, "alpha": round(self.a, 2), "beta": round(self.b, 2),
                "mean": round(self.mean, 4), "ci95": [round(lo, 4), round(hi, 4)]}

# Channel priors measured from the two campaigns
CHANNEL_PRIORS: Dict[str, BetaHazard] = {
    "kubernetes": BetaHazard.from_telemetry(1584, 4979, "kubernetes"),
    "vscode":     BetaHazard.from_telemetry(601, 3685, "vscode"),
    # Pooled hierarchical-ish prior for unknown OSS channels (weakly informed:
    # scaled to an effective n of 40 so new telemetry dominates quickly)
    "oss_default": BetaHazard(alpha=1 + 40 * (2185 / 8664), beta=1 + 40 * (1 - 2185 / 8664),
                              name="oss_default"),
}


# ─────────────────────────────────────────────────────────────────────────────
# 3. Posterior hazard — the replacement for every deterministic D law
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class HazardPosterior:
    p_mean: float
    ci95: Tuple[float, float]
    base_rate: float
    covariate_contribution_logodds: float
    prior: str
    floor_applied: bool

    def to_dict(self) -> dict:
        return {"p_fail_mean": round(self.p_mean, 4),
                "ci95": [round(self.ci95[0], 4), round(self.ci95[1], 4)],
                "base_rate": round(self.base_rate, 4),
                "covariate_logodds": round(self.covariate_contribution_logodds, 4),
                "prior": self.prior, "floor_applied": self.floor_applied}


def hazard_posterior(d_gap: float = 0.0,
                     channel: str = "oss_default",
                     extra_logodds: float = 0.0,
                     n_mc: int = 4000,
                     seed: int = 7) -> HazardPosterior:
    """
    P(fail | D_gap, channel) with FULL uncertainty propagation:
      - base rate ~ Beta posterior (channel prior)
      - b_Dgap    ~ Normal(0.1939, 0.5727)   <- the measured null, as a prior
    Monte Carlo over both. Because the coefficient prior straddles zero, a
    large D_gap widens the credible interval instead of moving the verdict —
    which is exactly what a null result should do.
    """
    import random
    rng = random.Random(seed)
    prior = CHANNEL_PRIORS.get(channel, CHANNEL_PRIORS["oss_default"])
    cal = CALIBRATION["kubernetes_confirmatory"]
    mu_b, sd_b = cal["d_gap_coef"], cal["d_gap_se"]

    draws: List[float] = []
    for _ in range(n_mc):
        p0 = clip_floor(rng.betavariate(prior.a, prior.b))
        b  = rng.gauss(mu_b, sd_b)
        draws.append(sigmoid(logit(p0) + b * d_gap + extra_logodds))
    draws.sort()
    mean = sum(draws) / len(draws)
    lo, hi = draws[int(0.025 * n_mc)], draws[int(0.975 * n_mc)]
    return HazardPosterior(
        p_mean=clip_floor(mean), ci95=(clip_floor(lo), clip_floor(hi)),
        base_rate=prior.mean,
        covariate_contribution_logodds=mu_b * d_gap + extra_logodds,
        prior=prior.name, floor_applied=True)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Expected essence — E[E] = U · E[D], posterior form
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EssencePosterior:
    e_mean: float
    ci95: Tuple[float, float]
    d_mean: float
    d_ci95: Tuple[float, float]
    law: str = "E[E] = U * E[D | evidence]  (TRANSMISSION, SUPPORTED)"

    def to_dict(self) -> dict:
        return {"E_mean": round(self.e_mean, 4),
                "E_ci95": [round(self.ci95[0], 4), round(self.ci95[1], 4)],
                "D_mean": round(self.d_mean, 4),
                "D_ci95": [round(self.d_ci95[0], 4), round(self.d_ci95[1], 4)],
                "law": self.law}


def expected_essence(U: float, d_alpha: float, d_beta: float) -> EssencePosterior:
    """
    D is a Beta(d_alpha, d_beta) random variable — never a point.
    E is linear in D (the SUPPORTED transmission form), so the posterior
    on E is just U times the posterior on D. Nothing here is squared:
    E = U·D² is RETIRED_FULLY and does not appear in this codebase's math.
    """
    d = BetaHazard(d_alpha, d_beta, "D_posterior")
    lo, hi = d.ci95()
    return EssencePosterior(e_mean=U * d.mean, ci95=(U * lo, U * hi),
                            d_mean=d.mean, d_ci95=(lo, hi))


def evidence_to_beta(point_estimate: float, evidence_strength: float = 12.0
                     ) -> Tuple[float, float]:
    """
    Convert a legacy point D score in [0,1] plus an evidence-strength
    (pseudo-count) into Beta parameters. This is the migration shim:
    every place the old kernel produced `D = 0.62`, v3.0 produces
    Beta(0.62*s + 1, 0.38*s + 1) instead.
    """
    p = max(0.0, min(1.0, point_estimate))
    return (p * evidence_strength + 1.0, (1.0 - p) * evidence_strength + 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Verdict bands — the verdict floor
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ProbabilisticVerdict:
    verdict: str                 # BLOCK / WARN / PASS
    p_mean: float
    ci95: Tuple[float, float]
    rationale: str
    certificate_id: str = ""
    certificate_hash: str = ""

    def to_dict(self) -> dict:
        d = asdict(self); d["ci95"] = [round(self.ci95[0], 4), round(self.ci95[1], 4)]
        d["p_mean"] = round(self.p_mean, 4)
        return d


def band_verdict(p_mean: float, ci: Tuple[float, float],
                 block_mean: float = 0.85, block_lower: float = 0.50,
                 warn_mean: float = 0.40, payload: str = "") -> ProbabilisticVerdict:
    """
    BLOCK requires BOTH a high posterior mean AND a lower credible bound
    above block_lower — a wide interval (i.e., genuine uncertainty) cannot
    trip a BLOCK on its own. That asymmetry is the verdict floor: the
    system must be confident to act deterministically, and confidence is
    a property of the whole posterior, not of a point.
    """
    p_mean = clip_floor(p_mean); lo, hi = clip_floor(ci[0]), clip_floor(ci[1])
    if p_mean >= block_mean and lo >= block_lower:
        v, why = "BLOCK", (f"posterior mean {p_mean:.3f} >= {block_mean} and "
                           f"lower 95% bound {lo:.3f} >= {block_lower}")
    elif p_mean >= warn_mean or hi >= block_mean:
        v, why = "WARN", (f"posterior mean {p_mean:.3f} in warn band or upper "
                          f"bound {hi:.3f} reaches block region — uncertainty "
                          f"is resolved toward caution, not toward certainty")
    else:
        v, why = "PASS", f"posterior mean {p_mean:.3f} below warn band {warn_mean}"
    ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    pay = f"{ts}|{v}|{p_mean:.4f}|{lo:.4f}|{hi:.4f}|{payload}"
    cid = "PGT-" + hashlib.sha256(pay.encode()).hexdigest()[:8].upper()
    ch  = hashlib.sha256((cid + pay).encode()).hexdigest()
    return ProbabilisticVerdict(v, p_mean, (lo, hi), why, cid, ch)


def registry_report() -> str:
    lines = ["GT v18.2 LAW REGISTRY (post null-result pivot)"]
    for k, v in LAW_REGISTRY.items():
        lines.append(f"  [{v['status']:>17}] {k}: {v['form']}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(registry_report())
    print("\nChannel priors (base-rate floor):")
    for k, p in CHANNEL_PRIORS.items():
        print(f"  {p.to_dict()}")
    print("\nNull-in-action demo — same base rate, extreme D_gap values:")
    for dg in (0.0, 0.5, -0.5, 0.86):
        h = hazard_posterior(d_gap=dg, channel="kubernetes")
        print(f"  D_gap={dg:+.2f}  ->  P(fail)={h.p_mean:.4f}  CI={h.to_dict()['ci95']}")
