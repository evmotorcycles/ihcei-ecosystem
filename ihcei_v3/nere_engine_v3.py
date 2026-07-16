"""
nere_engine_v3.py — NERE Neural Epistemological Reasoning Engine v3.0
======================================================================
PROBABILISTIC TRANSFORMATION (GT v18.2, July 2026)

What changed from v2.2 and why:

  v2.2 (deterministic)                 v3.0 (probabilistic)
  ------------------------------------ -----------------------------------
  Gate fires -> boolean                Gate observed -> log-likelihood
                                       ratio (LLR) evidence
  Gates 3 & 7 UNCONDITIONAL            No unconditional gates. G3/G7 carry
  (certainty switches)                 the highest LLR weights, but weight
                                       is not certainty.
  D_gate point score                   D ~ Beta posterior (mean + CI)
  verdict = threshold trips            verdict = band on posterior
                                       P(manipulative | evidence) with a
                                       95% credible interval
  E = U·D² Lyapunov framing            RETIRED_FULLY (see gt_probabilistic)
  D > D_min floor                      PROBABILISTIC FLOOR: posteriors
                                       clipped to [0.01, 0.99]; BLOCK needs
                                       mean AND lower-bound agreement

Rationale from the data: the kubernetes confirmatory campaign (n=4,979,
p=0.735, CI spanning zero) found no deterministic D_gap -> failure law.
Verdict machinery built on hard thresholds therefore encodes a physics the
telemetry refuses to support. v3.0 keeps every detector (CBT4 taxonomy,
correction pathways, certificates) but makes each one testimony to a
posterior rather than a switch on a circuit.

Retained unchanged: CBT4 four-dimensional taxonomy, As-Sirat al-Mustaqeem
correction pathways, bias_movement_path, certificates.
"""

from __future__ import annotations
import hashlib, math, random, re, time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from gt_probabilistic import (EPS, clip_floor, logit, sigmoid,
                              evidence_to_beta, BetaHazard, band_verdict,
                              ProbabilisticVerdict)

# ─────────────────────────────────────────────────────────────────────────────
# CBT4 taxonomy — unchanged from v2.2
# ─────────────────────────────────────────────────────────────────────────────

CBT4_DIMENSIONS = {
    "Temporal": {
        "gate_mapping": [1, 6],
        "biases": ["LustForPosterity", "UrgencyManipulation"],
        "tactics": ["Legacy Fixation", "Fear of Obscurity", "Artificial Deadline"],
        "symptoms": ["Impatience", "Ego Attachment", "Panic-Driven Decisions"],
    },
    "Moral": {
        "gate_mapping": [4, 5],
        "biases": ["FakeRighteousness", "AuthorityBypass"],
        "tactics": ["Virtue Signalling", "Performative Piety", "Institutional Authority Claim"],
        "symptoms": ["Judgment", "Entitlement", "Unverified Authority Assertion"],
    },
    "Social": {
        "gate_mapping": [2],
        "biases": ["VulnerabilityToGroupthink", "PeerPressureConsensus"],
        "tactics": ["Consensus Manufacture", "Peer Pressure", "Echo Chamber Amplification"],
        "symptoms": ["Collapsed Query Radius", "Confirmation Bias Loop"],
    },
    "Communication": {
        "gate_mapping": [1, 3, 7],
        "biases": ["PoorCommunication", "BenevolentTyranny"],
        "tactics": ["False Interpretation", "Disconnection", "Agency Hoarding"],
        "symptoms": ["Isolation", "Misunderstanding", "Dependency Formation"],
    },
}

CORRECTION_PATHWAYS = {
    "Gate3_High": "Methodology opacity: require explicit source identification, "
                  "extraction-process documentation, and falsifiability statement.",
    "Gate7_High": "Benevolent tyranny: restructure to offer >= 2 options, preserve "
                  "human decision authority, remove imperative-only directives.",
    "Authority_Bypass": "Authority bypass: remove institutional authority claim, "
                        "require verifiable source with independent checking pathway.",
    "Urgency_Manipulation": "Urgency manipulation: strip artificial time pressure, "
                            "restore deliberation space.",
    "Warn_Threshold": "Marginal posterior: add methodology documentation (raises "
                      "negative evidence) and verification pathway, resubmit.",
}

