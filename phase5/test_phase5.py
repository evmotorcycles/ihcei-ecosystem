"""The Phase 5 bundle must stay UNLOCKED, and must stay complete.

Two failure modes, one test file. The bundle is worthless if it quietly gets
locked (a pre-registration that can never be scored), and equally worthless if
a door's section loses the feasibility gate or the acceptance criteria and
becomes a wish list.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SPEC = os.path.join(HERE, "runner_spec.md")


def _text():
    return " ".join(open(SPEC, encoding="utf-8").read().split())


def test_the_bundle_exists_and_declares_itself_unlocked():
    t = _text()
    assert "STATUS: UNLOCKED" in t
    assert "requires a networked runner" in t
    assert "nothing in this repository asserts its hash" in t


def test_no_test_in_this_repository_asserts_this_file_s_hash():
    """The guard against quiet locking.

    Computed here and searched for, rather than pinned: pinning the digest
    would itself be the locking this test exists to prevent. A rename of the
    file would slip past this, which is why the check is scoped to what it can
    see and the ledger carries the rule in words as well.
    """
    digest = hashlib.sha256(open(SPEC, "rb").read()).hexdigest()
    hits = []
    for dirpath, dirnames, files in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in ("__pycache__", ".git", "node_modules")]
        for f in files:
            if not f.endswith((".py", ".md", ".sh")):
                continue
            p = os.path.join(dirpath, f)
            if os.path.abspath(p) == os.path.abspath(SPEC):
                continue
            with open(p, encoding="utf-8", errors="replace") as fh:
                if digest in fh.read():
                    hits.append(p)
    assert hits == [], f"the unlocked bundle has been locked in {hits}"


def test_each_door_carries_all_four_required_parts():
    t = _text()
    for door in ("DOOR 1 — trained attention", "DOOR 2 — per-hop swarm payloads"):
        assert door in t, door
    for part in ("1. Feasibility gate", "2. Pre-registration text",
                 "3. Data and provenance requirements",
                 "4. Acceptance criteria"):
        # each part appears once per door
        assert _text().count(part) >= 2, part


def test_every_prediction_is_written_out_and_marked_unlocked():
    t = _text()
    for pid in ("P21", "P22", "P23", "P24", "P25", "P26"):
        assert re.search(rf"### {pid} — \S", t), f"{pid} has no written text"
        assert f"{pid}," in t or f"{pid} —" in t
    assert t.count("(UNLOCKED, requires networked runner)") == 2


def test_every_prediction_states_what_would_falsify_it():
    body = open(SPEC, encoding="utf-8").read()
    sections = re.split(r"\n### (P2[1-6]) — ", body)[1:]
    pairs = list(zip(sections[0::2], sections[1::2]))
    assert len(pairs) == 6, [p[0] for p in pairs]
    for pid, chunk in pairs:
        assert "Falsified by:" in chunk, pid


def test_the_door_two_predictions_live_here_and_nowhere_else():
    """Asserted by ROLE: every `prereg_*.md` in the repository, not one path."""
    for dirpath, dirnames, files in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in ("__pycache__", ".git", "node_modules")]
        for f in files:
            if not (f.startswith("prereg_") and f.endswith(".md")):
                continue
            text = open(os.path.join(dirpath, f), encoding="utf-8").read()
            for pid in ("P24", "P25", "P26"):
                assert not re.search(rf"{pid}\s*[-—:]\s*\S", text), (f, pid)


def test_the_threshold_in_p23_carries_a_reason_and_a_sensor():
    """CLAUDE.md: every number that gates a decision needs both."""
    t = _text()
    assert "Why `1e-6`:" in t
    assert "float32 machine epsilon" in t
    assert "The sensor is the eight-way sweep itself." in t


def test_the_horizon_rule_is_carried_into_the_bundle():
    t = _text()
    assert "one probe past that range, reported whichever way it falls" in t
    assert "a second model of different depth" in t


def test_the_bundle_refuses_untrained_weights_as_a_substitute():
    t = _text()
    assert "Do not substitute randomly-initialised weights" in t
    assert "synthetic fixture with a misleading provenance" in t


def test_the_standing_instruction_is_present_in_both_status_files_and_here():
    t = _text()
    assert "A network limitation must not harden into a finding." in t
    for name in ("DOOR1_STATUS.md", "DOOR2_STATUS.md"):
        s = " ".join(open(os.path.join(ROOT, "stack", "swarm", name),
                          encoding="utf-8").read().split())
        assert "egress" in s
        assert "not on inspection" in s or "not on inspection of the primary" in s


def test_the_ledger_records_the_human_check_as_open():
    led = " ".join(open(os.path.join(ROOT, "stack", "governance",
                                     "declarations.md"),
                        encoding="utf-8").read().split())
    assert "The human check — status OPEN" in led
    assert "Status: OPEN" in led
    assert "phase5/runner_spec.md" in led
