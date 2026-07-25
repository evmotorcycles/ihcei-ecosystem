#!/usr/bin/env python3
"""
verify_colab.py -- verify a Colab run against the pre-registered lock.
================================================================================
Two ways to use it:

  # 1. Just paste the RESULTS_SHA256 line the Colab notebook printed:
  python3 colab-tests/verify_colab.py aebdd9b7723bf6c516283ebed15112f0227109ada7cb2e0bf9ced86464b56e51

  # 2. Or paste the whole RESULTS_JSON to see which field diverged (if any):
  python3 colab-tests/verify_colab.py '{"T1_lmd_ring":{...}, ...}'

A hash equal to expected_results_sha256 = INDEPENDENT REPRODUCTION CONFIRMED.
A mismatch prints exactly which test/field differs from the locked expectation.
"""
import json
import os
import sys
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "prereg", "colab_prereg.json")


def main():
    spec = json.load(open(SPEC))
    expected_hash = spec["expected_results_sha256"]
    expected = spec["expected_results"]

    if len(sys.argv) < 2:
        print("usage: verify_colab.py <RESULTS_SHA256 | RESULTS_JSON>")
        print("expected_results_sha256 =", expected_hash)
        raise SystemExit(2)

    arg = sys.argv[1].strip()
    bar = "=" * 74
    print(bar)
    print(" COLAB REPRODUCTION VERIFICATION")
    print(bar)
    print(" locked expected hash : %s" % expected_hash)

    # case 1: a bare hash
    if all(c in "0123456789abcdef" for c in arg.lower()) and len(arg) == 64:
        ok = arg.lower() == expected_hash
        print(" returned hash        : %s" % arg.lower())
        print("\n %s" % ("VERIFIED — independent reproduction confirmed (hashes match)." if ok
                          else "MISMATCH — the returned hash does NOT equal the lock. Re-run and paste RESULTS_JSON to localise."))
        print(bar)
        raise SystemExit(0 if ok else 1)

    # case 2: full JSON -> field-by-field
    try:
        got = json.loads(arg)
    except Exception as e:
        print(" could not parse argument as a hash or JSON:", e)
        raise SystemExit(2)
    got_hash = hashlib.sha256(json.dumps(got, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(" returned hash        : %s" % got_hash)
    diffs = []
    for test, exp in expected.items():
        g = got.get(test)
        if g != exp:
            diffs.append((test, exp, g))
    if not diffs and got_hash == expected_hash:
        print("\n VERIFIED — every field matches the pre-registered expectation.")
        print(bar)
        raise SystemExit(0)
    print("\n MISMATCH — diverging tests:")
    for test, exp, g in diffs:
        print("   %-16s expected %s" % (test, json.dumps(exp)))
        print("   %-16s got      %s" % ("", json.dumps(g)))
    print("\n (A stable field diverging suggests a real code change or a broken environment;")
    print("  report it honestly — do not adjust the lock to match a bad run.)")
    print(bar)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