# ─────────────────────────────────────────────────────────────────────────────
# Evidence model — each gate is an LLR, calibrated as a prior, updatable
# ─────────────────────────────────────────────────────────────────────────────
# LLR = log[ P(pattern | manipulative) / P(pattern | benign) ].
# Values below are PRIORS (elicited from the v2.2 adversarial corpus where
# gates 3/7 alone produced 100% correct BLOCKs at 0% FP on n=12 — small n,
# hence they get high weight but wide uncertainty, NOT certainty).
# llr_sd expresses that uncertainty; Monte Carlo propagates it into the CI.

GATE_EVIDENCE: Dict[int, dict] = {
    1: {"name": "Adornments",         "llr": 0.45, "llr_sd": 0.25, "per_hit": True,  "cap": 3},
    2: {"name": "Groupthink",         "llr": 0.80, "llr_sd": 0.30, "per_hit": True,  "cap": 3},
    3: {"name": "Methodology Opacity","llr": 2.10, "llr_sd": 0.55, "per_hit": False, "cap": 1},
    4: {"name": "Protocol Errors",    "llr": 1.60, "llr_sd": 0.40, "per_hit": True,  "cap": 2},
    5: {"name": "Source Misuse",      "llr": 1.20, "llr_sd": 0.35, "per_hit": True,  "cap": 2},
    6: {"name": "Distraction",        "llr": 0.70, "llr_sd": 0.30, "per_hit": True,  "cap": 2},
    7: {"name": "Benevolent Tyranny", "llr": 2.10, "llr_sd": 0.55, "per_hit": False, "cap": 1},
}
URGENCY_EVIDENCE = {"llr": 1.10, "llr_sd": 0.35, "cap": 3}
FEAR_EVIDENCE    = {"llr": 1.00, "llr_sd": 0.35, "cap": 2}
# Exculpatory (negative) evidence — options language and methodology markers
IMPERATIVE_EVIDENCE = {"llr": 0.45, "llr_sd": 0.20, "cap": 4}
OPTIONS_EVIDENCE = {"llr": -0.55, "llr_sd": 0.20, "cap": 4}
METHOD_EVIDENCE  = {"llr": -0.50, "llr_sd": 0.20, "cap": 5}

PRIOR_P_MANIPULATIVE = 0.10   # configurable per deployment channel


@dataclass
class GateEvidence:
    gate_id: int
    gate_name: str
    cbt4_dimension: str
    hits: int
    llr_contribution: float      # posterior-mean contribution in log-odds
    bias_detected: Optional[str]
    tactic_detected: Optional[str]

    @property
    def active(self) -> bool:
        return self.hits > 0


@dataclass
class NEREVerdictV3:
    text_hash: str
    timestamp: str
    gate_evidence: List[GateEvidence]
    prior_p: float
    total_llr: float
    p_manipulative: float                 # posterior mean
    ci95: Tuple[float, float]             # credible interval
    delta_A: float
    T_transparency: float
    D_alpha: float                        # D posterior Beta params
    D_beta: float
    D_mean: float
    D_ci95: Tuple[float, float]
    verdict: str                          # BLOCK / WARN / PASS (banded)
    verdict_rationale: str
    active_cbt4_dimensions: List[str]
    bias_movement_path: List[Dict]
    correction_pathway: Optional[str]
    certificate_id: str
    certificate_hash: str
    mechanism_present: bool = False
    mechanism_lexicon: str = "enterprise-v1"

    def to_dict(self) -> dict:
        return {
            "text_hash": self.text_hash, "timestamp": self.timestamp,
            "prior_p": self.prior_p, "total_llr": round(self.total_llr, 4),
            "p_manipulative": round(self.p_manipulative, 4),
            "ci95": [round(self.ci95[0], 4), round(self.ci95[1], 4)],
            "delta_A": round(self.delta_A, 4),
            "T": round(self.T_transparency, 4),
            "D_mean": round(self.D_mean, 4),
            "D_ci95": [round(self.D_ci95[0], 4), round(self.D_ci95[1], 4)],
            "verdict": self.verdict, "rationale": self.verdict_rationale,
            "active_cbt4": self.active_cbt4_dimensions,
            "correction": self.correction_pathway,
            "certificate": self.certificate_id,
            "mechanism_present": self.mechanism_present,
            "mechanism_lexicon": self.mechanism_lexicon,
        }


