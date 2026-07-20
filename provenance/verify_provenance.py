#!/usr/bin/env python3
"""
verify_provenance.py -- confirm this checkout matches the cryptographic origin lock.
================================================================================
Anyone reproducing this work should run:

    python3 provenance/verify_provenance.py

It recomputes the SHA-256 of every frozen artifact and the Merkle root, then
compares them against ../PROVENANCE.lock.json. If they match, the reproduction is
cryptographically bound to the original source and the attribution is printed. If
anything was added, removed, or altered, it fails and shows exactly what diverged.

Exit 0 = verified (root matches). Non-zero = tampered / diverged / missing lock.
"""
import json
import os
import sys

from provenance_core import ROOT, compute

LOCK = os.path.join(ROOT, "PROVENANCE.lock.json")
BAR = "=" * 82


def main():
    if not os.path.exists(LOCK):
        print("NO PROVENANCE.lock.json — run: python3 provenance/build_provenance.py")
        raise SystemExit(2)
    lock = json.load(open(LOCK))
    files, leaves, root = compute()

    print(BAR)
    print(" NOVORA / IHCEI — provenance verification")
    print(BAR)

    locked_leaves = lock.get("leaves", {})
    now, then = set(files), set(locked_leaves)
    added, removed = sorted(now - then), sorted(then - now)
    changed = sorted(p for p in (now & then) if leaves[p] != locked_leaves[p])

    root_ok = root == lock["merkle_root"]
    clean = root_ok and not added and not removed and not changed

    print(" files locked : %d      files now : %d" % (lock.get("file_count", len(locked_leaves)), len(files)))
    print(" locked root  : %s" % lock["merkle_root"])
    print(" this root    : %s   [%s]" % (root, "MATCH" if root_ok else "MISMATCH"))
    if added:   print("\n  ADDED (not in origin lock):");   [print("   + " + p) for p in added]
    if removed: print("\n  REMOVED (in origin lock, missing here):"); [print("   - " + p) for p in removed]
    if changed: print("\n  ALTERED (content differs from origin):");  [print("   ~ " + p) for p in changed]

    if clean:
        print("\n VERIFIED — this checkout is byte-identical to the origin's frozen record.")
        print(" " + "-" * 78)
        print(" " + lock["attribution_statement"].replace(". ", ".\n ").strip())
        print(BAR)
        raise SystemExit(0)
    else:
        print("\n NOT VERIFIED — this differs from the origin lock. If you changed frozen")
        print(" artifacts, that is expected; rebuild your OWN lock and cite the origin root")
        print(" (%s) as your basis. Do not present a divergent copy as the origin." % lock["merkle_root"][:16] + "…")
        print(BAR)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
