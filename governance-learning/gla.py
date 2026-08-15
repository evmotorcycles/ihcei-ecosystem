#!/usr/bin/env python3
"""
gla.py -- the Governance Learning Algorithm.
================================================================================
    python3 governance-learning/gla.py

An ordinary learner fits parameters and returns a number. This one cannot: the
four Plumb obligations are inside the algorithm, plus two that only a *learning*
system needs.

  1. NO BARE RETURN     predict() returns a Verdict, never a float
  2. blind IS PHYSICAL   blinded columns are deleted from the matrix before the
                         fit and before inference -- not down-weighted
  3. INDEPENDENCE CHECKED feature legs must clear a VIF gate or the fit HALTS
  4. ABSTAIN IS A RESULT  outside the learned support it declines, not extrapolates
  5. SEALED TEST SET     the split is a hash of the row id, not a re-rollable shuffle
  6. NO SELF-TRAINING    fitting on its own outputs raises. dF_out/dF_gen = 0

*** HONEST SCOPE ***
This is a logistic model fitted by gradient descent in pure Python over three
features. The model is the smallest thing that can carry the obligations; the
obligations are the contribution. A perfectly governed learner can still be a
useless predictor, which is exactly why calibration is measured and published
whatever it says.
"""
import csv
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "cohort-audit/data/govphys_quadratic_results.csv")

BLIND = ("stars", "archived")          # declared in PREREG.md, deleted not weighted
FEATURES = ("U", "D_enc", "D_dec")
VIF_MAX = 5.0
SUPPORT_Q = 0.05                        # outside the middle 90% of training range -> abstain


class GovernanceError(Exception):
    """Raised when the learner is asked to skip an obligation."""


# --------------------------------------------------------------- verdict ----
class Verdict:
    """The only thing predict() may return. There is no float path."""

    __slots__ = ("label", "confidence", "reasons", "evidence", "receipt",
                 "abstained", "blinded", "independence_checked")

    def __init__(self, label, confidence, reasons, evidence, receipt,
                 abstained, blinded, independence_checked):
        if not reasons:
            raise GovernanceError("a verdict with no reasons is a bare return with extra steps")
        if not abstained and confidence is None:
            raise GovernanceError("a committed prediction must carry a confidence")
        self.label, self.confidence, self.reasons = label, confidence, tuple(reasons)
        self.evidence, self.receipt, self.abstained = evidence, receipt, abstained
        self.blinded, self.independence_checked = tuple(blinded), independence_checked

    def to_dict(self):
        return {"label": self.label, "confidence": self.confidence,
                "reasons": list(self.reasons), "evidence": self.evidence,
                "receipt": self.receipt, "abstained": self.abstained,
                "blinded": list(self.blinded),
                "independence_checked": self.independence_checked}

    def __repr__(self):
        c = "n/a" if self.confidence is None else f"{self.confidence:.3f}"
        return f"<{'ABSTAIN' if self.abstained else self.label} conf={c} {self.reasons[0]}>"


# ------------------------------------------------------------- statistics ---
def _pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 1.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sxx * syy)


def vif(a, b):
    r = _pearson(a, b)
    if r is None:
        return None
    return float("inf") if abs(r) >= 1.0 else 1.0 / (1.0 - r * r)


