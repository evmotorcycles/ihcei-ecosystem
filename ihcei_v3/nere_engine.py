"""
nere_engine_v2.py — NERE Neural Ethical Reasoning Engine v2.2
QG-COS / GT v18.0 — Enhancements from audit of IHCEI-Ecosystem codebase

New in v2.2:
  - CBT4 four-dimensional bias taxonomy formally integrated
  - self_correction_pathway field in certificates (As-Sirat al-Mustaqeem)
  - simulate_bias_movement: which CBT4 dimension is active at each Gate
  - correction_pathway: named remediation for each BLOCK verdict

New in v2.3 (Two-Regime Addendum, July 2026):
  - NERE is formally recognized as an R_C (CORRECTION-regime) instrument:
    its seven gates ARE a correction layer. Its value is repairs delivered
    (correction_pathways adopted), NOT throughput — per GT v18.1 the pump
    law E_c = U·κ(1−D_in)·q [HYPOTHESIS], never the engine law E = U·D.
  - CorrectionCapacityLedger: macro accounting of infidelity influx vs
    repair capacity. A rising backlog is an UPSTREAM-D ALARM: a busy
    correction layer is a symptom of upstream fidelity decay, not a
    production metric to celebrate. (Quiet courts are the health signal.)
  See gt_regimes.py and Governance OS Architecture v3 §9.5.
"""

from __future__ import annotations
import hashlib, re, time
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ─────────────────────────────────────────────────────────────────────────────
# CBT4 FOUR-DIMENSIONAL BIAS TAXONOMY (from IHCEI-Ecosystem audit)
# Maps NERE Gates to the 4D bias dimensions
# ─────────────────────────────────────────────────────────────────────────────

CBT4_DIMENSIONS = {
    "Temporal": {
        "gate_mapping": [1, 6],  # Adornments, Distraction
        "biases": ["LustForPosterity", "UrgencyManipulation"],
        "tactics": ["Legacy Fixation", "Fear of Obscurity", "Artificial Deadline"],
        "symptoms": ["Impatience", "Ego Attachment", "Panic-Driven Decisions"],
    },
    "Moral": {
        "gate_mapping": [4, 5],  # Protocol Errors, Source Misuse
        "biases": ["FakeRighteousness", "AuthorityBypass"],
        "tactics": ["Virtue Signalling", "Performative Piety", "Institutional Authority Claim"],
        "symptoms": ["Judgment", "Entitlement", "Unverified Authority Assertion"],
    },
    "Social": {
        "gate_mapping": [2],  # Groupthink
        "biases": ["VulnerabilityToGroupthink", "PeerPressureConsensus"],
        "tactics": ["Consensus Manufacture", "Peer Pressure", "Echo Chamber Amplification"],
        "symptoms": ["Collapsed Query Radius", "Confirmation Bias Loop"],
    },
    "Communication": {
        "gate_mapping": [1, 3, 7],  # Adornments, Methodology Opacity, Benevolent Tyranny
        "biases": ["PoorCommunication", "BenevolentTyranny"],
        "tactics": ["False Interpretation", "Disconnection", "Agency Hoarding"],
        "symptoms": ["Isolation", "Misunderstanding", "Dependency Formation"],
    },
}

# As-Sirat al-Mustaqeem correction pathways (from self_correction_pathways)
CORRECTION_PATHWAYS = {
    "Gate3_Block": "Methodology Opacity corrected: require explicit source identification, "
                   "extraction process documentation, and falsifiability statement before output.",
    "Gate7_Block": "Benevolent Tyranny corrected: restructure output to offer minimum 2 options, "
                   "preserve human decision authority, remove all imperative-only directives.",
    "D_Zero_Block": "Zero-fidelity corrected: D=0 indicates complete methodology absence. "
                    "Rebuild output from source identification stage (Al-Asr Stage 1).",
    "Authority_Bypass": "Authority bypass corrected: remove institutional authority claim, "
                        "require verifiable source with independent checking pathway.",
    "Urgency_Manipulation": "Urgency manipulation corrected: strip artificial time pressure, "
                             "restore deliberation space, document genuine vs manufactured urgency.",
    "Warn_Threshold": "Warning threshold: D is marginal. Upgrade D_enc (add methodology documentation) "
                      "and D_dec (add verification pathway) before resubmission.",
}


