#!/usr/bin/env python3
"""Run the pipeline on both drawings and on the padding attack.

Offline, deterministic, no network, no keys.

Predictions locked in prereg_nere.md, sha256
81a0c16b22a81c9d89df8c3153d9cfacc98e7ec5889a292b90f124828b45248c
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from nere import NEREPipeline                                    # noqa: E402
from nere.drawings import (all_literal_toy, locked_five_part,    # noqa: E402
                           padded_six_part, six_part_metaphor_split)

PREREG_SHA = "81a0c16b22a81c9d89df8c3153d9cfacc98e7ec5889a292b90f124828b45248c"


def hit(ok):
    return "HIT" if ok else "MISS"


def main():
    p = NEREPipeline()
    five = locked_five_part()
    six = six_part_metaphor_split()
    padded = padded_six_part()
    toy = all_literal_toy()

    r5, r6, rt = p.run(five), p.run(six), p.run(toy)
    cmp_ = p.compare(six, padded)

    print("=== ARM 1 -- two drawings of one document ===")
    for label, r in (("locked, 5 parts", r5), ("alternative, 6 parts", r6)):
        s = r["structure"]
        print(f"\n  {label}")
        print(f"    Foster total {s['load']['total_bearing']:.4f} / expected "
              f"{s['load']['expected_total']:.1f}  conserved="
              f"{s['load']['conserved']}")
        print(f"    cut parts    {s['cut_parts']}")
        print(f"    R_eff first evidence -> conclusion: "
              f"{s['resistance_first_evidence_to_conclusion']}")
        print(f"    layer        {r['layer']}")

    s5, s6 = r5["structure"], r6["structure"]
    print(f"\nE1 5-part Foster 4.0 and one cut  -> "
          f"{hit(abs(s5['load']['total_bearing'] - 4.0) < 1e-9 and len(s5['cut_parts']) == 1)}")
    print(f"E2 6-part Foster 5.0 and two cuts -> "
          f"{hit(abs(s6['load']['total_bearing'] - 5.0) < 1e-9 and len(s6['cut_parts']) == 2)}")
    print(f"E3 6-part R_eff = 3.0             -> "
          f"{hit(abs(s6['resistance_first_evidence_to_conclusion'] - 3.0) < 1e-9)}")

    print("\n=== ARM 2 -- the seam that abstains ===")
    print(f"  semantic layer: {r6['semantic_layer']}")
    print(f"  energy carried: {r6['semantic_energy']}")
    print(f"E4/E5/E6 abstains, no number, line present -> "
          f"{hit(r6['semantic_energy'] is None and 'ABSTAIN' in r6['semantic_layer'])}")

    print("\n=== ARM 3 -- the firewall ===")
    print(f"  rule: {r6['layer_rule']}")
    print(f"  6-part kept out of Layer 1 by {len(r6['kept_out_of_layer_1_by'])} edge(s)")
    print(f"  provenance counts {r6['provenance_counts']}  "
          f"inferred ratio {r6['inferred_edge_ratio']:.4f} (gates nothing)")
    print(f"  all-literal toy -> {rt['layer']}")
    print(f"E8 both N182 drawings Layer 3 -> "
          f"{hit('Layer 3' in r5['layer'] and 'Layer 3' in r6['layer'])}")
    print(f"E9 all-literal toy Layer 1    -> {hit('Layer 1' in rt['layer'])}")

    print("\n=== ARM 4 -- padding attack, and the one declared fusion ===")
    b, a = cmp_["before"], cmp_["after"]
    print(f"  cut parts   {b['cut_parts']}  ->  {a['cut_parts']}")
    print(f"  Foster      {b['load']['total_bearing']:.4f}  ->  "
          f"{a['load']['total_bearing']:.4f}")
    print(f"  dependence  {b['deepest_dependence']:.6f}  ->  "
          f"{a['deepest_dependence']:.6f}")
    tw = cmp_["padding_tripwire"]
    print(f"  tripwire fired={tw['fired']}   ({tw['note']})")
    added = len(padded.edges) - len(six.edges)
    print(f"\nE11 padding clears every cut  -> {hit(len(a['cut_parts']) == 0)}")
    print(f"E12 at most 4 added edges     -> {hit(added <= 4)}  (added {added})")
    print(f"E13 Foster unchanged at 5.0   -> "
          f"{hit(abs(a['load']['total_bearing'] - 5.0) < 1e-9)}")
    print(f"E14 dependence RISES          -> "
          f"{hit(a['deepest_dependence'] > b['deepest_dependence'])}")

    out = {"prereg_sha256": PREREG_SHA, "locked_five_part": r5,
           "six_part": r6, "all_literal_toy": rt, "padding": cmp_,
           "added_edges": added}
    with open(os.path.join(HERE, "results_nere.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("\nwrote results_nere.json")
    return out


if __name__ == "__main__":
    main()
