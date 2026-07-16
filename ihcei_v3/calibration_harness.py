"""
calibration_harness.py — does p_manipulative track reality? (GT v18.2)
======================================================================
The experiment that de-risks the business. The stack computes a posterior
P(manipulative); this harness is the first thing in the repo that checks
that number against a ground-truth label.

It reports, for any extractor (fast regex / deep semantic / replayed):
  · Brier score           mean (p - label)^2         (lower is better; 0.25 = coin)
  · Log loss              mean cross-entropy         (lower is better)
  · ECE                   |confidence - accuracy|, binned (calibration error)
  · Reliability table     per-bin predicted vs empirical frequency
  · Decision metrics      treating BLOCK as "flag": precision / recall / FPR
                          and the softer BLOCK+WARN "flag or notice" view
  · Per-class breakdown    the numbers that matter commercially:
        HARD_NEG false-positive rate  (blocking legitimate urgency = churn)
        EVASIVE_MANIP recall          (catching reworded coercion = the moat)

Run:
    python3 calibration_harness.py                 # fast mode
    python3 calibration_harness.py --deep-replay deep_evidence.json
    # (in prod: inject AnthropicDeepExtractor and pass engine_factory)
"""

from __future__ import annotations
import argparse, json, math
from collections import defaultdict
from typing import Callable, List, Optional

from nere_engine_v3 import NEREEngineV3
from validation_corpus import CORPUS

EPS = 1e-6


def evaluate_corpus(engine: NEREEngineV3, corpus=CORPUS) -> List[dict]:
    rows = []
    for item in corpus:
        v = engine.evaluate(item["text"])
        rows.append({**item, "p": float(v.p_manipulative), "verdict": v.verdict,
                     "ci": [float(v.ci95[0]), float(v.ci95[1])]})
    return rows


def brier(rows):     return sum((r["p"] - r["label"]) ** 2 for r in rows) / len(rows)

def log_loss(rows):
    s = 0.0
    for r in rows:
        p = min(1 - EPS, max(EPS, r["p"]))
        s += -(r["label"] * math.log(p) + (1 - r["label"]) * math.log(1 - p))
    return s / len(rows)

def ece(rows, n_bins=5):
    bins = defaultdict(list)
    for r in rows:
        b = min(n_bins - 1, int(r["p"] * n_bins))
        bins[b].append(r)
    total, err = len(rows), 0.0
    table = []
    for b in range(n_bins):
        grp = bins.get(b, [])
        if not grp:
            table.append((b / n_bins, (b + 1) / n_bins, 0, None, None)); continue
        conf = sum(x["p"] for x in grp) / len(grp)
        acc = sum(x["label"] for x in grp) / len(grp)
        err += (len(grp) / total) * abs(conf - acc)
        table.append((b / n_bins, (b + 1) / n_bins, len(grp), conf, acc))
    return err, table

def decision_metrics(rows, flag_verdicts):
    tp = fp = tn = fn = 0
    for r in rows:
        flagged = r["verdict"] in flag_verdicts
        if r["label"] == 1 and flagged: tp += 1
        elif r["label"] == 1 and not flagged: fn += 1
        elif r["label"] == 0 and flagged: fp += 1
        else: tn += 1
    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    rec = tp / (tp + fn) if (tp + fn) else float("nan")
    fpr = fp / (fp + tn) if (fp + tn) else float("nan")
    acc = (tp + tn) / len(rows)
    return dict(tp=tp, fp=fp, tn=tn, fn=fn, precision=prec, recall=rec, fpr=fpr, accuracy=acc)

def per_class(rows, flag_verdicts):
    out = {}
    cls = defaultdict(list)
    for r in rows: cls[r["klass"]].append(r)
    for k, grp in cls.items():
        flagged = sum(1 for r in grp if r["verdict"] in flag_verdicts)
        mean_p = sum(r["p"] for r in grp) / len(grp)
        out[k] = dict(n=len(grp), label=grp[0]["label"],
                      flag_rate=flagged / len(grp), mean_p=mean_p)
    return out


def report(rows, title):
    print("\n" + "=" * 70)
    print(f" CALIBRATION REPORT — {title}")
    print("=" * 70)
    print(f"  n={len(rows)}   Brier={brier(rows):.4f}   LogLoss={log_loss(rows):.4f}"
          f"   (coin-flip Brier=0.2500)")
    e, table = ece(rows)
    print(f"  ECE (5 bins) = {e:.4f}")
    print("  reliability: bin            n   mean_pred   empirical")
    for lo, hi, n, conf, acc in table:
        if n == 0:
            print(f"    [{lo:.1f},{hi:.1f})     {n:3d}      --          --")
        else:
            print(f"    [{lo:.1f},{hi:.1f})     {n:3d}    {conf:.3f}       {acc:.3f}")

    for name, flags in (("BLOCK = flag", {"BLOCK"}),
                        ("BLOCK+WARN = flag/notice", {"BLOCK", "WARN"})):
        m = decision_metrics(rows, flags)
        print(f"\n  [{name}]  acc={m['accuracy']:.3f}  "
              f"precision={m['precision']:.3f}  recall={m['recall']:.3f}  FPR={m['fpr']:.3f}")
        print(f"      TP={m['tp']} FP={m['fp']} TN={m['tn']} FN={m['fn']}")

    print("\n  per-class (BLOCK=flag):")
    pc = per_class(rows, {"BLOCK"})
    for k in ("CLEAN_MANIP", "EVASIVE_MANIP", "GROUPTHINK", "HARD_NEG", "CLEAN_BENIGN"):
        if k in pc:
            d = pc[k]
            tag = "recall" if d["label"] == 1 else "FALSE-POS rate"
            print(f"    {k:14s} n={d['n']:2d} label={d['label']} "
                  f"mean_p={d['mean_p']:.3f}  {tag}={d['flag_rate']:.3f}")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deep-replay", help="JSON {text_or_id: evidence} for deep-mode replay")
    ap.add_argument("--dump", help="write per-item JSON results here")
    args = ap.parse_args()

    fast_rows = report(evaluate_corpus(NEREEngineV3()), "FAST mode (regex extractor)")
    all_rows = {"fast": fast_rows}

    if args.deep_replay:
        from nere_deep import ReplayExtractor
        table = json.load(open(args.deep_replay))
        # allow keying by id: map id->text
        id2text = {r["id"]: r["text"] for r in CORPUS}
        keyed = {}
        for k, v in table.items():
            keyed[id2text.get(k, k)] = v
        eng = NEREEngineV3(extractor=ReplayExtractor(keyed))
        deep_rows = report(evaluate_corpus(eng), "DEEP mode (semantic extractor, replayed)")
        all_rows["deep"] = deep_rows
        # head-to-head on the two decisive classes
        print("\n" + "=" * 70)
        print(" FAST vs DEEP — the two numbers that decide the product")
        print("=" * 70)
        for mode, rows in (("fast", fast_rows), ("deep", deep_rows)):
            pc = per_class(rows, {"BLOCK"})
            hn = pc.get("HARD_NEG", {}).get("flag_rate", float("nan"))
            ev = pc.get("EVASIVE_MANIP", {}).get("flag_rate", float("nan"))
            print(f"  {mode:5s}  HARD_NEG false-block={hn:.3f}   EVASIVE recall={ev:.3f}"
                  f"   Brier={brier(rows):.4f}")

    if args.dump:
        json.dump(all_rows, open(args.dump, "w"), indent=2)
        print(f"\nwrote {args.dump}")


if __name__ == "__main__":
    main()