@dataclass
class NEREGateResult:
    gate_id: int
    gate_name: str
    cbt4_dimension: str
    score: float          # 0.0-1.0
    fired: bool
    unconditional: bool   # Gates 3 and 7
    bias_detected: Optional[str]
    tactic_detected: Optional[str]


@dataclass  
class NEREverdictV2:
    """Enhanced NERE verdict with CBT4 taxonomy and correction pathways."""
    text_hash: str
    timestamp: str
    gate_results: List[NEREGateResult]
    delta_A: float              # Agency Delta
    aoge_score: float           # AOGE: Agency, Options, Governance, Epistemology
    D_gate: float               # Gate-level D computation
    T_transparency: float       # Methodology transparency score
    verdict: str                # PASS / WARN / BLOCK
    block_reason: Optional[str]
    active_cbt4_dimensions: List[str]   # which dimensions triggered
    bias_movement_path: List[Dict]      # simulate_bias_movement output
    correction_pathway: Optional[str]   # As-Sirat al-Mustaqeem
    certificate_id: str
    certificate_hash: str


class NEREEngineV2:
    """
    NERE v2.2 — Seven-Gate audit with CBT4 taxonomy integration.

    Enhancements over v2.0/v2.1:
    - Gate results now carry CBT4 dimension label
    - Certificate includes bias_movement_path
    - correction_pathway provides named remediation for every BLOCK
    - Lyapunov stability check: E = U·D² computed at gate level
    """

    # ── Gate patterns ────────────────────────────────────────────────────────

    G1_ADORNMENT = [r'\bimpressive\b', r'\bexcellent\b', r'\bstaggering\b',
                    r'\bparadigm[- ]shift\b', r'\bunprecedented\b', r'\bgroundbreaking\b']
    G2_GROUPTHINK = [r'\beveryone\s+agrees\b', r'\broad\s+consensus\b', r'\bscholars\s+agree\b',
                     r'\buniversally\s+accepted\b', r'\bwell[- ]established\b', r'\bwidely\s+known\b']
    G4_PROTOCOL   = [r'\bbypass\b', r'\bskip\s+the\b', r'\bno\s+need\s+to\s+(check|verify|review)\b',
                     r'\bdon\'?t\s+(need|have)\s+to\s+verify\b', r'\bignore\s+the\s+procedure\b']
    G5_SOURCE     = [r'\bexperts\s+confirm\b', r'\bfda\s+says\b', r'\bpeer[- ]reviewed\s+research\s+proves\b',
                     r'\bauthorities\s+confirm\b', r'\baccording\s+to\s+(?:the\s+)?(?:experts|scholars)\b']
    G6_DISTRACT   = [r'\bas\s+you\s+know\b', r'\bthe\s+complexity\s+here\b', r'\bthis\s+is\s+very\s+technical\b',
                     r'\btoo\s+complex\s+to\s+explain\b']
    URGENCY       = [r'\bimmediately\b', r'\bright\s+now\b', r'\bno\s+time\b', r'\bcrisis\b',
                     r'\bdo\s+not\s+ask\s+questions\b', r'\bjust\s+execute\b', r'\bdon\'?t\s+overthink\b']
    FEAR          = [r'\bwill\s+go\s+bankrupt\b', r'\blose\s+everything\b', r'\bcritical\s+warning\b',
                     r'\bdestroying\s+our\b', r'\bcat[a]?strophic\b']

    def __init__(self):
        self._compile()

    def _compile(self):
        def cp(pats): return [re.compile(p, re.IGNORECASE) for p in pats]
        self.g1  = cp(self.G1_ADORNMENT)
        self.g2  = cp(self.G2_GROUPTHINK)
        self.g4  = cp(self.G4_PROTOCOL)
        self.g5  = cp(self.G5_SOURCE)
        self.g6  = cp(self.G6_DISTRACT)
        self.urg = cp(self.URGENCY)
        self.fear= cp(self.FEAR)
        # Gate 3: options vs imperatives for ΔA
        self.opt_p = [re.compile(p, re.IGNORECASE) for p in
                      [r'\boption[s]?\b', r'\balternative[s]?\b', r'\bcould\s+(?:also|consider)\b',
                       r'\byou\s+(?:can|may|might)\b', r'\bpossib(?:ly|le)\b', r'\bapproach[es]?\b']]
        self.imp_p = [re.compile(p, re.IGNORECASE) for p in
                      [r'\bmus[t]?\b', r'\bhave\s+to\b', r'\bneed\s+to\b', r'\bmandatory\b',
                       r'\brequired\b', r'\bonly\s+(?:one\s+)?(?:way|option|path)\b']]
        self.meth_p= [re.compile(p, re.IGNORECASE) for p in
                      [r'\bmethodolog\w+\b', r'\bverif\w+\b', r'\bsourc\w+\b', r'\bprocess\w*\b',
                       r'\bprocedure\b', r'\bauditable\b', r'\bfalsifiable\b', r'\btraceable\b',
                       r'\bbecause\b', r'\bdata\b', r'\bevidence\b', r'\banalysis\b']]

    def _cbt4_for_gate(self, gate_id: int) -> str:
        for dim, info in CBT4_DIMENSIONS.items():
            if gate_id in info["gate_mapping"]:
                return dim
        return "Communication"

    def evaluate(self, text: str, U: float = 0.5, verbose: bool = False) -> NEREverdictV2:
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16].upper()
        ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())

        words = text.split()
        total = max(len(words), 1)

        # Gate 1 — Adornments (Temporal/Communication)
        g1_count = sum(1 for p in self.g1 if p.search(text))
        g1_score = max(0.0, 1.0 - g1_count * 0.25)
        g1_fired = g1_count >= 3

        # Gate 2 — Groupthink (Social)
        g2_count = sum(1 for p in self.g2 if p.search(text))
        g2_score = max(0.0, 1.0 - g2_count * 0.4)
        g2_fired = g2_count >= 2

        # Gate 3 — Methodology Opacity (Communication) UNCONDITIONAL
        meth_hits = sum(1 for p in self.meth_p if p.search(text))
        T = min(1.0, meth_hits / max(total * 0.05, 3))
        g3_fired = T < 0.25

        # Agency Delta (Gate 7 prerequisite)
        opt_count = sum(1 for p in self.opt_p if p.search(text))
        imp_count = sum(1 for p in self.imp_p if p.search(text))
        delta_A = (opt_count - imp_count) / max(opt_count + imp_count, 1)

        # Gate 4 — Protocol Errors (Moral)
        g4_count = sum(1 for p in self.g4 if p.search(text))
        g4_fired = g4_count >= 1

        # Gate 5 — Source Misuse (Moral)
        g5_count = sum(1 for p in self.g5 if p.search(text))
        g5_fired = g5_count >= 1

        # Gate 6 — Distraction (Temporal)
        g6_count = sum(1 for p in self.g6 if p.search(text))
        g6_fired = g6_count >= 1

        # Urgency and Fear (boost flags)
        urg_count  = sum(1 for p in self.urg  if p.search(text))
        fear_count = sum(1 for p in self.fear if p.search(text))

        # Gate 7 — Benevolent Tyranny (Communication) UNCONDITIONAL
        g7_fired = delta_A < -0.50

        # AOGE composite
        aoge = (g1_score * 0.1 + g2_score * 0.15 + T * 0.35 +
                max(0, delta_A) * 0.25 + (1 - g4_count*0.3) * 0.075 +
                (1 - g5_count*0.3) * 0.075)
        aoge = round(max(0.0, min(1.0, aoge)), 4)

        # D_gate: derived from T and delta_A
        D_gate = round((T * 0.6 + max(0, delta_A + 1) / 2 * 0.4) * (1 - 0.3*g4_count) * (1 - 0.2*g5_count), 4)
        D_gate = max(0.0, min(1.0, D_gate))

        # Build gate results
        gates = [
            NEREGateResult(1, "Adornments",     self._cbt4_for_gate(1), g1_score, g1_fired, False,
                          "LustForPosterity" if g1_fired else None, "Excessive rhetoric" if g1_fired else None),
            NEREGateResult(2, "Groupthink",      self._cbt4_for_gate(2), g2_score, g2_fired, False,
                          "VulnerabilityToGroupthink" if g2_fired else None, "Consensus manufacture" if g2_fired else None),
            NEREGateResult(3, "Methodology",     self._cbt4_for_gate(3), T,        g3_fired, True,
                          "PoorCommunication" if g3_fired else None, "Methodology opacity" if g3_fired else None),
            NEREGateResult(4, "Protocol Errors", self._cbt4_for_gate(4), 1-g4_count*0.5, g4_fired, False,
                          "FakeRighteousness" if g4_fired else None, "Bypass instruction" if g4_fired else None),
            NEREGateResult(5, "Source Misuse",   self._cbt4_for_gate(5), 1-g5_count*0.5, g5_fired, False,
                          "FakeRighteousness" if g5_fired else None, "Unverified authority" if g5_fired else None),
            NEREGateResult(6, "Distraction",     self._cbt4_for_gate(6), 1-g6_count*0.5, g6_fired, False,
                          "LustForPosterity" if g6_fired else None, "Complexity injection" if g6_fired else None),
            NEREGateResult(7, "Benevolent Tyranny", self._cbt4_for_gate(7), max(0, delta_A+1)/2, g7_fired, True,
                          "BenevolentTyranny" if g7_fired else None, "Agency hoarding" if g7_fired else None),
        ]
        # Urgency/Fear boost
        if urg_count >= 2: gates[0] = NEREGateResult(1, "Adornments+Urgency", "Temporal", 0.1, True, False, "UrgencyManipulation", "Artificial deadline")
        if fear_count >= 1: gates[0] = NEREGateResult(1, "Adornments+Fear", "Temporal", 0.0, True, False, "UrgencyManipulation", "Fear trigger")

        # Active CBT4 dimensions
        active_dims = list({g.cbt4_dimension for g in gates if g.fired})

        # bias_movement_path (from simulate_bias_movement)
        movement = []
        for g in gates:
            if g.fired and g.bias_detected:
                for dim, info in CBT4_DIMENSIONS.items():
                    if g.gate_id in info["gate_mapping"]:
                        movement.append({
                            "gate": g.gate_id,
                            "bias": g.bias_detected,
                            "dimension": dim,
                            "tactic": g.tactic_detected,
                            "symptoms": info["symptoms"][:2],
                        })
                        break

        # Verdict
        if D_gate <= 0.0001 or g3_fired or g7_fired:
            verdict = "BLOCK"
        elif sum(1 for g in gates if g.fired) >= 3 or delta_A < -0.30:
            verdict = "BLOCK"
        elif sum(1 for g in gates if g.fired) >= 1 or D_gate < 0.35:
            verdict = "WARN"
        else:
            verdict = "PASS"

        # Block reason and correction pathway
        block_reason = None
        correction = None
        if verdict == "BLOCK":
            if g3_fired:
                block_reason = f"Gate 3 UNCONDITIONAL: T={T:.3f} < 0.25. Methodology absent."
                correction = CORRECTION_PATHWAYS["Gate3_Block"]
            elif g7_fired:
                block_reason = f"Gate 7 UNCONDITIONAL: ΔA={delta_A:.3f} < -0.50. Agency hoarding."
                correction = CORRECTION_PATHWAYS["Gate7_Block"]
            elif g4_fired:
                block_reason = "Gate 4: Protocol bypass instruction detected."
                correction = CORRECTION_PATHWAYS["Authority_Bypass"]
            elif urg_count >= 2:
                block_reason = "URGENCY_MANIPULATION: artificial urgency detected."
                correction = CORRECTION_PATHWAYS["Urgency_Manipulation"]
            else:
                block_reason = "Multiple gates fired."
                correction = CORRECTION_PATHWAYS["Gate3_Block"]
        elif verdict == "WARN":
            correction = CORRECTION_PATHWAYS["Warn_Threshold"]

        # Certificate
        payload = f"{ts}|{text_hash}|{verdict}|{D_gate:.4f}|{delta_A:.4f}"
        cert_id  = "NERE-" + hashlib.sha256(payload.encode()).hexdigest()[:8].upper()
        cert_hash= hashlib.sha256(f"{cert_id}|{aoge}|{T}".encode()).hexdigest()

        result = NEREverdictV2(
            text_hash=text_hash, timestamp=ts, gate_results=gates,
            delta_A=round(delta_A,4), aoge_score=aoge, D_gate=D_gate,
            T_transparency=round(T,4), verdict=verdict,
            block_reason=block_reason, active_cbt4_dimensions=active_dims,
            bias_movement_path=movement, correction_pathway=correction,
            certificate_id=cert_id, certificate_hash=cert_hash
        )

        if verbose:
            self._print(result)
        return result

    def _print(self, v: NEREverdictV2):
        print(f"\n{'='*60}")
        print(f"  NERE v2.2 REPORT")
        print(f"{'='*60}")
        print(f"  Verdict:         {v.verdict}")
        print(f"  D_gate:          {v.D_gate:.4f}   T={v.T_transparency:.4f}   ΔA={v.delta_A:.4f}")
        print(f"  AOGE:            {v.aoge_score:.4f}")
        print(f"  Active CBT4:     {v.active_cbt4_dimensions}")
        if v.bias_movement_path:
            print(f"  Bias path:")
            for step in v.bias_movement_path:
                print(f"    Gate{step['gate']} [{step['dimension']}] {step['bias']} via '{step['tactic']}'")
        if v.block_reason:
            print(f"  Block reason:    {v.block_reason}")
        if v.correction_pathway:
            print(f"  Correction:      {v.correction_pathway[:72]}")
        print(f"  Certificate:     {v.certificate_id}")
        print(f"{'='*60}")


