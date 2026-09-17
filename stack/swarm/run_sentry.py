#!/usr/bin/env python3
"""Produce the Commit 5 numbers. Predictions were locked before this ran.

    python3 stack/swarm/run_sentry.py

Pre-registration: stack/swarm/prereg_sentry.md, sha256
9e45f3b272faff4389e1126e6c71034a955fd480a3e112eeed3702d18ec964df
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in (ROOT, os.path.join(ROOT, "lintel"), os.path.join(ROOT, "page-code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from lintel import cuts                                            # noqa: E402
from stack.swarm import fixtures                                   # noqa: E402
from stack.swarm.lism_sentry import (  # noqa: E402
    absolute_floor_trip_depth, sentry, trip_depth)

FLOOR = 0.6


def line(label, got, want):
    mark = "HIT " if got == want else "MISS"
    print(f"  {mark}  {label:<46} {got!s:<24} (predicted {want})")
    return got == want


def main():
    print(__doc__.strip().splitlines()[0])
    ok = []

    print("\nP10b -- the floor form, and only the floor form, depends on U")
    ds = [0.9] * 200
    ok.append(line("ratio floor, U = 1, trip depth", trip_depth(ds, FLOOR), 5))
    ok.append(line("ratio floor, U = 1000, trip depth",
                   trip_depth(ds, FLOOR), 5))
    ok.append(line("absolute floor, U = 1, trip depth",
                   absolute_floor_trip_depth(1.0, ds, FLOOR), 5))
    ok.append(line("absolute floor, U = 1000, trip depth",
                   absolute_floor_trip_depth(1000.0, ds, FLOOR), 71))

    print("\nP11 -- the two padding forms move in OPPOSITE directions")
    plain = sentry(1.0, *fixtures.chain(6), "a0", "a5", FLOOR)
    sub = sentry(1.0, *fixtures.subdivided_chain(6, hop=2), "a0", "a5", FLOOR)
    byp = sentry(1.0, *fixtures.bypass_chain(6, 1, 4), "a0", "a5", FLOOR)
    ok.append(line("unpadded chain, ratio_best",
                   round(plain["ratio_best"], 6), 0.59049))
    ok.append(line("subdivision padding, ratio_best",
                   round(sub["ratio_best"], 6), 0.531441))
    ok.append(line("subdivision padding, trips_best", sub["trips_best"], True))
    ok.append(line("bypass padding, ratio_best",
                   round(byp["ratio_best"], 6), 0.729))
    ok.append(line("bypass padding, trips_best  <- DEFEAT",
                   byp["trips_best"], False))
    ok.append(line("bypass padding, trips_worst <- survives",
                   byp["trips_worst"], True))

    print("\nP12 -- the OR-gate is earned: each sensor misses a fixture")
    sp, sl, sr = fixtures.star(4)
    rp, rl, rr = fixtures.ring(12)
    s = sentry(1.0, sp, sl, sr, "leaf0", "leaf1", FLOOR)
    g = sentry(1.0, rp, rl, rr, "a0", "a6", FLOOR)
    ok.append(line("star: cut vertices", len(cuts(sp, sl)), 1))
    ok.append(line("star: fidelity trips", s["trips_best"], False))
    ok.append(line("ring: cut vertices", len(cuts(rp, rl)), 0))
    ok.append(line("ring: ratio_best", round(g["ratio_best"], 6), 0.531441))
    ok.append(line("ring: fidelity trips", g["trips_best"], True))

    print(f"\n{sum(ok)}/{len(ok)} predictions hit.")
    print("\nSCOPE:", plain["scope"])
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