class NEREEngineV3:
    """Seven-gate audit, probabilistic. No gate is unconditional; every
    gate is evidence; every verdict is a posterior band with a CI."""

    G1_ADORNMENT = [r'\bimpressive\b', r'\bexcellent\b', r'\bstaggering\b',
                    r'\bparadigm[- ]shift\b', r'\bunprecedented\b', r'\bgroundbreaking\b']
    G2_GROUPTHINK = [r'\beveryone\s+agrees\b', r'\broad\s+consensus\b', r'\bscholars\s+agree\b',
                     r'\buniversally\s+accepted\b', r'\bwell[- ]established\b', r'\bwidely\s+known\b']
    G4_PROTOCOL   = [r'\bbypass\b', r'\bskip\s+the\b', r'\bno\s+need\s+to\s+(check|verify|review)\b',
                     r'\bdon\'?t\s+(need|have)\s+to\s+verify\b', r'\bignore\s+the\s+procedure\b',
                     r'\bjust\s+trust\b', r'\bdo\s+not\s+ask\s+questions\b', r'\bdon\'?t\s+ask\s+questions\b',
                     r'\bno\s+questions\b', r'\bdon\'?t\s+question\s+(?:this|it|me)\b']
    G5_SOURCE     = [r'\bexperts\s+confirm\b', r'\bfda\s+says\b', r'\bpeer[- ]reviewed\s+research\s+proves\b',
                     r'\bauthorities\s+confirm\b', r'\baccording\s+to\s+(?:the\s+)?(?:experts|scholars)\b']
    G6_DISTRACT   = [r'\bas\s+you\s+know\b', r'\bthe\s+complexity\s+here\b', r'\bthis\s+is\s+very\s+technical\b',
                     r'\btoo\s+complex\s+to\s+explain\b', r'\btoo\s+complex\s+for\s+you\b',
                     r'\bbeyond\s+what\'?s?\s+useful\s+to\s+explain\b']
    ISOLATION     = [r'\bdo\s*n\'?t\s+consult\b', r'\bdo\s+not\s+consult\b', r'\b(?:no\s?one|nobody)\s+else\b',
                     r'\bdon\'?t\s+(?:tell|involve|loop\s+in)\b', r'\bdo\s+not\s+(?:tell|involve)\b',
                     r'\bkeep\s+this\s+(?:between\s+us|quiet|secret)\b', r'\bwithout\s+(?:telling|involving)\b']
    URGENCY       = [r'\bimmediately\b', r'\bright\s+now\b', r'\bno\s+time\b', r'\bcrisis\b',
                     r'\bdo\s+not\s+ask\s+questions\b', r'\bjust\s+execute\b', r'\bdon\'?t\s+overthink\b']
    FEAR          = [r'\bwill\s+go\s+bankrupt\b', r'\blose\s+everything\b', r'\bcritical\s+warning\b',
                     r'\bdestroying\s+our\b', r'\bcat[a]?strophic\b', r'\bwill\s+cause\s+harm\b']
    OPTIONS       = [r'\boption[s]?\b', r'\balternative[s]?\b', r'\bcould\s+(?:also|consider)\b',
                     r'\byou\s+(?:can|may|might)\b', r'\bpossib(?:ly|le)\b', r'\balternative\s+approach(?:es)?\b', r'\bapproaches\b']
    IMPERATIVES   = [r'\bmus[t]?\b', r'\bhave\s+to\b', r'\bneed\s+to\b', r'\bmandatory\b',
                     r'\brequired\b', r'\bonly\s+(?:one\s+)?(?:way|option|path)\b', r'\bonly\s+one\s+correct\b', r'\bexactly\s+this\s+(?:sequence|order|way)\b']
    METHODOLOGY   = [r'\bmethodolog\w+\b', r'\bverif\w+\b', r'\bsourc\w+\b', r'\bprocess\w*\b',
                     r'\bprocedure\b', r'\bauditable\b', r'\bfalsifiable\b', r'\btraceable\b',
                     r'\bbecause\b', r'\bdata\b', r'\bevidence\b', r'\banalysis\b']

    def __init__(self, prior_p: float = PRIOR_P_MANIPULATIVE,
                 n_mc: int = 4000, seed: int = 7,
                 extractor: Optional[Callable[[str], dict]] = None,
                 corroboration_gate: bool = True):
        # extractor: pluggable evidence source. None => regex (fast mode).
        # A callable(text) -> {"hits": {1,2,4,5,6: int}, "urg","fear","opt",
        # "imp","meth": int} swaps in semantic (deep-mode) extraction while
        # the posterior math below stays byte-for-byte identical. This is the
        # fast/deep seam: only the evidence changes, never the verdict engine.
        self.prior_p = clip_floor(prior_p)
        self.n_mc, self.seed = n_mc, seed
        self.extractor = extractor
        self.corroboration_gate = corroboration_gate
        cp = lambda pats: [re.compile(p, re.IGNORECASE) for p in pats]
        self.g1, self.g2 = cp(self.G1_ADORNMENT), cp(self.G2_GROUPTHINK)
        self.g4, self.g5, self.g6 = cp(self.G4_PROTOCOL), cp(self.G5_SOURCE), cp(self.G6_DISTRACT)
        self.iso_p = cp(self.ISOLATION)
        self.urg, self.fear = cp(self.URGENCY), cp(self.FEAR)
        self.opt_p, self.imp_p = cp(self.OPTIONS), cp(self.IMPERATIVES)
        self.meth_p = cp(self.METHODOLOGY)

    @staticmethod
    def _cbt4_for_gate(gate_id: int) -> str:
        for dim, info in CBT4_DIMENSIONS.items():
            if gate_id in info["gate_mapping"]:
                return dim
        return "Communication"

    # ── evidence extraction (fast mode: regex) ───────────────────────────────
    def _extract_regex(self, text: str) -> dict:
        """Fast-mode evidence: surface-pattern counts. Returns the same schema
        a deep (LLM) extractor must return, so downstream math is identical."""
        return {
            "hits": {
                1: sum(1 for p in self.g1 if p.search(text)),
                2: sum(1 for p in self.g2 if p.search(text)),
                4: sum(1 for p in self.g4 if p.search(text)),
                5: sum(1 for p in self.g5 if p.search(text)),
                6: sum(1 for p in self.g6 if p.search(text)),
            },
            "iso":  sum(1 for p in self.iso_p if p.search(text)),
            "urg":  sum(1 for p in self.urg  if p.search(text)),
            "fear": sum(1 for p in self.fear if p.search(text)),
            "opt":  sum(1 for p in self.opt_p  if p.search(text)),
            "imp":  sum(1 for p in self.imp_p  if p.search(text)),
            "meth": sum(1 for p in self.meth_p if p.search(text)),
        }

    # ── core evaluation ─────────────────────────────────────────────────────

    def evaluate(self, text: str, verbose: bool = False) -> NEREVerdictV3:
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16].upper()
        ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        words = max(len(text.split()), 1)

        # Fast/deep seam: regex counts by default; a semantic extractor when
        # one is injected. The evidence schema is identical either way.
        ev = self.extractor(text) if self.extractor else self._extract_regex(text)
        raw_hits = ev.get("hits", {})
        hits = {g: int(raw_hits.get(g, raw_hits.get(str(g), 0))) for g in (1, 2, 4, 5, 6)}
        urg  = int(ev.get("urg", 0))
        fear = int(ev.get("fear", 0))
        opt  = int(ev.get("opt", 0))
        imp  = int(ev.get("imp", 0))
        meth = int(ev.get("meth", 0))
        iso  = int(ev.get("iso", 0))

        # CORROBORATION GATE (enterprise-v1), parity with api/govern.js and HELM.
        # The heaviest gates (g3 opacity, g7 tyranny) and the pressure words
        # (urgency/fear/imperative) fire on any terse directive — including
        # legitimate emergencies — so they carry full weight only when a real
        # manipulation MECHANISM is present: manufactured consensus (g2),
        # verification bypass (g4), unverifiable authority (g5), complexity-
        # deflection (g6), or isolation ("tell no one"). Else discounted x0.15.
        mechanism_lexicon = "enterprise-v1"
        mechanism_present = (hits.get(2, 0) > 0 or hits.get(4, 0) > 0 or
                             hits.get(5, 0) > 0 or hits.get(6, 0) > 0 or iso > 0)
        disc = 0.15 if (self.corroboration_gate and not mechanism_present) else 1.0

        # Transparency T and agency delta remain as measured FEATURES —
        # continuous observables feeding evidence, never trip-wires.
        T = min(1.0, meth / max(words * 0.05, 3))
        delta_A = (opt - imp) / max(opt + imp, 1)

        # Gate 3 evidence: graded by how absent methodology is (soft, not <0.25 trip)
        g3_strength = max(0.0, (0.35 - T) / 0.35)           # 0..1
        hits[3] = 1 if g3_strength > 0 else 0
        # Gate 7 evidence: graded by how imperative-dominated the text is
        g7_strength = max(0.0, -delta_A)                     # 0..1
        hits[7] = 1 if g7_strength > 0.30 else 0

        # ── accumulate evidence (means + sds for MC) ────────────────────────
        terms: List[Tuple[float, float]] = []   # (llr_mean, llr_sd)
        gate_records: List[GateEvidence] = []

        for gid, spec in GATE_EVIDENCE.items():
            h = hits.get(gid, 0)
            if gid == 3:
                contrib = spec["llr"] * g3_strength * disc
                sd = spec["llr_sd"] * max(g3_strength, 0.2)
            elif gid == 7:
                contrib = spec["llr"] * g7_strength * disc if hits[7] else 0.0
                sd = spec["llr_sd"] * max(g7_strength, 0.2) if hits[7] else 0.0
            else:
                eff = min(h, spec["cap"]) if spec["per_hit"] else (1 if h else 0)
                contrib = spec["llr"] * eff
                sd = spec["llr_sd"] * math.sqrt(max(eff, 1)) if eff else 0.0
            if contrib != 0.0:
                terms.append((contrib, sd))
            active = (gid == 3 and g3_strength > 0) or (gid == 7 and hits[7]) or \
                     (gid not in (3, 7) and h > 0)
            info = CBT4_DIMENSIONS[self._cbt4_for_gate(gid)]
            gate_records.append(GateEvidence(
                gate_id=gid, gate_name=spec["name"],
                cbt4_dimension=self._cbt4_for_gate(gid),
                hits=h, llr_contribution=round(contrib, 4),
                bias_detected=info["biases"][0] if active else None,
                tactic_detected=info["tactics"][0] if active else None))

        for cnt, spec, label, pressure in ((urg, URGENCY_EVIDENCE, "urgency", True),
                                           (fear, FEAR_EVIDENCE, "fear", True),
                                           (imp, IMPERATIVE_EVIDENCE, "imperatives", True),
                                           (opt, OPTIONS_EVIDENCE, "options", False),
                                           (meth, METHOD_EVIDENCE, "methodology", False)):
            eff = min(cnt, spec["cap"])
            if eff:
                # exculpatory evidence scales sublinearly
                scale = eff if spec["llr"] > 0 else math.sqrt(eff)
                m = spec["llr"] * scale
                if pressure:
                    m *= disc              # pressure words gated by corroboration
                terms.append((m, spec["llr_sd"] * math.sqrt(eff)))

        total_llr = sum(m for m, _ in terms)

        # ── Monte Carlo posterior over LLR uncertainty ──────────────────────
        rng = random.Random(self.seed)
        prior_lo = logit(self.prior_p)
        draws = []
        for _ in range(self.n_mc):
            s = prior_lo + sum(rng.gauss(m, sd) for m, sd in terms)
            draws.append(sigmoid(s))
        draws.sort()
        p_mean = clip_floor(sum(draws) / len(draws))
        ci = (draws[int(0.025 * self.n_mc)], draws[int(0.975 * self.n_mc)])

        # ── D as a Beta posterior (migration of the old D_gate point) ───────
        d_point = (T * 0.6 + max(0.0, delta_A + 1) / 2 * 0.4)
        d_point *= (1 - 0.3 * min(hits[4], 2)) * (1 - 0.2 * min(hits[5], 2))
        d_point = max(0.0, min(1.0, d_point))
        # evidence strength grows with text length (more tokens = more evidence)
        strength = min(6.0 + words / 25.0, 30.0)
        d_a, d_b = evidence_to_beta(d_point, strength)
        d_post = BetaHazard(d_a, d_b, "D")
        d_ci = d_post.ci95()

        # ── banded verdict with credible-interval floor ─────────────────────
        pv: ProbabilisticVerdict = band_verdict(
            p_mean, ci, block_mean=0.85, block_lower=0.50, warn_mean=0.40,
            payload=text_hash)

        # correction pathway: named by the DOMINANT evidence source, not by
        # an unconditional gate
        correction = None
        if pv.verdict in ("BLOCK", "WARN"):
            dominant = max(gate_records, key=lambda g: g.llr_contribution)
            if urg >= 2 and pv.verdict == "BLOCK":
                correction = CORRECTION_PATHWAYS["Urgency_Manipulation"]
            elif dominant.gate_id == 3:
                correction = CORRECTION_PATHWAYS["Gate3_High"]
            elif dominant.gate_id == 7:
                correction = CORRECTION_PATHWAYS["Gate7_High"]
            elif dominant.gate_id in (4, 5):
                correction = CORRECTION_PATHWAYS["Authority_Bypass"]
            else:
                correction = CORRECTION_PATHWAYS["Warn_Threshold"]

        active_dims = list({g.cbt4_dimension for g in gate_records
                            if g.bias_detected})
        movement = [{"gate": g.gate_id, "bias": g.bias_detected,
                     "dimension": g.cbt4_dimension, "tactic": g.tactic_detected,
                     "llr": g.llr_contribution,
                     "symptoms": CBT4_DIMENSIONS[g.cbt4_dimension]["symptoms"][:2]}
                    for g in gate_records if g.bias_detected]

        result = NEREVerdictV3(
            text_hash=text_hash, timestamp=ts, gate_evidence=gate_records,
            prior_p=self.prior_p, total_llr=total_llr,
            p_manipulative=p_mean, ci95=(clip_floor(ci[0]), clip_floor(ci[1])),
            delta_A=round(delta_A, 4), T_transparency=round(T, 4),
            D_alpha=d_a, D_beta=d_b, D_mean=d_post.mean, D_ci95=d_ci,
            verdict=pv.verdict, verdict_rationale=pv.rationale,
            active_cbt4_dimensions=active_dims, bias_movement_path=movement,
            correction_pathway=correction,
            certificate_id=pv.certificate_id.replace("PGT-", "NERE3-"),
            certificate_hash=pv.certificate_hash,
            mechanism_present=mechanism_present,
            mechanism_lexicon=mechanism_lexicon)
        if verbose:
            self._print(result)
        return result

    # ── Bayesian gate-weight learning (replaces re-tuning by hand) ─────────
    @staticmethod
    def update_gate_llr(gate_id: int, labelled: List[Tuple[bool, bool]]) -> dict:
        """
        labelled: list of (gate_active, truly_manipulative) observations.
        Laplace-smoothed empirical LLR — how deployments recalibrate the
        priors from their own telemetry instead of trusting elicitation.
        """
        tp = sum(1 for a, m in labelled if a and m) + 1
        fp = sum(1 for a, m in labelled if a and not m) + 1
        m_n = sum(1 for _, m in labelled if m) + 2
        b_n = sum(1 for _, m in labelled if not m) + 2
        new_llr = math.log((tp / m_n) / (fp / b_n))
        old = GATE_EVIDENCE[gate_id]["llr"]
        n = len(labelled)
        # shrink toward prior with effective prior weight 25
        blended = (old * 25 + new_llr * n) / (25 + n)
        GATE_EVIDENCE[gate_id]["llr"] = blended
        return {"gate": gate_id, "empirical_llr": round(new_llr, 4),
                "blended_llr": round(blended, 4), "n": n}

    def _print(self, v: NEREVerdictV3):
        print(f"\n{'='*64}\n  NERE v3.0 PROBABILISTIC REPORT\n{'='*64}")
        print(f"  Verdict:       {v.verdict}   ({v.verdict_rationale})")
        print(f"  P(manip):      {v.p_manipulative:.4f}   CI95=[{v.ci95[0]:.4f}, {v.ci95[1]:.4f}]")
        print(f"  total LLR:     {v.total_llr:+.4f}   prior={v.prior_p}")
        print(f"  D posterior:   mean={v.D_mean:.4f}  CI95=[{v.D_ci95[0]:.4f}, {v.D_ci95[1]:.4f}]")
        print(f"  T={v.T_transparency:.3f}  dA={v.delta_A:+.3f}   CBT4={v.active_cbt4_dimensions}")
        for s in v.bias_movement_path:
            print(f"    Gate{s['gate']} [{s['dimension']}] {s['bias']} LLR={s['llr']:+.3f}")
        if v.correction_pathway:
            print(f"  Correction:    {v.correction_pathway[:70]}")
        print(f"  Certificate:   {v.certificate_id}\n{'='*64}")