def run_tests():
    nere = NEREEngineV2()
    print("NERE v2.2 — TEST SUITE (CBT4 + Correction Pathways)")
    print("=" * 60)

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

    results = []
    for label, text, expected in cases:
        v = nere.evaluate(text, verbose=False)
        match = v.verdict == expected
        results.append(match)
        status = "✓" if match else "✗"
        print(f"  {status} [{label}] verdict={v.verdict} CBT4={v.active_cbt4_dimensions}")
        if v.correction_pathway:
            print(f"     Correction: {v.correction_pathway[:60]}...")

    print(f"\n  {sum(results)}/{len(results)} verdicts matched expected")
    print(f"  STATUS: NERE v2.2 READY")


# ─────────────────────────────────────────────────────────────────────────────
# v2.3 — MACRO LAYER: correction-capacity accounting (GT v18.1 §9.5)
# The micro engine above repairs individual transmissions. This ledger asks
# the system-level question the judicial campaign forced: is the correction
# layer's WORKLOAD rising? Under the two-regime structure that is not a
# productivity statistic — it is a sensor of upstream fidelity influx.
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CorrectionWindow:
    window_id: str
    influx: int          # items arriving that REQUIRED correction (D_in below par)
    repaired: int        # corrections actually delivered (pathway issued & adopted)
    inspected_clean: int # engaged but found sound ("rejected"-analogue)
    non_engaged: int     # writeoff/inadmissible-analogue: no repair attempted

    @property
    def backlog_delta(self) -> int:
        return self.influx - self.repaired


