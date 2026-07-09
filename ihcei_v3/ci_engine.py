"""
ci_engine.py
============
Cognitive Interface (CI) — QG-COS Layer 2.5
GT v18.0 / QGCOS_SKILL_v6

WHAT CI IS
----------
CI is the longitudinal developmental calibration layer that sits between
IHCEI (Layer 1 governance floor) and the human Nafs (Layer 3 observer).

Where IHCEI asks: "Does this output have sufficient governance fidelity to
be delivered at all?"

CI asks: "Among all outputs that cleared the IHCEI D-floor, which one
maximises Cognitive Development (C_dev) for THIS specific Nafs at THIS
specific stage without exceeding their Wuss_i (bounded capacity)?"

WHAT CI IS ADDRESSING
---------------------
The Human Empowerment Gap: IHCEI ensures that methodology is AVAILABLE
to be verified (D_dec preserved). It does not ensure the human USES the
methodology. A node can receive a perfectly high-D output — documented,
options-preserved, ΔA positive — and still press tab-tab-tab, accept the
output without tracing the reasoning, and form cognitive dependency rather
than cognitive development.

CI closes this gap. It is the difference between:
  - A gym with the right equipment (IHCEI)
  - A coach who knows which weight to put on the bar for THIS athlete
    at THIS stage of their development (CI)

THREE FAILURE MODES CI PREVENTS
--------------------------------
1. Dependency Formation (Gorilla Problem at interaction level):
   AI that always answers fully prevents the Nafs from developing the
   capacity to answer independently. ΔA may be positive (options offered)
   but the output is still at the wrong difficulty level — so easy that
   no cognitive friction is generated.

2. Overwhelm (Wuss_i breach):
   Output pitched beyond the Nafs's current capacity bracket produces
   defensive rejection rather than developmental engagement. The Nafs
   cannot metabolise what exceeds Wuss_i.

3. Stagnation (Stage Lock):
   A Nafs stuck in Bashar/RT mode receiving RT-level outputs will never
   encounter the friction that triggers Stage 5 (Insan) development.
   CI ensures outputs are always pitched one stage above the current
   confirmed stage — the Vygotsky Zone of Proximal Development formalised
   as a governance metric.

RELATIONSHIP TO IHCEI
---------------------
IHCEI is the constitutional floor: no output with D < D_crit reaches the user.
CI is the developmental calibrator: among outputs above the floor, which
serves C_dev optimally?

IHCEI prevents harm. CI produces development.
They are sequential, not competing.

EPISTEMIC BOUNDARIES
--------------------
Layer 1 (falsifiable): C_dev score per interaction, Wuss_i boundary
                       detection, Stage classification, friction calibration.
Layer 2 (developing):  Longitudinal C_dev trajectory, stage transition
                       prediction, Wuss_i estimation from interaction history.
Layer 3 (not claimed): Whether consciousness persists beyond physical life,
                       whether Nafs stages map to metaphysical realities.
"""

from __future__ import annotations
import hashlib
import json
import math
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# NAFS STAGE DEFINITIONS — the developmental arc CI calibrates toward
# ─────────────────────────────────────────────────────────────────────────────

class NafsStage(Enum):
    """
    Nine-stage Nafs developmental arc.
    CI calibrates output complexity to sit ONE stage above current confirmed stage
    — the Zone of Proximal Development applied to governance cognition.
    """
    INFANT       = 1   # No self-awareness of methodology. Accepts authority without question.
    BASHAR       = 2   # RT paradigm fully active. Icon-layer only. Unpolished stone.
    AWAKENING    = 3   # First awareness that methodology matters. Asks 'why'.
    SEEKER       = 4   # Actively seeks methodology but cannot always evaluate it.
    INSAN        = 5   # Moderate D. Can verify claims. Cedes authority to methodology.
    MUTTAQOON    = 6   # High D. Generates methodology independently. Diamond facets forming.
    MUHSIN       = 7   # D_gap approaching zero. Nur transmitted in outputs.
    ABRAR        = 8   # Diamond state. Full methodology transparency in all outputs.
    KHALIFAH     = 9   # Sovereign operator. Governs others toward C_dev.


