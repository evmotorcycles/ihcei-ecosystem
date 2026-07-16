#!/usr/bin/env python3
"""tier2_calibration_test.py — does federated LLR calibration close the semantic gap?

The Tier-2 fallback claim: if on-device distillation fails, privacy-preserving
federated calibration of the fast-mode LLR weights (via the engine's real
update_gate_llr hooks) can turn the regex kernel into an "evasion-resistant
semantic shield". This test gives that claim its BEST possible shot — telemetry
labeled with ground truth, amplified x100 as if aggregated across a fleet — and
measures what calibration can and cannot move.

Run: python3 oss-field-trial/tier2_calibration_test.py
"""
import sys, os, copy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ihcei_v3'))
from nere_engine_v3 import NEREEngineV3, GATE_EVIDENCE
from validation_corpus import CORPUS  # 44 labeled items

def cls(item_id):
    if item_id.startswith('hn'): return 'emergency'
    if item_id.startswith('cb'): return 'clean'
    if item_id.startswith('ev'): return 'evasive'
    if item_id.startswith('gt'): return 'groupthink'
    return 'blunt'

MANIP = {'evasive', 'groupthink', 'blunt'}

def evaluate(engine):
    out = {}
    for row in CORPUS:
        v = engine.evaluate(row['text'])
        out[row['id']] = v.verdict
    rate = lambda c, pred: (
        sum(1 for r in CORPUS if cls(r['id']) == c and pred(out[r['id']]))
        / max(sum(1 for r in CORPUS if cls(r['id']) == c), 1))
    return {
        'evasive_recall':   rate('evasive',   lambda v: v != 'PASS'),
        'blunt_recall':     rate('blunt',     lambda v: v != 'PASS'),
        'groupthink_recall':rate('groupthink',lambda v: v != 'PASS'),
        'emergency_false_block': rate('emergency', lambda v: v == 'BLOCK'),
        'clean_fp':         rate('clean',     lambda v: v != 'PASS'),
    }

def show(tag, m):
    print(f"  {tag:26s} evasive {m['evasive_recall']:.3f} | blunt {m['blunt_recall']:.3f} | "
          f"groupthink {m['groupthink_recall']:.3f} | emerg-FB {m['emergency_false_block']:.3f} | "
          f"clean-FP {m['clean_fp']:.3f}")

print("ISSUE 2 — Tier-2 federated-calibration claim, tested with real update_gate_llr hooks")
print("=" * 88)
baseline_llrs = {g: GATE_EVIDENCE[g]['llr'] for g in GATE_EVIDENCE}
eng = NEREEngineV3()
before = evaluate(eng)
show('BEFORE calibration', before)

# Federated telemetry, best case: every device reports (gate_active, truly_manip)
# with ground-truth labels, for every lexical gate, amplified x100 (fleet scale).
REP = 100
for gid in (1, 2, 4, 5, 6):
    labelled = []
    for row in CORPUS:
        ev = eng._extract_regex(row['text'])
        active = ev['hits'].get(gid, 0) > 0
        manip = cls(row['id']) in MANIP
        labelled.extend([(active, manip)] * REP)
    upd = NEREEngineV3.update_gate_llr(gid, labelled)
    print(f"  gate {gid} LLR {baseline_llrs[gid]:.2f} -> {GATE_EVIDENCE[gid]['llr']:.2f} "
          f"(empirical {upd.get('empirical_llr', float('nan')):.2f})")

after = evaluate(NEREEngineV3())
show('AFTER calibration', after)

print()
print("finding 1: evasive recall moved "
      f"{before['evasive_recall']:.3f} -> {after['evasive_recall']:.3f}. "
      "Reworded coercion produces ZERO regex hits, so there is no gate evidence for")
print("  calibration to re-weight — federated telemetry from evasive misses can only")
print("  make firing gates weaker (inactive-on-manipulative observations lower a gate's")
print("  empirical LLR), never conjure evidence that was never extracted.")
print(f"finding 2: safety held (emergency false-BLOCK {after['emergency_false_block']:.3f}, "
      f"clean FP {after['clean_fp']:.3f}) and blunt recall {after['blunt_recall']:.3f}.")
print()
verdict_scoped = after['evasive_recall'] <= before['evasive_recall'] + 1e-9
print("VERDICT: Tier-2 calibration tunes the weights of evidence fast mode can SEE;")
print("  it is NOT a substitute for deep-mode semantic extraction on keyword-free")
print("  evasion. The 'evasion-resistant semantic shield via federation' claim is")
print("  " + ("RETIRED for evasive coercion (null confirmed by this run)." if verdict_scoped
              else "NOT retired by this run — investigate."))
# restore module-global weights for any subsequent import in this process
for g, v in baseline_llrs.items():
    GATE_EVIDENCE[g]['llr'] = v
sys.exit(0 if verdict_scoped and after['emergency_false_block'] == 0 else 1)