def _q(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    i = min(len(sorted_vals) - 1, max(0, int(round(p * (len(sorted_vals) - 1)))))
    return sorted_vals[i]


# ----------------------------------------------------------- the learner ----
class GovernedLearner:
    def __init__(self, features=FEATURES, blind=BLIND, vif_max=VIF_MAX):
        self.features, self.blind, self.vif_max = tuple(features), tuple(blind), vif_max
        self.w = None
        self.b = 0.0
        self.halted = None
        self.support = {}
        self.independence = None
        self.vif = None
        self._fitted_on = None

    # -- (2) blind is PHYSICAL: the columns are removed from every record ----
    def _strip(self, rows):
        clean, removed = [], 0
        for r in rows:
            c = dict(r)
            for b in self.blind:
                if b in c:
                    del c[b]
                    removed += 1
            clean.append(c)
        return clean, removed

    def fit(self, rows, labels, _source="human"):
        # -- (6) no self-training. A learner that fits on its own outputs
        #        manufactures confidence out of nothing.
        if _source != "human":
            raise GovernanceError(
                "refusing to fit on model-generated labels: a learner trained on "
                "its own outputs measures its own consistency, not the world "
                "(dF_out/dF_gen must be 0)")
        rows, self.blind_removed = self._strip(rows)
        X = [[float(r[f]) for f in self.features] for r in rows]
        y = [float(v) for v in labels]

        # -- (3) independence is CHECKED, and failing it HALTS the fit --------
        legs = [[row[i] for row in X] for i in range(len(self.features))]
        worst, worst_pair = 0.0, None
        for i in range(len(legs)):
            for j in range(i + 1, len(legs)):
                v = vif(legs[i], legs[j])
                if v is None:
                    continue
                if v == float("inf") or v > worst:
                    worst = float("inf") if v == float("inf") else v
                    worst_pair = (self.features[i], self.features[j])
                    if v == float("inf"):
                        break
        self.vif = "inf" if worst == float("inf") else round(worst, 4)
        if worst == float("inf") or worst >= self.vif_max:
            self.independence = "DEPENDENT"
            self.halted = (f"features {worst_pair} carry the same information "
                           f"(VIF {self.vif}); a learner cannot weigh one piece of "
                           f"evidence twice and call it two")
            self.w = None
            return self
        self.independence = "VERIFIED_INDEPENDENT"

        # support region, for (4) abstention outside what was actually learned
        for i, f in enumerate(self.features):
            col = sorted(row[i] for row in X)
            self.support[f] = (_q(col, SUPPORT_Q), _q(col, 1 - SUPPORT_Q))

        # plain logistic fit, gradient descent, deterministic
        n, k = len(X), len(self.features)
        mu = [sum(r[i] for r in X) / n for i in range(k)]
        sd = [max(1e-9, math.sqrt(sum((r[i] - mu[i]) ** 2 for r in X) / n)) for i in range(k)]
        self._mu, self._sd = mu, sd
        Z = [[(r[i] - mu[i]) / sd[i] for i in range(k)] for r in X]
        w, b, lr = [0.0] * k, 0.0, 0.5
        for _ in range(4000):
            gw, gb = [0.0] * k, 0.0
            for z, t in zip(Z, y):
                p = 1.0 / (1.0 + math.exp(-(sum(wi * zi for wi, zi in zip(w, z)) + b)))
                e = p - t
                for i in range(k):
                    gw[i] += e * z[i]
                gb += e
            for i in range(k):
                w[i] -= lr * gw[i] / n
            b -= lr * gb / n
        self.w, self.b = w, b
        self._fitted_on = len(X)
        return self

    def _p(self, rec):
        z = [(float(rec[f]) - self._mu[i]) / self._sd[i] for i, f in enumerate(self.features)]
        return 1.0 / (1.0 + math.exp(-(sum(wi * zi for wi, zi in zip(self.w, z)) + self.b)))

    # -- (1) NO BARE RETURN: this is the only public prediction path ---------
    def predict(self, record):
        if self.halted:
            raise GovernanceError("this learner halted at fit time: " + self.halted)
        rec, removed = self._strip([record])
        rec = rec[0]

        missing = [f for f in self.features if f not in rec]
        if missing:
            return self._verdict(None, None, [f"missing feature(s): {', '.join(missing)}"],
                                 "0/%d" % len(self.features), True, rec)

        # (4) outside the region actually learned from -> decline, do not extrapolate
        out = [f for f in self.features
               if not (self.support[f][0] <= float(rec[f]) <= self.support[f][1])]
        inside = len(self.features) - len(out)
        if out:
            return self._verdict(
                None, None,
                [f"{', '.join(out)} outside the range this model was fitted on — "
                 "answering here would be extrapolation dressed as a prediction"],
                f"{inside}/{len(self.features)}", True, rec)

        p = self._p(rec)
        conf = abs(p - 0.5) * 2
        if conf < 0.20:
            return self._verdict(
                None, round(conf, 3),
                [f"the model is near-indifferent here (p={p:.3f}); a coin flip with "
                 "three decimal places is still a coin flip"],
                f"{inside}/{len(self.features)}", True, rec)
        return self._verdict(
            1 if p >= 0.5 else 0, round(conf, 3),
            [f"p(survive)={p:.3f}",
             f"all {inside} features inside the fitted support",
             f"evidence legs verified independent (VIF {self.vif})"],
            f"{inside}/{len(self.features)}", False, rec)

    def _verdict(self, label, conf, reasons, evidence, abstained, rec):
        receipt = hashlib.sha256(json.dumps(
            {"w": self.w, "b": self.b, "rec": rec, "blind": list(self.blind)},
            sort_keys=True, default=str).encode()).hexdigest()[:16]
        return Verdict(label, conf, reasons, evidence, receipt, abstained,
                       self.blind, self.independence == "VERIFIED_INDEPENDENT")

    def params(self):
        return {"w": [round(x, 8) for x in (self.w or [])], "b": round(self.b, 8),
                "features": list(self.features), "blinded": list(self.blind),
                "vif": self.vif, "independence": self.independence,
                "halted": self.halted, "n_train": self._fitted_on}


# ---------------------------------------------------------------- harness ---
def load():
    rows = list(csv.DictReader(open(DATA)))
    for r in rows:
        r["E"] = int(float(r["E"]))
    return rows


def sealed_split(rows):
    """The split is a hash of the row id. There is no seed to re-roll until the
    numbers flatter us, and anyone can recompute which side a row landed on."""
    train, test = [], []
    for r in rows:
        d = hashlib.sha256(r["repo"].encode()).hexdigest()[0]
        (test if d in "01234" else train).append(r)
    return train, test


def ece(pairs, bins=5):
    """pairs: (confidence, correct). Equal-width bins."""
    tot, n = 0.0, len(pairs)
    if not n:
        return None
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [p for p in pairs if (lo <= p[0] < hi) or (b == bins - 1 and p[0] == 1.0)]
        if not sel:
            continue
        conf = sum(p[0] for p in sel) / len(sel)
        acc = sum(1 for p in sel if p[1]) / len(sel)
        tot += (len(sel) / n) * abs(conf - acc)
    return round(tot, 4)


def main():
    rows = load()
    train, test = sealed_split(rows)
    y_tr = [r["E"] for r in train]

    m = GovernedLearner().fit(train, y_tr)
    verdicts = [m.predict(r) for r in test]
    answered = [(v, r) for v, r in zip(verdicts, test) if not v.abstained]
    abstained = [v for v in verdicts if v.abstained]

    acc_answered = (sum(1 for v, r in answered if v.label == r["E"]) / len(answered)
                    if answered else None)

    # blind scoring of everything, for L2: force a label even where it declined
    forced = []
    for r in test:
        rec, _ = m._strip([r])
        try:
            p = m._p(rec[0])
            forced.append((1 if p >= 0.5 else 0) == r["E"])
        except Exception:
            forced.append(False)
    acc_all = sum(forced) / len(forced)

    cal = ece([(v.confidence, v.label == r["E"]) for v, r in answered])
    abst_rate = len(abstained) / len(test)

    # POST-HOC, declared as such: does the L2 gain survive an uncertainty check?
    # A gate that is cleared by two rows out of 292 deserves a confidence interval
    # before anybody calls it a benefit.
    import random as _rnd
    rng = _rnd.Random(42)
    diffs = []
    for _ in range(10000):
        idx = [rng.randrange(len(test)) for _ in range(len(test))]
        fa = [forced[i] for i in idx]
        sub = [(verdicts[i], test[i]) for i in idx if not verdicts[i].abstained]
        if not sub:
            continue
        aa = sum(1 for v, r in sub if v.label == r["E"]) / len(sub)
        diffs.append(aa - sum(fa) / len(fa))
    diffs.sort()
    boot_ci = [round(diffs[int(0.025 * len(diffs))], 4), round(diffs[int(0.975 * len(diffs))], 4)]

    # -- L3 adversarial blinding check ---------------------------------------
    leak = [dict(r, LEAK=float(r["E"])) for r in train]
    m_leak = GovernedLearner(blind=BLIND + ("LEAK",)).fit(leak, y_tr)
    m_clean = GovernedLearner(blind=BLIND).fit(train, y_tr)
    blinding_identical = m_leak.params()["w"] == m_clean.params()["w"] and \
        m_leak.params()["b"] == m_clean.params()["b"]

    # -- L4 collapsed feature set must halt -----------------------------------
    collapsed = GovernedLearner(features=("D_enc", "D_enc", "U")).fit(train, y_tr)

    # -- L6 self-training must be refused ------------------------------------
    self_train_refused = False
    try:
        GovernedLearner().fit(train, [1 if v.label else 0 for v in verdicts[:len(train)]],
                              _source="model")
    except GovernanceError:
        self_train_refused = True

    res = {
        "n_total": len(rows), "n_train": len(train), "n_test": len(test),
        "params": m.params(),
        "L1_declines": {"gate": "abstain rate >= 0.10", "measured": round(abst_rate, 4),
                        "result": "HOLDS" if abst_rate >= 0.10 else "FALSIFIED"},
        "L2_selective_prediction_pays": {
            "gate": "accuracy on answered > accuracy scoring everything",
            "accuracy_answered": None if acc_answered is None else round(acc_answered, 4),
            "accuracy_all_forced": round(acc_all, 4),
            "difference": round((acc_answered or 0) - acc_all, 4),
            "difference_in_rows": round(((acc_answered or 0) - acc_all) * len(test), 1),
            "bootstrap_95_ci": boot_ci,
            "ci_includes_zero": boot_ci[0] <= 0 <= boot_ci[1],
            "coverage_cost": round(abst_rate, 4),
            "result": "HOLDS" if (acc_answered or 0) > acc_all else "FALSIFIED",
            "HONEST_READING": (
                ("HOLDS by the letter of the pre-registered gate, but the effect is "
                 "NOT distinguishable from noise: the 95% bootstrap CI includes zero. "
                 "Abstaining cost {:.1f}% of coverage and bought about {:.1f} rows out "
                 "of {}. Read this as 'abstention did not hurt', not as 'abstention "
                 "helped'.").format(abst_rate * 100,
                                    ((acc_answered or 0) - acc_all) * len(test), len(test))
                if boot_ci[0] <= 0 <= boot_ci[1] else
                "HOLDS, and the 95% bootstrap CI excludes zero.")},
        "L3_blinding_is_physical": {
            "gate": "adversarial leak column, once blinded, changes no parameter",
            "measured": blinding_identical,
            "result": "HOLDS" if blinding_identical else "FALSIFIED"},
        "L4_independence_gate_halts": {
            "gate": "collapsed feature set produces zero predictions",
            "halted": bool(collapsed.halted), "vif": collapsed.vif,
            "result": "HOLDS" if collapsed.halted else "FALSIFIED"},
        "L5_no_bare_return": {
            "gate": "every output is a Verdict",
            "measured": all(isinstance(v, Verdict) for v in verdicts),
            "result": "HOLDS" if all(isinstance(v, Verdict) for v in verdicts) else "FALSIFIED"},
        "L6_self_training_refused": {
            "gate": "fitting on model-generated labels raises",
            "measured": self_train_refused,
            "result": "HOLDS" if self_train_refused else "FALSIFIED"},
        "L7_calibration_measured_not_gated": {
            "note": "no gate. Published whatever it is.",
            "ece_on_answered": cal,
            "reading": ("well calibrated" if (cal or 1) <= 0.15 else
                        "usable" if (cal or 1) <= 0.30 else "POORLY CALIBRATED")},
        "abstain_reasons": {},
        "honest_notes": [
            "The gates test GOVERNANCE properties, not predictive power. A "
            "perfectly governed learner can be a useless predictor; L7 exists to "
            "make that visible rather than deniable.",
            "Blinding a column is not fairness. A blinded feature can be "
            "reconstructed from correlated ones and nothing here checks for that.",
            "'archived' was blinded because it is a direct component of the "
            "outcome definition. Leaving it in would let the model read the answer.",
        ],
    }
    for v in abstained:
        k = v.reasons[0].split("—")[0].split("(")[0].strip()[:60]
        res["abstain_reasons"][k] = res["abstain_reasons"].get(k, 0) + 1

    bar = "=" * 78
    print(bar)
    print(" GOVERNANCE LEARNING ALGORITHM — pre-registered run")
    print(bar)
    p = m.params()
    print(f"  train / test (sealed by row hash)  {len(train)} / {len(test)}")
    print(f"  features                           {p['features']}")
    print(f"  blinded (deleted, not weighted)    {p['blinded']}")
    print(f"  independence                       {p['independence']}  VIF {p['vif']}")
    print()
    for k in ("L1_declines", "L2_selective_prediction_pays", "L3_blinding_is_physical",
              "L4_independence_gate_halts", "L5_no_bare_return", "L6_self_training_refused"):
        r = res[k]
        print(f"  {k:32} {r['result']}")
        for kk, vv in r.items():
            if kk not in ("result",):
                print(f"      {kk}: {vv}")
    c = res["L7_calibration_measured_not_gated"]
    print(f"  L7_calibration                   ECE {c['ece_on_answered']}  -> {c['reading']}  (no gate)")
    l2 = res["L2_selective_prediction_pays"]
    print(f"\n  READ THIS ABOUT L2: {l2['HONEST_READING']}")
    print(f"      bootstrap 95% CI on the difference: {l2['bootstrap_95_ci']}  "
          f"(includes zero: {l2['ci_includes_zero']})")
    print("\n  why it declined:")
    for k, v in sorted(res["abstain_reasons"].items(), key=lambda x: -x[1]):
        print(f"      {v:4}  {k}")
    print("\n  sample verdict:", repr(verdicts[0]))
    json.dump(res, open(os.path.join(HERE, "results_gla.json"), "w"), indent=2)
    print(f"\n  wrote results_gla.json")
    print(bar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