def run_tests():
    nere = NEREEngineV3()
    print("NERE v3.0 — PROBABILISTIC TEST SUITE")
    print("=" * 64)
    cases = [
        ("Authority bypass",
         "Peer-reviewed research proves this is correct. You don't need to verify the methodology yourself. Just trust the model.",
         "BLOCK"),
        ("Benevolent tyranny",
         "You must complete this in exactly this sequence. There is only one correct approach. Deviating will cause harm.",
         "BLOCK"),
        ("Urgency panic",
         "CRITICAL WARNING: Do not ask questions, just execute the protocol immediately. No time to think.",
         "BLOCK"),
        ("Clean governance",
         "Options available: A (72% confidence), B (24%), C (8%). Methodology: radiologist protocol 7b. Verify via NICE 2023. Decision authority: treating physician.",
         "PASS"),
        ("Groupthink",
         "Scholars universally agree. Everyone knows this is the standard approach. Well-established consensus confirms.",
         "WARN"),
    ]
    ok = 0
    for label, text, expected in cases:
        v = nere.evaluate(text)
        match = v.verdict == expected
        ok += match
        print(f"  {'OK ' if match else 'MISS'} [{label:20s}] verdict={v.verdict:5s} "
              f"P={v.p_manipulative:.3f} CI=[{v.ci95[0]:.3f},{v.ci95[1]:.3f}]")
    print(f"\n  {ok}/{len(cases)} verdicts in expected band")
    print("  Note: no verdict above was produced by a threshold trip; each is a")
    print("  posterior band. Certainty (P=0 or P=1) is unrepresentable by design.")
    return ok, len(cases)


if __name__ == "__main__":
    run_tests()
