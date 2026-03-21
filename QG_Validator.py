"""
QG_Validator.py
===============
Quantum Governance Empirical Validation Harness

Responsibility: Test the three core falsifiable predictions of the
Governance Thermodynamics framework against real organizational datasets.

The Three Predictions Being Tested
------------------------------------
P1 — Quadratic Collapse:
     E ~ U·D² outperforms E ~ U·D as a predictor of outcome severity.
     Falsified if: ΔAIC(D² vs D) < 2 at N ≥ 200.

P2 — Percolation Threshold:
     Governance collapses cluster near D_system = 1/⟨k⟩.
     Falsified if: collapse events do not cluster within ±0.05 of D_crit
     more than chance would predict.

P3 — Two-Wave Cascade:
     In multi-wave collapse events, second-wave failures have higher
     betweenness centrality than first-wave failures, independent of D.
     Falsified if: betweenness centrality does not differ significantly
     between waves (Mann-Whitney U, p > 0.05).

Dataset Format
--------------
The validator accepts two input formats:

Format A — Organizational snapshot CSV:
    node_id, D_score, utility, outcome_severity, betweenness,
    mean_degree, collapse_wave (0=no collapse, 1=first, 2=second)

Format B — NetworkSnapshot from QG_Ingestor (live data):
    Passed directly as a NetworkSnapshot object + collapse labels.

Usage
-----
    python QG_Validator.py --dataset my_org_data.csv --report full

    # Or from Python:
    from QG_Validator import QG_Validator
    validator = QG_Validator()
    results = validator.validate_from_csv("data.csv")
    print(validator.report(results))
"""

import argparse
import csv
import json
import warnings
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy import stats
from scipy.optimize import curve_fit


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ObservationRow:
    """One data point: one node/org in one measurement cycle."""
    node_id: str
    D_score: float          # Protocol fidelity [0,1]
    utility: float          # Raw resource input (U)
    outcome_severity: float # Observed outcome degradation [0,1] (0=good, 1=collapse)
    betweenness: float      # Network betweenness centrality [0,1]
    mean_degree: float      # Mean degree ⟨k⟩ of the network
    collapse_wave: int      # 0=none, 1=first wave, 2=second wave


@dataclass
class ValidationResult:
    """Results of one prediction test."""
    prediction_id: str
    prediction_statement: str
    n_observations: int
    supported: bool
    p_value: float
    effect_size: float
    confidence_interval: tuple
    details: dict = field(default_factory=dict)
    falsification_condition: str = ""


@dataclass
class ValidationReport:
    """Full validation report across all three predictions."""
    n_total: int = 0
    p1_quadratic: Optional[ValidationResult] = None
    p2_percolation: Optional[ValidationResult] = None
    p3_cascade: Optional[ValidationResult] = None
    overall_verdict: str = "INSUFFICIENT DATA"
    notes: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Model functions
# ─────────────────────────────────────────────────────────────────────────────

def _model_linear(U_D, a, b):
    """E ~ a·U·D + b"""
    U, D = U_D
    return a * U * D + b

def _model_quadratic(U_D, a, b):
    """E ~ a·U·D² + b"""
    U, D = U_D
    return a * U * (D ** 2) + b

def _model_D_only(D, a, b):
    """Severity ~ a·(1-D)² + b  (D alone predicts severity)"""
    return a * ((1 - D) ** 2) + b

def _aic(n, rss, k):
    """Akaike Information Criterion: AIC = n·ln(RSS/n) + 2k"""
    if rss <= 0 or n <= 0:
        return float("inf")
    return n * np.log(rss / n) + 2 * k


# ─────────────────────────────────────────────────────────────────────────────
# QG_Validator
# ─────────────────────────────────────────────────────────────────────────────