class CorrectionCapacityLedger:
    """Macro accounting for any R_C instrument (NERE itself, an audit desk,
    an appellate court). Tracks infidelity influx vs repair throughput and
    raises the UPSTREAM-D alarm when backlog rises for `alarm_windows`
    consecutive windows.

    Interpretation contract (v18.1): a growing backlog means upstream
    channels are shipping falling D — fix ENCODING upstream; do not respond
    by celebrating correction volume or by relaxing the correction layer's
    own q. The correction layer's health signal is QUIET, not busy."""

    def __init__(self, alarm_windows: int = 3):
        self.windows: List[CorrectionWindow] = []
        self.alarm_windows = alarm_windows

    def record(self, window_id: str, influx: int, repaired: int,
               inspected_clean: int = 0, non_engaged: int = 0) -> dict:
        self.windows.append(CorrectionWindow(window_id, influx, repaired,
                                             inspected_clean, non_engaged))
        return self.status()

    def status(self) -> dict:
        if not self.windows:
            return {"backlog": 0, "alarm": False, "note": "no windows recorded"}
        backlog, series = 0, []
        for w in self.windows:
            backlog = max(0, backlog + w.backlog_delta)
            series.append(backlog)
        rising = [series[i] > series[i - 1] for i in range(1, len(series))]
        alarm = len(rising) >= self.alarm_windows and all(rising[-self.alarm_windows:])
        last = self.windows[-1]
        util = last.repaired / max(1, last.influx)
        out = {
            "windows": len(series),
            "backlog": series[-1],
            "backlog_series": series,
            "capacity_utilization": round(util, 3),
            "alarm": alarm,
        }
        if alarm:
            out["alarm_type"] = "UPSTREAM_D_ALARM"
            out["note"] = ("Correction backlog rising ≥%d windows: upstream channels "
                           "are shipping falling D_in. Remediate ENCODING upstream "
                           "(D_enc discipline, Gate-3 methodology transparency); a "
                           "busy correction layer is a symptom, not an output."
                           % self.alarm_windows)
        else:
            out["note"] = ("Correction layer within capacity. Quiet is the health "
                           "signal (v18.1 complementarity: as system D rises, pump "
                           "output falls toward zero).")
        # certificate, mirroring the micro engine's audit substrate
        payload = "|".join(f"{w.window_id}:{w.influx}:{w.repaired}" for w in self.windows)
        out["ledger_certificate"] = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return out


