"""pytest: the cryptographic origin lock verifies, and tampering is detected."""
import json
import re
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


# ---------------------------------------------------------------------------
# The supersession chain.
#
# A lock that can never be re-issued after a correction penalises honesty: the
# H5 retirement was a TRUE statement replacing a false one, and it turned the
# provenance test red. A lock that can be re-rooted whenever a test goes red
# attests to nothing. The builder takes the third option -- it refuses to move
# the root unless the root being retired is declared, with a reason, in source.
#
# These four tests are what make that a mechanism rather than a comment. The
# first two are the required two-sided decoy: one case the refusal MUST fire
# on, one it must NOT.
# ---------------------------------------------------------------------------
import build_provenance as bp  # noqa: E402


def _lock_with_root(tmpdir, root):
    p = os.path.join(tmpdir, "lock.json")
    json.dump({"merkle_root": root}, open(p, "w"))
    return p


def test_an_undeclared_re_root_is_refused(tmp_path, monkeypatch):
    """MUST fire. This is the whole point: a frozen artifact changed and
    nobody said why, so the builder will not write a new root over it."""
    monkeypatch.setattr(bp, "OUT", _lock_with_root(str(tmp_path), "de" * 32))
    try:
        bp.check_supersession("ad" * 32)
    except bp.UndeclaredResubmission as e:
        assert "SUPERSESSIONS" in str(e)
        assert "attests to nothing" in str(e)
    else:
        raise AssertionError("a silent re-root was allowed")


def test_a_declared_supersession_is_accepted(tmp_path, monkeypatch):
    """MUST NOT fire -- the control that makes the refusal meaningful. Without
    this the previous test would also pass if the builder refused everything."""
    declared = bp.SUPERSESSIONS[-1]["root"]
    monkeypatch.setattr(bp, "OUT", _lock_with_root(str(tmp_path), declared))
    supersedes, chain = bp.check_supersession("ad" * 32)
    assert supersedes == declared
    assert chain and all(e.get("reason") for e in chain)


def test_every_retired_root_carries_a_reason_and_a_date():
    """A chain entry without a reason is a re-root wearing a chain's clothes."""
    assert bp.SUPERSESSIONS, "the chain is empty; nothing records the H5 re-issue"
    for e in bp.SUPERSESSIONS:
        assert len(e["root"]) == 64, e
        assert len(e["reason"]) > 60, "a one-word reason is not a reason"
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["superseded_on"]), e


def test_the_shipped_chain_came_from_the_builder_not_a_hand_edit():
    """If the chain were typed into the JSON, the next rebuild would silently
    erase it and nothing would notice. Pinning the file to the source constant
    is what makes that impossible."""
    lock = json.load(open(os.path.join(ROOT, "PROVENANCE.lock.json")))
    assert lock["supersession_chain"] == bp.SUPERSESSIONS
    assert lock["supersedes"] == bp.SUPERSESSIONS[-1]["root"]
    assert lock["merkle_root"] != lock["supersedes"], "superseded by itself"


def test_attribution_did_not_move_across_the_supersession():
    """Only the snapshot moved. If author, affiliation or origin could travel
    with a re-issue, the chain would be a way to launder authorship."""
    lock = json.load(open(os.path.join(ROOT, "PROVENANCE.lock.json")))
    assert lock["author"] == bp.AUTHOR
    assert lock["affiliation"] == bp.AFFIL
    assert lock["origin"] == bp.ORIGIN
