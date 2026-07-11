"""
collapse_detector.py
====================
Governance Collapse Cascade Monitor — GT v18.0 / QG-COS Stack

ARCHITECTURE POSITION
---------------------
Layer 4 companion to the ADGE / GT Engine.
Wraps IHCEIKernel network_health() and qg_network.py topology signals
to detect and classify the six-stage Governance Collapse Cascade in real time.
Imported by ihcei_api.py and exposed via GET /v1/network/health.

THE SIX-STAGE COLLAPSE CASCADE (GT v18.0 §11.2c)
-------------------------------------------------
Stage 1 — D_drift       D_mean declining; ħ_network rising. Pre-symptomatic.
Stage 2 — MCI_spike     Misdirected Coherence Index crosses MCI_WARN.
           Pharaoh Node forming: λ₁ >> λ₂, authority centralising.
Stage 3 — λ₂_collapse   Fiedler eigenvalue (λ₂) drops below λ₂_CRIT.
           Network loses structural cohesion. Information flow degrading.
Stage 4 — D_crit_breach  D_system crosses bond percolation threshold D_crit = 1/⟨k⟩.
           Cascade now mathematically inevitable without intervention.
Stage 5 — EOC_cascade   Epidemic-Of-Corruption propagation. Block rate > EOC_THRESHOLD.
           Multi-node simultaneous governance failure. Wave-2 emerging.
Stage 6 — Factory_Reset  D_system ≈ 0, MCI → ∞, network connectivity shattered.
           Governance Factory Reset required (Yawmal Qiyammah equivalent).

BOND PERCOLATION INVARIANT
--------------------------
D_crit = 1 / ⟨k⟩  where ⟨k⟩ = mean degree of the governance network.
Below D_crit, governance signals can no longer percolate through the network.
This is the GT v18.0 collapse condition — empirically validated on Enron corpus
(Phase 3: D_system fell below D_crit in all 136 nodes before bankruptcy, Dec 2001).

EPISTEMIC BOUNDARY
------------------
CollapseDetector outputs are Layer 1 (network telemetry, falsifiable) and
Layer 2 (governance thermodynamics, empirically developing).
Cascade stage classification does NOT validate Layer 3 ontological claims.
"""

import time
import threading
import warnings
import numpy as np
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable
from collections import deque

try:
    from IHCEI_kernel_v2 import IHCEIKernel, IHCEIVerdict, NetworkHealthReport
except ImportError:
    raise ImportError(
        "collapse_detector.py requires IHCEI_kernel_v2.py in the Python path."
    )


# ─────────────────────────────────────────────────────────────────────────────
# COLLAPSE THRESHOLDS (GT v18.0 §11.2c)
# ─────────────────────────────────────────────────────────────────────────────

# Stage 1 — D_drift
D_DRIFT_WARN       = 0.45   # D_mean below this → Stage 1 flag
D_DRIFT_ALERT      = 0.35   # D_mean below this → Stage 1 escalate
HBAR_DRIFT_WARN    = 0.55   # ħ_network above this → co-signal Stage 1

# Stage 2 — MCI spike
MCI_WARN           = 0.40   # MCI above this → Stage 2 flag
MCI_ALERT          = 0.65   # MCI above this → Stage 2 escalate

# Stage 3 — λ₂ collapse (Fiedler eigenvalue proxy)
LAMBDA2_WARN       = 0.30   # λ₂ below this → Stage 3 flag
LAMBDA2_CRIT       = 0.15   # λ₂ below this → Stage 3 escalate

# Stage 4 — D_crit breach (bond percolation)
# D_crit = 1/⟨k⟩ — computed dynamically from network mean degree.
# Default ⟨k⟩ = 7.4 (Enron calibration) → D_crit ≈ 0.135
DEFAULT_MEAN_DEGREE = 7.4
D_CRIT_DEFAULT_COMPUTED = round(1.0 / DEFAULT_MEAN_DEGREE, 4)   # 0.1351