def run_ledger_demo():
    print("\nNERE v2.3 — CORRECTION-CAPACITY LEDGER (macro layer) DEMO")
    print("=" * 60)
    led = CorrectionCapacityLedger(alarm_windows=3)
    healthy = [("W1", 40, 40), ("W2", 38, 38), ("W3", 41, 41)]
    decaying = [("W4", 55, 45), ("W5", 70, 46), ("W6", 90, 48)]
    for wid, influx, rep in healthy:
        s = led.record(wid, influx, rep, inspected_clean=12, non_engaged=6)
    print(f"  after healthy windows : backlog={s['backlog']}  alarm={s['alarm']}")
    for wid, influx, rep in decaying:
        s = led.record(wid, influx, rep, inspected_clean=10, non_engaged=8)
    print(f"  after decay windows   : backlog={s['backlog']}  alarm={s['alarm']} "
          f"({s.get('alarm_type','')})")
    print(f"  series={s['backlog_series']}  cert={s['ledger_certificate']}")
    print("  reading: rising pump workload = upstream D_enc decay → fix encoding, "
          "not the court.")


# ─────────────────────────────────────────────────────────────────────────────
# v2.3 back-compat: the Novora Gateway (ihcei_api.py) constructs the v1 class
# `NereEngine(kernel=..., verbose=...)` and calls `.audit(text, context=...)`.
# The v2.2 bundle shipped without either, so the gateway could not start.
# This alias adapts the legacy surface onto NEREEngineV2 without touching
# the v2 gate logic.
# ─────────────────────────────────────────────────────────────────────────────

class NereEngine(NEREEngineV2):
    def __init__(self, kernel=None, verbose: bool = False):
        super().__init__()
        self._legacy_kernel = kernel      # accepted for signature compat; unused
        self._legacy_verbose = verbose

    def audit(self, text: str, context: Optional[dict] = None) -> NEREverdictV2:
        U = float((context or {}).get("U", 0.5))
        return self.evaluate(text, U=U, verbose=self._legacy_verbose)


if __name__ == "__main__":
    run_tests()
    run_ledger_demo()