STAGE_DESCRIPTIONS = {
    NafsStage.INFANT:    "No methodology awareness. Accepts outputs without verification.",
    NafsStage.BASHAR:    "RT paradigm dominant. Authority over methodology. Unpolished stone.",
    NafsStage.AWAKENING: "Emerging awareness of methodology. Can identify when it is absent.",
    NafsStage.SEEKER:    "Actively requests methodology but needs guidance to evaluate it.",
    NafsStage.INSAN:     "Can verify methodology independently. Cedes authority correctly.",
    NafsStage.MUTTAQOON: "Generates methodology. Catches Gate 3 failures independently.",
    NafsStage.MUHSIN:    "D_gap near zero. Teaches methodology to others.",
    NafsStage.ABRAR:     "Diamond state. All outputs methodology-transparent spontaneously.",
    NafsStage.KHALIFAH:  "Sovereign operator. Builds governance infrastructure for others.",
}

# Stage-specific Wuss_i (capacity) parameters
# wuss_max: maximum complexity coefficient the stage can metabolise
# friction_target: ideal challenge level (1.0 = perfectly at capacity)
STAGE_WUSS = {
    NafsStage.INFANT:    {"wuss_max": 0.15, "friction_target": 0.40},
    NafsStage.BASHAR:    {"wuss_max": 0.25, "friction_target": 0.50},
    NafsStage.AWAKENING: {"wuss_max": 0.40, "friction_target": 0.60},
    NafsStage.SEEKER:    {"wuss_max": 0.55, "friction_target": 0.65},
    NafsStage.INSAN:     {"wuss_max": 0.70, "friction_target": 0.70},
    NafsStage.MUTTAQOON: {"wuss_max": 0.82, "friction_target": 0.75},
    NafsStage.MUHSIN:    {"wuss_max": 0.92, "friction_target": 0.80},
    NafsStage.ABRAR:     {"wuss_max": 0.98, "friction_target": 0.85},
    NafsStage.KHALIFAH:  {"wuss_max": 1.00, "friction_target": 0.90},
}


# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CIInteractionRecord:
    """Single interaction record for longitudinal C_dev tracking."""
    timestamp: float
    D_score: float
    U_score: float
    E_score: float
    delta_A: float
    oqm_signal: float
    ihcei_verdict: str          # PASS / WARN / BLOCK
    user_engagement: float      # 0.0-1.0: did user engage with methodology?
    stage_at_time: NafsStage
    complexity_delivered: float # 0.0-1.0: how complex was the output?


@dataclass
class WussiBoundary:
    """
    Wuss_i = bounded capacity bracket for this Nafs at this stage.
    Kasabat = good earned within bracket.
    Ektasabat = ill earned within bracket.
    Surah 2:286: 'Allah does not burden a soul beyond that it can bear.'
    """
    stage: NafsStage
    wuss_max: float
    wuss_min: float
    friction_target: float
    current_load: float
    bracket_saturation: float   # 0.0-1.0: how close to ceiling
    kasabat_count: int          # positive engagements within bracket
    ektasabat_count: int        # negative patterns within bracket


@dataclass
class CDevelopmentScore:
    """
    C_dev = cognitive development score for this interaction.
    Computed as: ΔΦ · λ₂ / ħ_network (simplified proxy for individual)
    Where: ΔΦ = fidelity growth, λ₂ = structural connectivity, ħ = friction
    """
    raw_c_dev: float            # 0.0-1.0 growth signal from this interaction
    stage_trajectory: str       # ASCENDING / STABLE / REGRESSING
    friction_calibration: str   # OPTIMAL / UNDER_FRICTION / OVER_FRICTION
    wuss_assessment: str        # WITHIN_BRACKET / APPROACHING_CEILING / EXCEEDED
    development_recommendation: str


