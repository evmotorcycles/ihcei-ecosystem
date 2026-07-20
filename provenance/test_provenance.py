"""pytest: the cryptographic origin lock verifies, and tampering is detected."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import provenance_core as pc  # noqa: E402


def test_lock_exists_and_verifies():
    r = subprocess.run([sys.executable, os.path.join(HERE, "verify_provenance.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "VERIFIED" in r.stdout
    assert "originates from" in r.stdout


def test_locked_root_matches_recomputed():
    lock = json.load(open(os.path.join(ROOT, "PROVENANCE.lock.json")))
    _, _, root = pc.compute()
    assert root == lock["merkle_root"]
    assert lock["file_count"] == len(lock["leaves"]) >= 20


def test_results_json_are_not_fingerprinted():
    # provenance must exclude mutable, timestamped run outputs
    lock = json.load(open(os.path.join(ROOT, "PROVENANCE.lock.json")))
    assert not any("results" in p for p in lock["leaves"])


def test_merkle_is_tamper_evident():
    # flipping any single leaf must change the root (integrity property)
    _, leaves, root = pc.compute()
    hexes = list(leaves.values())
    tampered = hexes[:]
    tampered[0] = ("0" if tampered[0][0] != "0" else "1") + tampered[0][1:]
    assert pc.merkle_root(tampered) != root


def test_order_independence_of_content_only_via_sorted_paths():
    # the root is deterministic: recompute twice, identical
    _, _, r1 = pc.compute()
    _, _, r2 = pc.compute()
    assert r1 == r2