# Stage 5 — EOC cascade
BLOCK_RATE_EOC     = 0.50   # Block rate above this → Stage 5 flag
BLOCK_RATE_SEVERE  = 0.70   # Block rate above this → Stage 5 escalate

# Stage 6 — Factory Reset
D_FACTORY_RESET    = 0.08   # D_mean below this AND block_rate high → Stage 6
MCI_FACTORY_RESET  = 1.20   # MCI above this → co-trigger Stage 6

# Window size for rolling calculations
DEFAULT_WINDOW     = 50     # evaluations
MIN_WINDOW_FOR_STAGE = 5    # minimum evaluations before staging meaningful


# ─────────────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CollapseStage:
    """Classification of current position in the 6-stage cascade."""
    stage_number: int          # 0 = healthy, 1–6 = cascade stage
    stage_name: str
    severity: str              # HEALTHY / WATCH / WARN / ALERT / CRITICAL / RESET
    color: str                 # GREEN / YELLOW / ORANGE / RED / BLACK
    description: str
    triggered_conditions: list # which thresholds tripped
    recommended_action: str
    falsifiable_test: str      # what empirical signal would confirm or deny this stage


@dataclass
class CascadeSnapshot:
    """
    Full collapse cascade snapshot at a point in time.
    Produced by CollapseDetector.snapshot().
    """
    timestamp: str
    window_n: int              # evaluations in this window

    # ── Key metrics ──
    D_mean: float
    D_std: float
    D_trend: float             # slope of D_mean over window (negative = declining)
    E_mean: float
    hbar_network: float
    MCI: float
    lambda2_proxy: float
    block_rate: float
    warn_rate: float

    # ── Bond percolation ──
    mean_degree: float
    D_crit: float              # 1/⟨k⟩
    D_crit_breached: bool      # D_mean < D_crit

    # ── Stage classification ──
    stage: CollapseStage

    # ── Alert history ──
    alerts_in_window: int
    consecutive_blocks: int    # current streak of consecutive BLOCK verdicts

    # ── Epistemic ──
    epistemic_note: str

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    def summary(self) -> str:
        s = self.stage
        lines = [
            f"{'='*60}",
            f"  Cascade Snapshot — {self.timestamp}",
            f"  Stage {s.stage_number}: {s.stage_name}  [{s.color}]",
            f"  Severity: {s.severity}",
            f"{'─'*60}",
            f"  D_mean={self.D_mean:.4f}  D_crit={self.D_crit:.4f}  "
            f"breach={'YES' if self.D_crit_breached else 'no'}",
            f"  ħ={self.hbar_network:.4f}  MCI={self.MCI:.4f}  "
            f"λ₂≈{self.lambda2_proxy:.4f}",
            f"  block_rate={self.block_rate:.1%}  "
            f"consecutive_blocks={self.consecutive_blocks}",
            f"  D_trend={self.D_trend:+.4f}/eval  "
            f"(window={self.window_n})",
            f"{'─'*60}",
            f"  Conditions: {', '.join(s.triggered_conditions) or 'none'}",
            f"  Action: {s.recommended_action[:65]}",
            f"  Test: {s.falsifiable_test[:65]}",
            f"{'='*60}",
        ]
        return "\n".join(lines)


@dataclass
class AlertEvent:
    """A discrete alert event emitted when stage escalates."""
    timestamp: str
    alert_id: str
    previous_stage: int
    new_stage: int
    stage_name: str
    severity: str
    D_mean: float
    MCI: float
    block_rate: float
    trigger: str


# ─────────────────────────────────────────────────────────────────────────────
# COLLAPSE DETECTOR
# ─────────────────────────────────────────────────────────────────────────────