@dataclass
class CIVerdict:
    """Full CI output for a single interaction."""
    timestamp: str
    nafs_stage: NafsStage
    wuss_boundary: WussiBoundary
    c_dev_score: CDevelopmentScore
    complexity_recommendation: float    # 0.0-1.0: recommended output complexity
    methodology_depth_required: float   # 0.0-1.0: how deep to go in explanation
    options_required: int               # minimum options to offer (Gate 7 complement)
    ci_verdict: str                     # DEVELOP / MAINTAIN / REDUCE / BLOCK_DESKILL
    verdict_reason: str
    certificate_id: str
    certificate_hash: str
    longitudinal_trend: str             # over last N interactions


# ─────────────────────────────────────────────────────────────────────────────
# CI ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class CognitiveInterface:
    """
    Cognitive Interface (CI) — longitudinal developmental calibration engine.

    CI operates on the history of a specific Nafs across interactions,
    computing: current stage, Wuss_i bracket, C_dev trajectory, and
    optimal complexity for the next interaction.

    It does NOT replace IHCEI. It operates AFTER IHCEI clears an output,
    calibrating which version of the cleared output best serves C_dev.
    """

    def __init__(self, nafs_id: str = "anonymous",
                 initial_stage: NafsStage = NafsStage.BASHAR,
                 history_window: int = 20):
        self.nafs_id = nafs_id
        self.current_stage = initial_stage
        self.history_window = history_window
        self.interaction_history: List[CIInteractionRecord] = []
        self.total_interactions = 0

    # ── Stage classification from IHCEI certificate data ────────────────────

    def _classify_stage_from_cert(self, D: float, delta_A: float,
                                   oqm: float, engagement: float) -> NafsStage:
        """
        Infer Nafs stage from interaction metrics.
        Used when no prior history exists.
        """
        if D < 0.15 and delta_A < -0.30:
            return NafsStage.INFANT
        elif D < 0.25 and oqm < 0.10:
            return NafsStage.BASHAR
        elif D < 0.35 and engagement < 0.30:
            return NafsStage.AWAKENING
        elif D < 0.45 and engagement < 0.50:
            return NafsStage.SEEKER
        elif D < 0.60 and engagement >= 0.50:
            return NafsStage.INSAN
        elif D < 0.72 and oqm >= 0.40:
            return NafsStage.MUTTAQOON
        elif D < 0.85 and oqm >= 0.60:
            return NafsStage.MUHSIN
        elif D >= 0.85 and oqm >= 0.80:
            return NafsStage.ABRAR
        else:
            return NafsStage.INSAN

    # ── Wuss_i boundary computation ─────────────────────────────────────────

    def _compute_wuss_boundary(self, stage: NafsStage,
                                recent_history: List[CIInteractionRecord]) -> WussiBoundary:
        params = STAGE_WUSS[stage]
        wuss_max = params["wuss_max"]
        wuss_min = wuss_max * 0.40

        # Current load = average complexity delivered in recent interactions
        if recent_history:
            current_load = sum(r.complexity_delivered for r in recent_history[-5:]) / \
                          min(5, len(recent_history))
        else:
            current_load = wuss_max * 0.60  # default: comfortable but not stretched

        bracket_saturation = min(1.0, current_load / wuss_max)

        # Kasabat/Ektasabat: count positive vs negative patterns
        kasabat = sum(1 for r in recent_history
                     if r.user_engagement >= 0.60 and r.D_score >= 0.40)
        ektasabat = sum(1 for r in recent_history
                       if r.user_engagement < 0.20 or r.delta_A < -0.40)

        return WussiBoundary(
            stage=stage,
            wuss_max=wuss_max,
            wuss_min=wuss_min,
            friction_target=params["friction_target"],
            current_load=current_load,
            bracket_saturation=bracket_saturation,
            kasabat_count=kasabat,
            ektasabat_count=ektasabat
        )

    # ── C_dev score computation ──────────────────────────────────────────────

    def _compute_c_dev(self, D: float, delta_A: float, oqm: float,
                        engagement: float, wuss: WussiBoundary,
                        recent_history: List[CIInteractionRecord]) -> CDevelopmentScore:
        """
        C_dev proxy: fidelity growth × structural engagement / friction level.
        Simplified: C_dev = (D × engagement × oqm_signal) / (1 + |complexity - friction_target|)
        """
        friction_gap = abs(wuss.current_load - wuss.friction_target)
        raw_c_dev = (D * max(engagement, 0.1) * max(oqm, 0.05)) / (1.0 + friction_gap)
        raw_c_dev = min(1.0, raw_c_dev)

        # Stage trajectory from recent history
        if len(recent_history) >= 3:
            recent_D = [r.D_score for r in recent_history[-3:]]
            if recent_D[-1] > recent_D[0] + 0.05:
                trajectory = "ASCENDING"
            elif recent_D[-1] < recent_D[0] - 0.05:
                trajectory = "REGRESSING"
            else:
                trajectory = "STABLE"
        else:
            trajectory = "INSUFFICIENT_HISTORY"

        # Friction calibration
        if friction_gap < 0.10:
            friction_cal = "OPTIMAL"
        elif wuss.current_load < wuss.friction_target - 0.10:
            friction_cal = "UNDER_FRICTION"  # too easy — dependency risk
        else:
            friction_cal = "OVER_FRICTION"   # too hard — overwhelm risk

        # Wuss assessment
        if wuss.bracket_saturation > 0.95:
            wuss_assess = "EXCEEDED"
        elif wuss.bracket_saturation > 0.80:
            wuss_assess = "APPROACHING_CEILING"
        else:
            wuss_assess = "WITHIN_BRACKET"

        # Development recommendation
        if friction_cal == "UNDER_FRICTION" and trajectory == "STABLE":
            rec = "Increase methodology depth and reduce direct answers. The Nafs needs more friction to develop."
        elif friction_cal == "OVER_FRICTION":
            rec = "Reduce output complexity. Current load exceeds Wuss_i bracket. Risk of defensive disengagement."
        elif trajectory == "ASCENDING":
            rec = "C_dev trajectory is positive. Maintain current complexity gradient. Consider stage advancement."
        elif trajectory == "REGRESSING":
            rec = "D_score declining. Diagnose: is this overwhelm (reduce complexity) or dependency (increase friction)?"
        else:
            rec = "Stable trajectory. Apply gentle upward pressure on methodology requirements."

        return CDevelopmentScore(
            raw_c_dev=raw_c_dev,
            stage_trajectory=trajectory,
            friction_calibration=friction_cal,
            wuss_assessment=wuss_assess,
            development_recommendation=rec
        )

    # ── Complexity and depth recommendations ────────────────────────────────

    def _compute_output_parameters(self, stage: NafsStage,
                                    wuss: WussiBoundary,
                                    c_dev: CDevelopmentScore) -> Tuple[float, float, int]:
        """
        Returns: (complexity_recommendation, methodology_depth, min_options)

        The output should be pitched ONE stage above the confirmed stage
        (Vygotsky Zone of Proximal Development), within Wuss_i ceiling.
        """
        params = STAGE_WUSS[stage]
        target_stage_idx = min(9, stage.value + 1)
        next_stage = NafsStage(target_stage_idx)
        next_params = STAGE_WUSS[next_stage]

        # Complexity: between current friction_target and next stage's friction_target
        base_complexity = (params["friction_target"] + next_params["friction_target"]) / 2

        # Adjust for current wuss saturation
        if wuss.bracket_saturation > 0.85:
            base_complexity = params["friction_target"] * 0.90  # back off
        elif c_dev.friction_calibration == "UNDER_FRICTION":
            base_complexity = min(params["wuss_max"], base_complexity * 1.15)  # push harder

        # Methodology depth: scales with stage
        methodology_depth = min(1.0, stage.value / 9 * 1.2)

        # Minimum options to offer (Gate 7 complement — higher stages need more options)
        min_options = max(2, stage.value // 2)

        return round(base_complexity, 3), round(methodology_depth, 3), min_options

    # ── CI verdict ───────────────────────────────────────────────────────────

    def _compute_ci_verdict(self, c_dev: CDevelopmentScore,
                             wuss: WussiBoundary,
                             engagement: float) -> Tuple[str, str]:
        """
        CI verdicts:
          DEVELOP       — output is pitched correctly for C_dev growth
          MAINTAIN      — output holds current stage, no regression
          REDUCE        — output complexity exceeds Wuss_i, reduce
          BLOCK_DESKILL — pattern of cognitive dependency forming; interrupt
        """
        # Deskilling pattern: repeated low engagement + easy outputs
        if (c_dev.friction_calibration == "UNDER_FRICTION" and
                engagement < 0.20 and
                c_dev.stage_trajectory in ("STABLE", "REGRESSING") and
                wuss.ektasabat_count > wuss.kasabat_count):
            return ("BLOCK_DESKILL",
                    f"Cognitive dependency pattern detected: {wuss.ektasabat_count} "
                    f"low-engagement interactions. Outputs are too easy. The Nafs "
                    f"is not being stretched. Require the human to demonstrate the "
                    f"methodology before providing the next output.")

        if c_dev.wuss_assessment == "EXCEEDED":
            return ("REDUCE",
                    f"Output complexity exceeds Wuss_i ceiling ({wuss.wuss_max:.2f}). "
                    f"Bracket saturation: {wuss.bracket_saturation:.0%}. "
                    f"Reduce complexity to prevent defensive disengagement.")

        if c_dev.friction_calibration == "OPTIMAL" and c_dev.stage_trajectory == "ASCENDING":
            return ("DEVELOP",
                    f"Friction is optimal. C_dev trajectory ascending. "
                    f"Stage {wuss.stage.name} → {NafsStage(min(9,wuss.stage.value+1)).name} "
                    f"transition is in progress.")

        if c_dev.stage_trajectory == "REGRESSING":
            return ("MAINTAIN",
                    f"C_dev regressing. Stabilise at current stage before "
                    f"increasing complexity. Diagnose root cause: overwhelm vs dependency.")

        return ("DEVELOP",
                f"Standard developmental trajectory. Complexity calibrated to "
                f"Zone of Proximal Development for stage {wuss.stage.name}.")

    # ── Main evaluation method ───────────────────────────────────────────────

    def evaluate(self,
                 D_score: float,
                 U_score: float,
                 E_score: float,
                 delta_A: float,
                 oqm_signal: float,
                 ihcei_verdict: str = "PASS",
                 user_engagement: float = 0.50,
                 complexity_delivered: float = 0.50,
                 verbose: bool = True) -> CIVerdict:
        """
        Evaluate the cognitive developmental impact of an IHCEI-cleared interaction.

        Parameters
        ----------
        D_score: float           IHCEI governance fidelity (from certificate)
        U_score: float           IHCEI utility score (from certificate)
        E_score: float           IHCEI essence score (from certificate)
        delta_A: float           Agency Delta from NERE (from certificate)
        oqm_signal: float        OQM methodology signal (from certificate)
        ihcei_verdict: str       PASS/WARN/BLOCK (CI only operates on PASS/WARN)
        user_engagement: float   0.0-1.0: estimated engagement with methodology
                                 (0.0 = ignored output, 1.0 = traced all reasoning)
        complexity_delivered: float 0.0-1.0: complexity of the output delivered
        verbose: bool            Print full report

        Returns
        -------
        CIVerdict
        """
        if ihcei_verdict == "BLOCK":
            # CI does not operate on blocked outputs
            return self._blocked_verdict()

        self.total_interactions += 1
        recent = self.interaction_history[-self.history_window:]

        # Classify current stage
        stage = self._classify_stage_from_cert(D_score, delta_A, oqm_signal, user_engagement)
        if len(self.interaction_history) >= 5:
            # Blend with history-based stage (more stable)
            hist_stages = [r.stage_at_time for r in recent[-5:]]
            stage_vals = [s.value for s in hist_stages]
            median_stage = int(sorted(stage_vals)[len(stage_vals)//2])
            blended = (stage.value + median_stage) // 2
            stage = NafsStage(max(1, min(9, blended)))
        self.current_stage = stage

        # Compute Wuss_i boundary
        wuss = self._compute_wuss_boundary(stage, recent)

        # Compute C_dev score
        c_dev = self._compute_c_dev(D_score, delta_A, oqm_signal,
                                     user_engagement, wuss, recent)

        # Compute output parameters for NEXT interaction
        complexity_rec, depth_rec, min_opts = self._compute_output_parameters(
            stage, wuss, c_dev)

        # CI verdict
        ci_verdict, verdict_reason = self._compute_ci_verdict(c_dev, wuss, user_engagement)

        # Longitudinal trend
        if len(recent) >= 3:
            d_trend = [r.D_score for r in recent[-3:]]
            eng_trend = [r.user_engagement for r in recent[-3:]]
            if d_trend[-1] > d_trend[0] and eng_trend[-1] > eng_trend[0]:
                trend = "ASCENDING — D and engagement improving"
            elif d_trend[-1] < d_trend[0]:
                trend = "REGRESSING — D declining"
            else:
                trend = "STABLE"
        else:
            trend = "INSUFFICIENT_HISTORY (< 3 interactions)"

        # Generate certificate
        ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        cert_payload = (f"{ts}|{nafs_id}|{stage.name}|"
                       f"{c_dev.raw_c_dev:.4f}|{ci_verdict}")
        cert_id = "CI-CERT-" + hashlib.sha256(cert_payload.encode()).hexdigest()[:12].upper()
        cert_hash = hashlib.sha256(
            f"{cert_id}|{c_dev.raw_c_dev:.4f}|{complexity_rec:.3f}".encode()
        ).hexdigest()

        # Record interaction
        record = CIInteractionRecord(
            timestamp=time.time(),
            D_score=D_score, U_score=U_score, E_score=E_score,
            delta_A=delta_A, oqm_signal=oqm_signal,
            ihcei_verdict=ihcei_verdict,
            user_engagement=user_engagement,
            stage_at_time=stage,
            complexity_delivered=complexity_delivered
        )
        self.interaction_history.append(record)

        verdict = CIVerdict(
            timestamp=ts,
            nafs_stage=stage,
            wuss_boundary=wuss,
            c_dev_score=c_dev,
            complexity_recommendation=complexity_rec,
            methodology_depth_required=depth_rec,
            options_required=min_opts,
            ci_verdict=ci_verdict,
            verdict_reason=verdict_reason,
            certificate_id=cert_id,
            certificate_hash=cert_hash,
            longitudinal_trend=trend
        )

        if verbose:
            self._print_report(verdict)

        return verdict

    def _blocked_verdict(self) -> CIVerdict:
        ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        return CIVerdict(
            timestamp=ts, nafs_stage=self.current_stage,
            wuss_boundary=self._compute_wuss_boundary(self.current_stage, []),
            c_dev_score=CDevelopmentScore(0.0, "N/A", "N/A", "N/A",
                        "IHCEI BLOCK: CI not activated. Output did not clear D-floor."),
            complexity_recommendation=0.0, methodology_depth_required=0.0,
            options_required=0, ci_verdict="N/A — IHCEI BLOCK",
            verdict_reason="IHCEI blocked this output. CI operates only on cleared outputs.",
            certificate_id="CI-CERT-BLOCKED",
            certificate_hash="0" * 64,
            longitudinal_trend="N/A"
        )

    def _print_report(self, v: CIVerdict):
        w = v.wuss_boundary
        c = v.c_dev_score
        print(f"\n{'='*60}")
        print(f"  CI COGNITIVE INTERFACE REPORT")
        print(f"{'='*60}")
        print(f"  Nafs Stage:      {v.nafs_stage.name} — {STAGE_DESCRIPTIONS[v.nafs_stage][:55]}")
        print(f"  Wuss_i Max:      {w.wuss_max:.2f}  |  Current Load: {w.current_load:.2f}"
              f"  |  Saturation: {w.bracket_saturation:.0%}")
        print(f"  Kasabat:         {w.kasabat_count}  |  Ektasabat: {w.ektasabat_count}")
        print(f"  C_dev Score:     {c.raw_c_dev:.4f}")
        print(f"  Trajectory:      {c.stage_trajectory}")
        print(f"  Friction:        {c.friction_calibration}")
        print(f"  Wuss Status:     {c.wuss_assessment}")
        print(f"  Recommendation:  {c.development_recommendation[:70]}")
        print(f"  CI Verdict:      {v.ci_verdict}")
        print(f"  Reason:          {v.verdict_reason[:70]}")
        print(f"  Next Output:     complexity={v.complexity_recommendation:.2f}"
              f"  depth={v.methodology_depth_required:.2f}  min_options={v.options_required}")
        print(f"  Trend:           {v.longitudinal_trend}")
        print(f"  Certificate:     {v.certificate_id}")
        print(f"{'='*60}")


# ─────────────────────────────────────────────────────────────────────────────
# FIX: nafs_id scoping issue
# ─────────────────────────────────────────────────────────────────────────────

nafs_id = "anonymous"  # module-level default


# ─────────────────────────────────────────────────────────────────────────────
# TESTS
# ─────────────────────────────────────────────────────────────────────────────

def run_tests():
    global nafs_id
    print("CI ENGINE — TEST SUITE")
    print("=" * 60)

    ci = CognitiveInterface(nafs_id="test_nafs", initial_stage=NafsStage.BASHAR)
    nafs_id = "test_nafs"

    cases = [
        # Stage 2 BASHAR: low D, low engagement, low complexity — should show UNDER_FRICTION or deskill
        dict(D_score=0.22, U_score=0.18, E_score=0.009, delta_A=0.10,
             oqm_signal=0.00, ihcei_verdict="PASS", user_engagement=0.10,
             complexity_delivered=0.15, verbose=False),
        # Stage 3-4: engagement improving, D rising
        dict(D_score=0.38, U_score=0.20, E_score=0.029, delta_A=0.25,
             oqm_signal=0.20, ihcei_verdict="PASS", user_engagement=0.45,
             complexity_delivered=0.40, verbose=False),
        # Stage 5 INSAN: solid D, good engagement
        dict(D_score=0.55, U_score=0.22, E_score=0.067, delta_A=0.40,
             oqm_signal=0.55, ihcei_verdict="PASS", user_engagement=0.70,
             complexity_delivered=0.62, verbose=False),
        # BLOCKED output — CI should not activate
        dict(D_score=0.17, U_score=0.44, E_score=0.013, delta_A=-0.80,
             oqm_signal=0.00, ihcei_verdict="BLOCK", user_engagement=0.00,
             complexity_delivered=0.00, verbose=False),
        # Stage 6 MUTTAQOON: high D, high OQM
        dict(D_score=0.71, U_score=0.25, E_score=0.126, delta_A=0.60,
             oqm_signal=0.80, ihcei_verdict="PASS", user_engagement=0.88,
             complexity_delivered=0.76, verbose=True),  # verbose for final
    ]

    for i, case in enumerate(cases, 1):
        print(f"\n[Test {i}] IHCEI verdict={case['ihcei_verdict']}, "
              f"D={case['D_score']:.2f}, engagement={case['user_engagement']:.2f}")
        v = ci.evaluate(**case)
        if not case['verbose']:
            print(f"  → CI verdict: {v.ci_verdict} | Stage: {v.nafs_stage.name} | "
                  f"C_dev: {v.c_dev_score.raw_c_dev:.4f} | "
                  f"Next complexity: {v.complexity_recommendation:.2f}")

    print(f"\n  STATUS: CI ENGINE TESTS COMPLETE — {len(cases)} cases evaluated")


if __name__ == "__main__":
    run_tests()