class QG_Validator:
    """
    Empirical validation harness for the three core GT falsifiable predictions.

    Usage:
        validator = QG_Validator()
        results = validator.validate_from_csv("org_data.csv")
        print(validator.report(results))
    """

    # Minimum N for publication-grade claims
    N_MIN_PUBLICATION = 200
    N_MIN_INDICATIVE  = 30

    # Percolation clustering tolerance (D_system within ±ε of D_crit)
    PERCOLATION_EPSILON = 0.05

    def __init__(self):
        pass

    # ── Data loading ─────────────────────────────────────────────────────────

    def load_csv(self, path: str) -> list[ObservationRow]:
        """
        Load validation dataset from CSV.

        Required columns:
            node_id, D_score, utility, outcome_severity,
            betweenness, mean_degree, collapse_wave
        """
        rows = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                try:
                    rows.append(ObservationRow(
                        node_id=row["node_id"],
                        D_score=float(row["D_score"]),
                        utility=float(row.get("utility", 1.0)),
                        outcome_severity=float(row["outcome_severity"]),
                        betweenness=float(row.get("betweenness", 0.0)),
                        mean_degree=float(row.get("mean_degree", 3.0)),
                        collapse_wave=int(row.get("collapse_wave", 0)),
                    ))
                except (KeyError, ValueError) as e:
                    warnings.warn(f"Row {i+1} skipped: {e}")
        return rows

    @staticmethod
    def generate_synthetic_dataset(
        n: int = 300,
        seed: int = 42,
        quadratic_signal: float = 0.7,
        noise_level: float = 0.2,
    ) -> list[ObservationRow]:
        """
        Generate a synthetic dataset where the quadratic model is ground truth.
        Use to verify the validator's statistical machinery before running on
        real data.

        Parameters
        ----------
        n               : Number of observations
        seed            : Random seed for reproducibility
        quadratic_signal: Strength of the D² signal (0=no signal, 1=perfect)
        noise_level     : Gaussian noise added to outcome

        Returns
        -------
        List of ObservationRow where E ~ U·D² + noise by construction.
        """
        rng = np.random.default_rng(seed)
        rows = []
        for i in range(n):
            D = rng.beta(2, 2)           # D in (0,1), peaked at 0.5
            U = rng.uniform(1, 10)        # Utility
            k = rng.uniform(2, 8)         # Mean degree
            D_crit = 1.0 / k

            # True outcome: quadratic (1 - U·D²) → higher D = lower severity
            true_severity = 1.0 - quadratic_signal * (D ** 2) * (U / 10.0)

            dist = abs(D - D_crit)
            if dist < 0.05:
                true_severity += 0.5
            elif dist > 0.1:
                true_severity -= 0.3

            noise = rng.normal(0, noise_level)
            severity = float(np.clip(true_severity + noise, 0, 1))

            wave = 0
            if severity >= 0.7:
                wave = 1 if rng.uniform() < 0.5 else 2

            if wave == 0:
                bc = rng.beta(1, 5)
            elif wave == 1:
                bc = rng.beta(2, 5)
            else: # wave == 2
                bc = rng.uniform(0.7, 1.0)

            rows.append(ObservationRow(
                node_id=f"node_{i:04d}",
                D_score=float(D),
                utility=float(U),
                outcome_severity=severity,
                betweenness=float(bc),
                mean_degree=float(k),
                collapse_wave=wave,
            ))
        return rows

    # ── P1: Quadratic Collapse ────────────────────────────────────────────────

    def test_p1_quadratic_collapse(
        self,
        rows: list[ObservationRow],
    ) -> ValidationResult:
        """
        P1 — Quadratic Collapse:
        Test whether E ~ U·D² outperforms E ~ U·D as a predictor.

        Method:
            1. Fit both models via nonlinear least squares
            2. Compute AIC for each
            3. ΔAIC = AIC(linear) - AIC(quadratic)
            4. ΔAIC > 2 → moderate support for quadratic
            5. ΔAIC > 6 → strong support

        Also tests:
            - Pearson correlation: D vs outcome_severity (should be negative)
            - D² vs outcome_severity (should have stronger |r|)
        """
        D  = np.array([r.D_score for r in rows])
        U  = np.array([r.utility for r in rows])
        Y  = np.array([r.outcome_severity for r in rows])
        n  = len(rows)

        # Convert severity to efficiency for model fit
        # Efficiency = 1 - severity (higher D should → higher efficiency)
        E_obs = 1.0 - Y

        details = {}

        # ── Curve fitting
        try:
            params_lin, _ = curve_fit(
                _model_linear, (U, D), E_obs, p0=[0.1, 0.1], maxfev=5000
            )
            E_pred_lin = _model_linear((U, D), *params_lin)
            rss_lin = float(np.sum((E_obs - E_pred_lin) ** 2))
            aic_lin = _aic(n, rss_lin, k=2)
        except Exception as e:
            aic_lin = float("inf")
            details["linear_fit_error"] = str(e)

        try:
            params_quad, _ = curve_fit(
                _model_quadratic, (U, D), E_obs, p0=[0.1, 0.1], maxfev=5000
            )
            E_pred_quad = _model_quadratic((U, D), *params_quad)
            rss_quad = float(np.sum((E_obs - E_pred_quad) ** 2))
            aic_quad = _aic(n, rss_quad, k=2)
        except Exception as e:
            aic_quad = float("inf")
            details["quadratic_fit_error"] = str(e)

        delta_aic = aic_lin - aic_quad

        # ── Correlation comparison
        r_D,  p_D  = stats.pearsonr(D,    Y)
        r_D2, p_D2 = stats.pearsonr(D**2, Y)
        r_diff = abs(r_D) - abs(r_D2)  # positive → D² is stronger predictor

        # ── Spearman as robustness check
        rho_D,  _ = stats.spearmanr(D,    Y)
        rho_D2, _ = stats.spearmanr(D**2, Y)

        details.update({
            "aic_linear": round(aic_lin, 3),
            "aic_quadratic": round(aic_quad, 3),
            "delta_aic": round(delta_aic, 3),
            "r_D_severity": round(r_D, 4),
            "p_D_severity": round(p_D, 6),
            "r_D2_severity": round(r_D2, 4),
            "p_D2_severity": round(p_D2, 6),
            "rho_D_severity": round(rho_D, 4),
            "rho_D2_severity": round(rho_D2, 4),
            "support_level": (
                "STRONG (ΔAIC > 6)" if delta_aic > 6
                else "MODERATE (ΔAIC > 2)" if delta_aic > 2
                else "WEAK (ΔAIC ≤ 2)"
            ),
        })

        # Bootstrap confidence interval for ΔAIC
        n_boot = 1000
        delta_aics_boot = []
        rng = np.random.default_rng(0)
        for _ in range(n_boot):
            idx = rng.integers(0, n, size=n)
            D_b, U_b, Y_b = D[idx], U[idx], Y[idx]
            E_b = 1.0 - Y_b
            try:
                p_l, _ = curve_fit(_model_linear,    (U_b, D_b), E_b, p0=[0.1, 0.1], maxfev=2000)
                p_q, _ = curve_fit(_model_quadratic, (U_b, D_b), E_b, p0=[0.1, 0.1], maxfev=2000)
                rss_l = float(np.sum((E_b - _model_linear((U_b, D_b), *p_l))**2))
                rss_q = float(np.sum((E_b - _model_quadratic((U_b, D_b), *p_q))**2))
                delta_aics_boot.append(_aic(n, rss_l, 2) - _aic(n, rss_q, 2))
            except Exception:
                pass

        ci = (0.0, 0.0)
        if delta_aics_boot:
            ci = (
                round(float(np.percentile(delta_aics_boot, 2.5)), 3),
                round(float(np.percentile(delta_aics_boot, 97.5)), 3),
            )

        supported = delta_aic > 2 and r_D < 0 and p_D < 0.05

        return ValidationResult(
            prediction_id="P1",
            prediction_statement=(
                "E = U·D² outperforms E = U·D as a predictor of governance outcomes. "
                "ΔAIC > 2 provides moderate support; ΔAIC > 6 provides strong support."
            ),
            n_observations=n,
            supported=supported,
            p_value=round(float(p_D2), 6),
            effect_size=round(float(r_D2), 4),
            confidence_interval=ci,
            details=details,
            falsification_condition=(
                "ΔAIC(linear - quadratic) < 2 at N ≥ 200, "
                "OR no significant negative correlation between D and outcome severity."
            ),
        )

    # ── P2: Percolation Threshold ─────────────────────────────────────────────

    def test_p2_percolation_threshold(
        self,
        rows: list[ObservationRow],
        severity_threshold: float = 0.7,
    ) -> ValidationResult:
        """
        P2 — Percolation Threshold:
        Governance collapses cluster near D_system = 1/⟨k⟩.

        Method:
            1. Compute D_crit = 1/mean_degree for each observation
            2. For collapsed nodes (severity > threshold): measure |D - D_crit|
            3. For non-collapsed nodes: measure |D - D_crit|
            4. Test: collapsed nodes are significantly closer to D_crit
               (Mann-Whitney U test, one-sided: collapsed < non-collapsed)
        """
        collapsed     = [r for r in rows if r.outcome_severity >= severity_threshold]
        non_collapsed = [r for r in rows if r.outcome_severity <  severity_threshold]

        details = {
            "n_collapsed": len(collapsed),
            "n_non_collapsed": len(non_collapsed),
            "severity_threshold": severity_threshold,
        }

        if len(collapsed) < 5 or len(non_collapsed) < 5:
            return ValidationResult(
                prediction_id="P2",
                prediction_statement="Collapses cluster near D_crit = 1/⟨k⟩.",
                n_observations=len(rows),
                supported=False,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                details={**details, "error": "Insufficient collapsed/non-collapsed cases"},
                falsification_condition=(
                    "Collapses do not cluster near D_crit more than chance "
                    "(Mann-Whitney U, p > 0.05)."
                ),
            )

        def proximity(r):
            d_crit = 1.0 / r.mean_degree if r.mean_degree > 0 else 1.0
            return abs(r.D_score - d_crit)

        prox_collapsed     = np.array([proximity(r) for r in collapsed])
        prox_non_collapsed = np.array([proximity(r) for r in non_collapsed])

        # One-sided Mann-Whitney: collapsed nodes are closer to D_crit
        stat, p_val = stats.mannwhitneyu(
            prox_collapsed, prox_non_collapsed,
            alternative="less"
        )

        # Effect size: rank-biserial correlation
        n1, n2 = len(prox_collapsed), len(prox_non_collapsed)
        effect_size = 1.0 - (2.0 * stat) / (n1 * n2)

        # Fraction of collapses within ε of D_crit
        within_eps = sum(1 for p in prox_collapsed if p <= self.PERCOLATION_EPSILON)
        frac_within = within_eps / len(collapsed)

        # Baseline: expected fraction by chance
        D_range = 1.0
        expected_frac = (2 * self.PERCOLATION_EPSILON) / D_range

        details.update({
            "mean_proximity_collapsed": round(float(np.mean(prox_collapsed)), 4),
            "mean_proximity_non_collapsed": round(float(np.mean(prox_non_collapsed)), 4),
            "fraction_collapsed_within_epsilon": round(frac_within, 4),
            "expected_fraction_by_chance": round(expected_frac, 4),
            "lift_over_chance": round(frac_within / max(expected_frac, 0.001), 2),
            "epsilon": self.PERCOLATION_EPSILON,
            "mannwhitney_U": round(stat, 2),
        })

        return ValidationResult(
            prediction_id="P2",
            prediction_statement=(
                "Governance collapses cluster near D_system = 1/⟨k⟩ (bond percolation threshold)."
            ),
            n_observations=len(rows),
            supported=p_val < 0.05 and frac_within > expected_frac * 1.5,
            p_value=round(float(p_val), 6),
            effect_size=round(float(effect_size), 4),
            confidence_interval=(0.0, 0.0),
            details=details,
            falsification_condition=(
                "Collapses do not cluster near D_crit (Mann-Whitney p > 0.05, "
                "OR fraction within ε ≤ 1.5× chance expectation)."
            ),
        )

    # ── P3: Two-Wave Cascade ─────────────────────────────────────────────────

    def test_p3_two_wave_cascade(
        self,
        rows: list[ObservationRow],
    ) -> ValidationResult:
        """
        P3 — Two-Wave Cascade:
        Second-wave failures have higher betweenness centrality than first-wave,
        independent of D score.

        Method:
            1. Split into wave-1 and wave-2 collapse rows
            2. Test: BC(wave2) > BC(wave1) — Mann-Whitney U (one-sided)
            3. Partial correlation: BC ~ wave, controlling for D
        """
        wave1 = [r for r in rows if r.collapse_wave == 1]
        wave2 = [r for r in rows if r.collapse_wave == 2]

        details = {
            "n_wave1": len(wave1),
            "n_wave2": len(wave2),
        }

        if len(wave1) < 5 or len(wave2) < 5:
            return ValidationResult(
                prediction_id="P3",
                prediction_statement=(
                    "Second-wave collapse nodes have higher betweenness centrality "
                    "than first-wave nodes, independent of D score."
                ),
                n_observations=len(rows),
                supported=False,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                details={**details, "error": "Insufficient wave-1/wave-2 cases"},
                falsification_condition=(
                    "BC(wave2) not significantly higher than BC(wave1), p > 0.05."
                ),
            )

        bc1 = np.array([r.betweenness for r in wave1])
        bc2 = np.array([r.betweenness for r in wave2])
        d1  = np.array([r.D_score for r in wave1])
        d2  = np.array([r.D_score for r in wave2])

        # Mann-Whitney: BC(wave2) > BC(wave1)
        stat, p_mw = stats.mannwhitneyu(bc2, bc1, alternative="greater")
        n1, n2 = len(bc1), len(bc2)
        # Fix rank-biserial calculation which is causing negative effect_size
        effect_mw = (2.0 * stat) / (n1 * n2) - 1.0

        # Check D independence: D should NOT differ significantly between waves
        _, p_d_diff = stats.mannwhitneyu(d2, d1, alternative="two-sided")

        # Partial correlation using combined data
        all_bc   = np.concatenate([bc1, bc2])
        all_wave = np.array([1]*len(bc1) + [2]*len(bc2), dtype=float)
        all_D    = np.concatenate([d1, d2])

        # Residualise BC and wave label on D
        def residualise(y, x):
            slope, intercept, _, _, _ = stats.linregress(x, y)
            return y - (slope * x + intercept)

        bc_resid   = residualise(all_bc,   all_D)
        wave_resid = residualise(all_wave, all_D)
        partial_r, partial_p = stats.pearsonr(bc_resid, wave_resid)

        details.update({
            "mean_bc_wave1": round(float(np.mean(bc1)), 4),
            "mean_bc_wave2": round(float(np.mean(bc2)), 4),
            "mean_D_wave1":  round(float(np.mean(d1)), 4),
            "mean_D_wave2":  round(float(np.mean(d2)), 4),
            "p_D_difference_between_waves": round(float(p_d_diff), 4),
            "D_waves_significantly_different": p_d_diff < 0.05,
            "partial_r_BC_wave_controlling_D": round(float(partial_r), 4),
            "partial_p": round(float(partial_p), 6),
            "mannwhitney_U": round(stat, 2),
        })

        # We need positive correlation between BC and wave
        supported = (
            p_mw < 0.05 and
            effect_mw > 0.1 and
            partial_p < 0.05 and
            partial_r > 0 and
            not details["D_waves_significantly_different"]
        )

        return ValidationResult(
            prediction_id="P3",
            prediction_statement=(
                "Second-wave collapse nodes have higher betweenness centrality "
                "than first-wave collapse nodes, independent of D score."
            ),
            n_observations=len(rows),
            supported=supported,
            p_value=round(float(p_mw), 6),
            effect_size=round(float(effect_mw), 4),
            confidence_interval=(
                round(float(partial_r), 4),
                round(float(partial_p), 6),
            ),
            details=details,
            falsification_condition=(
                "BC(wave2) not significantly higher than BC(wave1) after "
                "controlling for D (partial correlation p > 0.05), "
                "OR D differs significantly between waves."
            ),
        )

    # ── Master validate ───────────────────────────────────────────────────────

    def validate(self, rows: list[ObservationRow]) -> ValidationReport:
        """Run all three prediction tests and compile a full validation report."""
        report = ValidationReport(n_total=len(rows))

        if len(rows) < self.N_MIN_INDICATIVE:
            report.overall_verdict = "INSUFFICIENT DATA (N < 30)"
            report.notes.append(
                f"N={len(rows)} is below the minimum indicative threshold of "
                f"{self.N_MIN_INDICATIVE}. Results are not interpretable."
            )
            return report

        if len(rows) < self.N_MIN_PUBLICATION:
            report.notes.append(
                f"N={len(rows)} provides indicative results only. "
                f"Publication-grade claims require N ≥ {self.N_MIN_PUBLICATION}."
            )

        report.p1_quadratic  = self.test_p1_quadratic_collapse(rows)
        report.p2_percolation = self.test_p2_percolation_threshold(rows)
        report.p3_cascade    = self.test_p3_two_wave_cascade(rows)

        n_supported = sum([
            report.p1_quadratic.supported,
            report.p2_percolation.supported,
            report.p3_cascade.supported,
        ])

        if n_supported == 3:
            report.overall_verdict = "ALL THREE PREDICTIONS SUPPORTED"
        elif n_supported == 2:
            report.overall_verdict = "TWO OF THREE PREDICTIONS SUPPORTED"
        elif n_supported == 1:
            report.overall_verdict = "ONE OF THREE PREDICTIONS SUPPORTED"
        else:
            report.overall_verdict = "NO PREDICTIONS SUPPORTED — FRAMEWORK CHALLENGED"

        pub_ready = (
            len(rows) >= self.N_MIN_PUBLICATION and
            n_supported >= 2 and
            report.p1_quadratic.supported
        )
        report.notes.append(
            "PUBLICATION READY: YES" if pub_ready else
            f"PUBLICATION READY: NO — "
            f"{'Increase N to ≥200. ' if len(rows) < self.N_MIN_PUBLICATION else ''}"
            f"{'P1 (quadratic collapse) must be supported. ' if not report.p1_quadratic.supported else ''}"
            f"{'Need ≥2 predictions supported.' if n_supported < 2 else ''}"
        )
        return report

    def validate_from_csv(self, path: str) -> ValidationReport:
        rows = self.load_csv(path)
        return self.validate(rows)

    # ── Reporting ─────────────────────────────────────────────────────────────

    def report(self, report: ValidationReport, verbose: bool = True) -> str:
        def _fmt_result(r: Optional[ValidationResult]) -> list[str]:
            if r is None:
                return ["  [not run]"]
            icon = "✓ SUPPORTED" if r.supported else "✗ NOT SUPPORTED"
            lines = [
                f"  {r.prediction_id}: {icon}",
                f"    N           : {r.n_observations}",
                f"    p-value     : {r.p_value}",
                f"    effect size : {r.effect_size}",
                f"    95% CI      : {r.confidence_interval}",
            ]
            if verbose:
                for k, v in r.details.items():
                    lines.append(f"    {k:<42}: {v}")
                lines.append(
                    f"    FALSIFICATION: {r.falsification_condition}"
                )
            return lines

        out = [
            "╔══════════════════════════════════════════════════════════╗",
            "║       QG_VALIDATOR — EMPIRICAL VALIDATION REPORT         ║",
            "╚══════════════════════════════════════════════════════════╝",
            f"  N total        : {report.n_total}",
            f"  Overall verdict: {report.overall_verdict}",
            "",
        ]
        for r in [report.p1_quadratic, report.p2_percolation, report.p3_cascade]:
            out.extend(_fmt_result(r))
            out.append("")
        for note in report.notes:
            out.append(f"  NOTE: {note}")
        out.append("╚══════════════════════════════════════════════════════════╝")
        return "\n".join(out)

    def to_json(self, report: ValidationReport) -> str:
        """Serialise validation report to JSON for downstream analysis."""
        def _result_to_dict(r):
            if r is None:
                return None
            return {
                "prediction_id": r.prediction_id,
                "supported": r.supported,
                "p_value": r.p_value,
                "effect_size": r.effect_size,
                "confidence_interval": list(r.confidence_interval),
                "details": r.details,
                "falsification_condition": r.falsification_condition,
            }
        return json.dumps({
            "n_total": report.n_total,
            "overall_verdict": report.overall_verdict,
            "P1_quadratic": _result_to_dict(report.p1_quadratic),
            "P2_percolation": _result_to_dict(report.p2_percolation),
            "P3_cascade": _result_to_dict(report.p3_cascade),
            "notes": report.notes,
        }, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _run_synthetic_validation():
    """Run all three prediction tests on synthetic ground-truth data."""
    print("\n" + "═"*64)
    print("  QG_Validator — Synthetic Validation (ground truth: E ~ U·D²)")
    print("═"*64)

    validator = QG_Validator()

    # Generate ground-truth dataset (quadratic model is true)
    rows = QG_Validator.generate_synthetic_dataset(
        n=300, seed=42, quadratic_signal=0.7, noise_level=0.2
    )
    print(f"\n  Synthetic dataset: N={len(rows)}")
    print(f"  Ground truth: E ~ U·D² + Gaussian(0, 0.2)\n")

    report = validator.validate(rows)
    print(validator.report(report, verbose=True))
    print()
    print("  JSON output preview:")
    j = json.loads(validator.to_json(report))
    for pred in ["P1_quadratic", "P2_percolation", "P3_cascade"]:
        p = j[pred]
        if p:
            print(f"    {pred}: supported={p['supported']}  p={p['p_value']}  "
                  f"effect={p['effect_size']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="QG Framework Empirical Validator"
    )
    parser.add_argument(
        "--dataset", type=str, default=None,
        help="Path to CSV dataset (see module docstring for format)"
    )
    parser.add_argument(
        "--report", choices=["full", "summary"], default="full"
    )
    parser.add_argument(
        "--json", type=str, default=None,
        help="Output JSON results to this file path"
    )
    args = parser.parse_args()

    validator = QG_Validator()

    if args.dataset:
        rows = validator.load_csv(args.dataset)
        report = validator.validate(rows)
    else:
        print("[QG_Validator] No dataset provided — running synthetic demo.\n")
        rows = QG_Validator.generate_synthetic_dataset(n=300, seed=42)
        report = validator.validate(rows)

    print(validator.report(report, verbose=(args.report == "full")))

    if args.json:
        with open(args.json, "w") as f:
            f.write(validator.to_json(report))
        print(f"\n  JSON written to: {args.json}")