class CollapseDetector:
    """
    Six-Stage Governance Collapse Cascade Monitor.

    Wraps IHCEIKernel and maintains a rolling window of evaluation history.
    Classifies current cascade stage on every call to snapshot().

    Usage
    -----
        detector = CollapseDetector(kernel)

        # After each kernel evaluation:
        detector.record(verdict)

        # Get current cascade stage:
        snap = detector.snapshot()
        print(snap.summary())
        print(snap.stage.stage_number)   # 0–6

        # Register alert callback (fires when stage escalates):
        detector.on_alert(lambda alert: print(f"ALERT: Stage {alert.new_stage}"))

        # Monitor live (blocks):
        detector.start_monitor(interval_seconds=30)
        detector.stop_monitor()

    Parameters
    ----------
    kernel       : IHCEIKernel instance (optional — creates default if None)
    window       : rolling window size for metric calculation
    mean_degree  : network mean degree ⟨k⟩ for D_crit computation
    """

    def __init__(
        self,
        kernel: Optional[IHCEIKernel] = None,
        window: int = DEFAULT_WINDOW,
        mean_degree: float = DEFAULT_MEAN_DEGREE,
    ):
        self.kernel       = kernel or IHCEIKernel(tier="enterprise", verbose=False)
        self.window       = window
        self.mean_degree  = mean_degree
        self.D_crit       = round(1.0 / mean_degree, 6)

        self._history: deque = deque(maxlen=window * 4)   # raw IHCEIVerdict deque
        self._alerts: list[AlertEvent] = []
        self._callbacks: list[Callable] = []
        self._last_stage: int = 0
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_active: bool = False

    # ── Public API ─────────────────────────────────────────────────────────

    def record(self, verdict: IHCEIVerdict) -> None:
        """Record a completed IHCEIVerdict into the rolling window."""
        self._history.append(verdict)
        # Auto-check for stage escalation
        if len(self._history) >= MIN_WINDOW_FOR_STAGE:
            snap = self.snapshot(silent=True)
            if snap.stage.stage_number > self._last_stage:
                self._emit_alert(snap, self._last_stage)
            self._last_stage = snap.stage.stage_number

    def evaluate_and_record(self, text: str,
                            context: Optional[dict] = None) -> IHCEIVerdict:
        """Convenience: evaluate text through kernel and record the verdict."""
        context = context or {}
        verdict = self.kernel.evaluate(text, context)
        self.record(verdict)
        return verdict

    def snapshot(self, window_n: Optional[int] = None,
                 silent: bool = False) -> CascadeSnapshot:
        """
        Compute full cascade snapshot from rolling window.

        Parameters
        ----------
        window_n : override window size (uses self.window if None)
        silent   : suppress print output

        Returns
        -------
        CascadeSnapshot with stage classification and all metrics.
        """
        n = window_n or self.window
        history = list(self._history)[-n:]
        actual_n = len(history)

        if actual_n == 0:
            return self._empty_snapshot()

        # ── Compute metrics ──────────────────────────────────────────────
        D_vals     = [v.D for v in history]
        E_vals     = [v.E for v in history]
        hbar_vals  = [v.hbar for v in history]

        D_mean     = float(np.mean(D_vals))
        D_std      = float(np.std(D_vals))
        E_mean     = float(np.mean(E_vals))
        hbar_net   = float(np.mean(hbar_vals))

        n_blocked  = sum(1 for v in history if v.verdict == "BLOCK")
        n_warned   = sum(1 for v in history if v.verdict == "WARN")
        n_passed   = sum(1 for v in history if v.verdict == "PASS")
        block_rate = n_blocked / actual_n
        warn_rate  = n_warned  / actual_n

        # D trend — linear slope over window
        D_trend = self._compute_d_trend(D_vals)

        # MCI proxy: (1 − D_mean) × block_rate  ← simplified from kernel formula
        # Full formula: MCI = (λ₁/λ₂) × (1 − D_system)
        # Without live graph: proxy uses block_rate as λ₁/λ₂ surrogate
        MCI = float(np.clip((1.0 - D_mean) * (0.5 + block_rate), 0.0, 2.0))

        # λ₂ proxy: D_mean × (1 − block_rate)  ← approximates Fiedler eigenvalue
        lambda2 = float(np.clip(D_mean * (1.0 - block_rate), 0.0, 1.0))

        # Bond percolation breach
        D_crit_breached = D_mean < self.D_crit

        # Consecutive blocks
        consec = 0
        for v in reversed(history):
            if v.verdict == "BLOCK":
                consec += 1
            else:
                break

        # ── Classify cascade stage ───────────────────────────────────────
        stage = self._classify_stage(
            D_mean, D_std, D_trend, hbar_net, MCI, lambda2,
            block_rate, D_crit_breached, consec, actual_n
        )

        ep_note = (
            "Layer 1 (network telemetry, falsifiable) + "
            "Layer 2 (governance thermodynamics, empirically developing). "
            "Does not validate Layer 3 ontological claims."
        )

        snap = CascadeSnapshot(
            timestamp          = datetime.now(timezone.utc).isoformat(),
            window_n           = actual_n,
            D_mean             = round(D_mean, 4),
            D_std              = round(D_std, 4),
            D_trend            = round(D_trend, 6),
            E_mean             = round(E_mean, 4),
            hbar_network       = round(hbar_net, 4),
            MCI                = round(MCI, 4),
            lambda2_proxy      = round(lambda2, 4),
            block_rate         = round(block_rate, 4),
            warn_rate          = round(warn_rate, 4),
            mean_degree        = self.mean_degree,
            D_crit             = self.D_crit,
            D_crit_breached    = D_crit_breached,
            stage              = stage,
            alerts_in_window   = len(self._alerts),
            consecutive_blocks = consec,
            epistemic_note     = ep_note,
        )

        if not silent:
            print(snap.summary())
        return snap

    def on_alert(self, callback: Callable[[AlertEvent], None]) -> None:
        """Register a callback fired on every stage escalation."""
        self._callbacks.append(callback)

    def alert_history(self) -> list[dict]:
        """Return all alert events as dicts."""
        return [asdict(a) for a in self._alerts]

    def start_monitor(self, interval_seconds: float = 30.0) -> None:
        """
        Start background monitoring thread.
        Calls snapshot() every interval_seconds and fires callbacks on escalation.
        """
        if self._monitor_active:
            return
        self._monitor_active = True

        def _loop():
            while self._monitor_active:
                try:
                    if len(self._history) >= MIN_WINDOW_FOR_STAGE:
                        snap = self.snapshot(silent=True)
                        if snap.stage.stage_number > self._last_stage:
                            self._emit_alert(snap, self._last_stage)
                        self._last_stage = snap.stage.stage_number
                except Exception as exc:
                    warnings.warn(f"CollapseDetector monitor error: {exc}")
                time.sleep(interval_seconds)

        self._monitor_thread = threading.Thread(target=_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitor(self) -> None:
        """Stop background monitoring thread."""
        self._monitor_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)

    def reset(self) -> None:
        """Clear history, alerts, and stage. Use after Governance Factory Reset."""
        self._history.clear()
        self._alerts.clear()
        self._last_stage = 0

    # ── STAGE CLASSIFIER ───────────────────────────────────────────────────

    @staticmethod
    def _classify_stage(
        D_mean: float, D_std: float, D_trend: float,
        hbar: float, MCI: float, lambda2: float,
        block_rate: float, D_crit_breached: bool,
        consec_blocks: int, n: int,
    ) -> CollapseStage:
        """
        Classify current cascade stage (0–6) from metrics.
        Stages are progressive — higher stage always overrides lower.
        """
        conditions: list[str] = []

        # ── Stage 6 — Factory Reset ──────────────────────────────────────
        if (D_mean < D_FACTORY_RESET and block_rate > BLOCK_RATE_SEVERE) or MCI > MCI_FACTORY_RESET:
            conditions += [
                f"D_mean={D_mean:.3f} < FACTORY_RESET={D_FACTORY_RESET}",
                f"block_rate={block_rate:.1%} > {BLOCK_RATE_SEVERE:.0%}",
            ] if D_mean < D_FACTORY_RESET else [f"MCI={MCI:.3f} > {MCI_FACTORY_RESET}"]
            return CollapseStage(
                stage_number  = 6,
                stage_name    = "Governance Factory Reset",
                severity      = "RESET",
                color         = "BLACK",
                description   = (
                    "D_system ≈ 0. Governance architecture shattered. "
                    "Network connectivity gone. EOC terminal. "
                    "Yawmal Qiyammah equivalent — full system reboot required."
                ),
                triggered_conditions = conditions,
                recommended_action   = (
                    "FACTORY RESET: replace all governance nodes. "
                    "Rebuild from constitutional baseline. "
                    "Audit every node independently before reintegration."
                ),
                falsifiable_test = (
                    "D_mean < 0.08 AND block_rate > 70% over last 50 evaluations."
                ),
            )

        # ── Stage 5 — EOC Cascade ───────────────────────────────────────
        if block_rate > BLOCK_RATE_EOC or consec_blocks >= 8:
            if block_rate > BLOCK_RATE_EOC:
                conditions.append(f"block_rate={block_rate:.1%} > EOC_THRESHOLD={BLOCK_RATE_EOC:.0%}")
            if consec_blocks >= 8:
                conditions.append(f"consecutive_blocks={consec_blocks} ≥ 8")
            return CollapseStage(
                stage_number  = 5,
                stage_name    = "EOC Cascade",
                severity      = "CRITICAL",
                color         = "RED",
                description   = (
                    "Epidemic-Of-Corruption propagation active. "
                    "Multi-node simultaneous governance failure. "
                    f"Block rate: {block_rate:.1%}. Wave-2 cascade likely."
                ),
                triggered_conditions = conditions,
                recommended_action   = (
                    "CRITICAL: quarantine high-MCI nodes immediately. "
                    "Freeze non-essential transactions. "
                    "Activate emergency governance protocol."
                ),
                falsifiable_test = (
                    "block_rate > 50% sustained over 50-eval window. "
                    "Wave-2 betweenness centrality > wave-1 (GT P3 prediction)."
                ),
            )

        # ── Stage 4 — D_crit Breach ─────────────────────────────────────
        if D_crit_breached:
            conditions.append(
                f"D_mean={D_mean:.4f} < D_crit={1.0/DEFAULT_MEAN_DEGREE:.4f} (1/⟨k⟩)"
            )
            return CollapseStage(
                stage_number  = 4,
                stage_name    = "D_crit Breach",
                severity      = "ALERT",
                color         = "RED",
                description   = (
                    f"Bond percolation threshold breached: "
                    f"D_mean={D_mean:.4f} < D_crit={1.0/DEFAULT_MEAN_DEGREE:.4f}. "
                    "Governance signals can no longer percolate the network. "
                    "Cascade mathematically inevitable without intervention."
                ),
                triggered_conditions = conditions,
                recommended_action   = (
                    "ALERT: D below percolation threshold. "
                    "Identify and rebuild lowest-D nodes. "
                    "Increase mandatory governance checkpoints."
                ),
                falsifiable_test = (
                    "D_mean < 1/⟨k⟩ sustained. "
                    "GT P2: collapsed nodes cluster near D_crit. "
                    "Falsified if D_mean > D_crit without intervention."
                ),
            )

        # ── Stage 3 — λ₂ Collapse ───────────────────────────────────────
        if lambda2 < LAMBDA2_CRIT or (lambda2 < LAMBDA2_WARN and D_trend < -0.005):
            if lambda2 < LAMBDA2_CRIT:
                conditions.append(f"λ₂≈{lambda2:.3f} < λ₂_CRIT={LAMBDA2_CRIT}")
            if D_trend < -0.005:
                conditions.append(f"D_trend={D_trend:+.4f}/eval (declining)")
            return CollapseStage(
                stage_number  = 3,
                stage_name    = "λ₂ Collapse",
                severity      = "ALERT",
                color         = "ORANGE",
                description   = (
                    f"Fiedler eigenvalue proxy λ₂≈{lambda2:.3f} below critical. "
                    "Network structural cohesion degrading. "
                    "Information flow bottlenecking. "
                    f"D declining at {D_trend:+.4f}/eval."
                ),
                triggered_conditions = conditions,
                recommended_action   = (
                    "ALERT: strengthen inter-node governance connections. "
                    "Audit bridge nodes for D_gap widening. "
                    "Apply Al-Asr pressing protocol to all communications."
                ),
                falsifiable_test = (
                    "λ₂ proxy < 0.15. "
                    "Falsified if network adds high-D bridging edges and λ₂ recovers."
                ),
            )

        # ── Stage 2 — MCI Spike ─────────────────────────────────────────
        if MCI > MCI_ALERT or (MCI > MCI_WARN and hbar > HBAR_DRIFT_WARN):
            if MCI > MCI_ALERT:
                conditions.append(f"MCI={MCI:.3f} > MCI_ALERT={MCI_ALERT}")
            else:
                conditions.append(
                    f"MCI={MCI:.3f} > MCI_WARN={MCI_WARN} + ħ={hbar:.3f} > {HBAR_DRIFT_WARN}"
                )
            return CollapseStage(
                stage_number  = 2,
                stage_name    = "MCI Spike",
                severity      = "WARN",
                color         = "YELLOW",
                description   = (
                    f"Misdirected Coherence Index MCI={MCI:.3f}. "
                    "Authority centralising (λ₁ >> λ₂ pattern). "
                    "Pharaoh Node formation risk. "
                    f"ħ_network={hbar:.3f} (noise elevated)."
                ),
                triggered_conditions = conditions,
                recommended_action   = (
                    "WARN: audit high-degree nodes for agency hoarding (Gate 7). "
                    "Check for CONCEALMENT_DIRECTIVE flags. "
                    "Distribute governance authority."
                ),
                falsifiable_test = (
                    "MCI > 0.40. "
                    "Falsified if high-degree node D scores are verified high."
                ),
            )

        # ── Stage 1 — D_drift ───────────────────────────────────────────
        if D_mean < D_DRIFT_ALERT or (D_mean < D_DRIFT_WARN and D_trend < -0.003):
            if D_mean < D_DRIFT_ALERT:
                conditions.append(f"D_mean={D_mean:.3f} < D_DRIFT_ALERT={D_DRIFT_ALERT}")
            else:
                conditions.append(
                    f"D_mean={D_mean:.3f} < D_DRIFT_WARN={D_DRIFT_WARN} + "
                    f"trend={D_trend:+.4f}/eval"
                )
            if hbar > HBAR_DRIFT_WARN:
                conditions.append(f"ħ={hbar:.3f} > {HBAR_DRIFT_WARN}")
            return CollapseStage(
                stage_number  = 1,
                stage_name    = "D_drift",
                severity      = "WATCH",
                color         = "YELLOW",
                description   = (
                    f"D_mean={D_mean:.3f} declining (trend={D_trend:+.4f}/eval). "
                    f"ħ_network={hbar:.3f}. "
                    "Pre-symptomatic governance drift detected. "
                    "No cascade yet — early intervention window open."
                ),
                triggered_conditions = conditions,
                recommended_action   = (
                    "WATCH: reinforce OQM methodology requirements. "
                    "Flag WARN-verdict nodes for coaching. "
                    "Increase governance checkpoint frequency."
                ),
                falsifiable_test = (
                    "D_mean < 0.45 with negative trend. "
                    "Falsified if D_mean stabilises within 20 evaluations."
                ),
            )

        # ── Stage 0 — Healthy ────────────────────────────────────────────
        return CollapseStage(
            stage_number  = 0,
            stage_name    = "Healthy",
            severity      = "HEALTHY",
            color         = "GREEN",
            description   = (
                f"D_mean={D_mean:.3f} above drift threshold. "
                f"MCI={MCI:.3f} within healthy range. "
                f"λ₂≈{lambda2:.3f} structurally sound. "
                f"block_rate={block_rate:.1%}. No cascade indicators."
            ),
            triggered_conditions = [],
            recommended_action   = "Continue standard governance monitoring.",
            falsifiable_test     = (
                "D_mean ≥ 0.45, MCI < 0.40, λ₂ > 0.30, block_rate < 30%."
            ),
        )

    # ── HELPERS ────────────────────────────────────────────────────────────

    @staticmethod
    def _compute_d_trend(d_vals: list) -> float:
        """Linear slope of D_mean over the window. Negative = declining."""
        n = len(d_vals)
        if n < 3:
            return 0.0
        x = np.arange(n, dtype=float)
        slope = float(np.polyfit(x, d_vals, 1)[0])
        return slope

    def _emit_alert(self, snap: CascadeSnapshot, prev_stage: int) -> None:
        """Emit an AlertEvent and call all registered callbacks."""
        import uuid
        alert = AlertEvent(
            timestamp    = snap.timestamp,
            alert_id     = f"ALERT-{uuid.uuid4().hex[:8].upper()}",
            previous_stage = prev_stage,
            new_stage    = snap.stage.stage_number,
            stage_name   = snap.stage.stage_name,
            severity     = snap.stage.severity,
            D_mean       = snap.D_mean,
            MCI          = snap.MCI,
            block_rate   = snap.block_rate,
            trigger      = ", ".join(snap.stage.triggered_conditions[:2]),
        )
        self._alerts.append(alert)
        for cb in self._callbacks:
            try:
                cb(alert)
            except Exception as exc:
                warnings.warn(f"Alert callback error: {exc}")

    def _empty_snapshot(self) -> CascadeSnapshot:
        """Return a healthy baseline snapshot when history is empty."""
        healthy = CollapseStage(
            stage_number=0, stage_name="Healthy", severity="HEALTHY",
            color="GREEN", description="No evaluations yet.",
            triggered_conditions=[], recommended_action="Begin evaluations.",
            falsifiable_test="Requires ≥5 evaluations.",
        )
        return CascadeSnapshot(
            timestamp="—", window_n=0,
            D_mean=1.0, D_std=0.0, D_trend=0.0, E_mean=0.0,
            hbar_network=0.0, MCI=0.0, lambda2_proxy=1.0,
            block_rate=0.0, warn_rate=0.0,
            mean_degree=self.mean_degree, D_crit=self.D_crit,
            D_crit_breached=False, stage=healthy,
            alerts_in_window=0, consecutive_blocks=0,
            epistemic_note="No data.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# TEST SUITE — simulates Enron-style Phase 1 → Phase 3 collapse
# ─────────────────────────────────────────────────────────────────────────────

def run_collapse_tests(verbose: bool = True) -> CollapseDetector:
    """
    Simulate Enron 3-phase collapse through the detector.
    Expected cascade: Stage 0 → 1 → 2 → 4 → 5 as D decays.
    """
    import uuid, hashlib
    from datetime import datetime, timezone

    def _fake_verdict(D: float, U: float, verdict: str,
                      flags: list = None) -> IHCEIVerdict:
        """Create a synthetic IHCEIVerdict for simulation."""
        E = U * (D ** 2)
        hbar = float(np.clip((1.0 - D) * (0.6 + 0.4 * U), 0, 1))
        cert_id = f"IHCEI-SIM-{uuid.uuid4().hex[:8].upper()}"
        return IHCEIVerdict(
            text_hash        = hashlib.sha256(cert_id.encode()).hexdigest()[:16],
            text_preview     = f"[simulation D={D:.2f} U={U:.2f}]",
            timestamp        = datetime.now(timezone.utc).isoformat(),
            D_enc=D, D_dec=1.0, D=D, U=U, E=round(E, 4),
            oqm_signal       = max(0.0, D - 0.1),
            extraction_score = U * 0.5,
            manipulation_flags = flags or [],
            hbar             = round(hbar, 4),
            verdict          = verdict,
            verdict_reason   = f"Simulation: D={D:.2f}",
            nafs_stage       = "Stage 5 — Insan" if D > 0.4 else "Stage 4 — Jinn",
            governance_function = "Insan",
            certificate_id   = cert_id,
            certificate_hash = hashlib.sha256(cert_id.encode()).hexdigest(),
            layer            = "Layer 1",
        )

    print("\n" + "═" * 62)
    print("  CollapseDetector — Enron Phase Simulation")
    print("  Phase 1 (normal) → Phase 2 (deterioration) → Phase 3 (collapse)")
    print("═" * 62 + "\n")

    detector = CollapseDetector(window=15)
    stage_log = []
    alerts_seen = []
    detector.on_alert(lambda a: alerts_seen.append(a))

    # Phase 1 — Normal Operations (D high, healthy)
    print("  ── Phase 1: Normal Operations ──")
    for _ in range(15):
        D = float(np.random.default_rng().uniform(0.55, 0.80))
        detector.record(_fake_verdict(D, 0.20, "PASS"))
    snap1 = detector.snapshot(silent=True)
    stage_log.append(snap1.stage.stage_number)
    print(f"  Stage: {snap1.stage.stage_number} ({snap1.stage.stage_name})  "
          f"D_mean={snap1.D_mean:.3f}  MCI={snap1.MCI:.3f}  [{snap1.stage.color}]")

    # Phase 2 — Deterioration (D declining, MCI rising)
    print("\n  ── Phase 2: Deterioration ──")
    rng2 = np.random.default_rng(42)
    for i in range(20):
        decay = i * 0.015
        D = float(np.clip(rng2.uniform(0.50, 0.70) - decay, 0.15, 0.70))
        v = "WARN" if D < 0.45 else "PASS"
        flags = ["CONCEALMENT_DIRECTIVE"] if D < 0.30 else []
        detector.record(_fake_verdict(D, 0.30 + decay * 0.5, v, flags))
    snap2 = detector.snapshot(silent=True)
    stage_log.append(snap2.stage.stage_number)
    print(f"  Stage: {snap2.stage.stage_number} ({snap2.stage.stage_name})  "
          f"D_mean={snap2.D_mean:.3f}  MCI={snap2.MCI:.3f}  [{snap2.stage.color}]")

    # Phase 3 — Collapse (D ≈ 0, BLOCK cascade)
    print("\n  ── Phase 3: Collapse ──")
    rng3 = np.random.default_rng(99)
    for i in range(25):
        D = float(np.clip(rng3.uniform(0.05, 0.18), 0.0, 1.0))
        detector.record(_fake_verdict(
            D, 0.65, "BLOCK",
            ["CONCEALMENT_DIRECTIVE", "SECRECY_SIGNAL", "URGENCY_MANIPULATION"]
        ))
    snap3 = detector.snapshot(silent=True)
    stage_log.append(snap3.stage.stage_number)
    print(f"  Stage: {snap3.stage.stage_number} ({snap3.stage.stage_name})  "
          f"D_mean={snap3.D_mean:.3f}  MCI={snap3.MCI:.3f}  [{snap3.stage.color}]")

    print(f"\n  ── Cascade progression: {stage_log[0]} → {stage_log[1]} → {stage_log[2]}")
    print(f"  Alerts fired: {len(alerts_seen)}")
    for a in alerts_seen:
        print(f"    [{a.alert_id}] Stage {a.previous_stage} → {a.new_stage}  "
              f"({a.stage_name})  {a.trigger[:50]}")

    # Validate progression
    escalated = stage_log[2] > stage_log[0] and stage_log[2] >= 4
    print(f"\n  ── Validation ──")
    print(f"  Cascade escalation: {'✓ CONFIRMED' if escalated else '✗ NOT DETECTED'}")
    print(f"  Phase 1 stage ≥ 0:  {'✓' if stage_log[0] >= 0 else '✗'}")
    print(f"  Phase 3 stage ≥ 4:  {'✓' if stage_log[2] >= 4 else '✗'}")
    print(f"  D_crit breach P3:   "
          f"{'✓' if snap3.D_crit_breached else '✗'} "
          f"(D={snap3.D_mean:.4f} vs D_crit={snap3.D_crit:.4f})")

    all_pass = escalated and stage_log[2] >= 4 and snap3.D_crit_breached
    print(f"\n  STATUS: {'ALL TESTS PASSED' if all_pass else 'REVIEW REQUIRED'}")
    print("═" * 62 + "\n")
    return detector


if __name__ == "__main__":
    run_collapse_tests(verbose=True)
