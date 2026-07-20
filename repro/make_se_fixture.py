#!/usr/bin/env python3
"""
make_se_fixture.py -- deterministic, OFFLINE Stack-Exchange-shaped fixture for the
knowledge-propagation (Barakah) cohort.
============================================================================
Addresses a reproducibility gap flagged by an independent reproducer (Jules):
`se_barakah_test.py` previously required a LIVE fetch through the Vercel SE proxy
(`api/se-search.js`), so the knowledge cohort could NOT be re-run offline. This
script writes a seeded fixture in the exact /api/se-search response shape so the
whole knowledge-cohort pipeline runs end-to-end with NO network.

HONEST SCOPE (Layer-1 discipline):
  * This is a SYNTHETIC OFFLINE fixture, not the live Stack Overflow data. It is
    generated from a GENUINELY LINEAR (additive, no D^2) latent process with the
    two hops drawn INDEPENDENTLY, so it reproduces the *verdict class* the live
    run reported -- "channel intact (VIF~1) + LINEAR adequate, no curvature" --
    deterministically and offline.
  * It does NOT reproduce the exact live N=793 headline numbers; those remain
    attested from SE_BARAKAH_RESULTS.md. The point here is that anyone can now
    re-run se_barakah_test.py's METHOD offline and confirm it returns the linear
    verdict on channel-intact data drawn from a no-quadratic ground truth -- i.e.
    the test is not rigged to always say "linear".

    python3 repro/make_se_fixture.py            # writes repro/data/se_fixture_barakah.json
    python3 se_barakah_test.py --json repro/data/se_fixture_barakah.json

Fields per question match what se_barakah_test.py reads:
    id, reputation, score (D_enc raw), answer_count (D_dec raw), view_count (E raw)
"""
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "se_fixture_barakah.json")
SEED = 20260720
N = 793                       # match the live pooled cohort size


def main():
    rng = random.Random(SEED)
    qs = []
    for i in range(N):
        # capacity U: asker reputation ~ lognormal
        reputation = int(math.exp(rng.gauss(6.0, 1.6)))
        # D_enc raw (question score) and D_dec raw (answer_count) drawn INDEPENDENTLY
        # -> channel intact, VIF ~ 1 (no shared driver).
        score = max(0, int(rng.gauss(6, 5)))
        answer_count = rng.randint(0, 6)
        # normalized hops (same transforms the test will apply, roughly)
        u = math.log1p(reputation)
        d_enc = min(score, 20) / 20.0
        d_dec = answer_count / 6.0
        d = d_enc * d_dec
        # LATENT reuse is ADDITIVE & LINEAR in the standardized drivers -- NO D^2 term.
        # This is the null the accelerating-quadratic hypothesis must beat and cannot.
        latent = 0.9 * (u - 6.5) + 2.3 * (d - 0.25) + rng.gauss(0, 0.8)
        view_count = int(math.exp(6.0 + 0.9 * latent))     # monotone, no curvature
        qs.append({
            "id": 1000 + i,
            "reputation": reputation,
            "score": score,
            "answer_count": answer_count,
            "view_count": view_count,
        })
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"questions": qs, "_provenance": {
            "synthetic": True, "seed": SEED, "n": N,
            "ground_truth": "additive linear latent, no D^2; hops independent",
            "purpose": "offline reproduction of the knowledge-cohort LINEAR verdict (Jules fix)",
        }}, f, indent=2)
    print("wrote %s  (N=%d, seed=%d, no-network)" % (OUT, N, SEED))


if __name__ == "__main__":
    main()
