"""Patch 2, organization. Locked in prereg_organization.md, sha256
e2c7b6567ae0b05111bf0f5332632d42f4d8f34c23975937dc48aa70b1a92e3c

Three defects in the draft are kept as evidence: R1 (the drafted score was not a
rename), R2 (kappa differed), R3 (dissonance leaked the label).
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from stack.organization.adg_cfe import (  # noqa: E402
    LABEL_ALIGNED, LABEL_HIGH_DISSONANCE, LABEL_MISALIGNED, PROBE_MARK, Cohort,
    adg_score, cfe_render, cosine_to_ones, minmax)

PREREG_SHA = "e2c7b6567ae0b05111bf0f5332632d42f4d8f34c23975937dc48aa70b1a92e3c"
COHORT_SHA = "020562667229a1c24e06b1a075786c2f86d700e5fbf1a4c0bb99a905b95f7a15"
FIXTURE = os.path.join(ROOT, "adg-tqg", "fixtures", "experiment_cohort.json")
EPS = 0.05


@pytest.fixture(scope="module")
def cohort():
    return Cohort(json.load(open(FIXTURE))["repos"], FIXTURE)


def _original():
    """adg-tqg/experiment.py lines 55-86, transcribed. The pre-rename truth."""
    repos = json.load(open(FIXTURE))["repos"]
    a = minmax([math.log1p(r["stargazers"]) for r in repos])
    t = minmax([math.log1p(r["n_closed"]) for r in repos])
    rsp = minmax([1.0 / (1.0 + r["tau_v"]) for r in repos])
    hbar = minmax([r["tau_v"] for r in repos])
    A_n, C_dev = [], []
    for i in range(len(repos)):
        an = cosine_to_ones((a[i], t[i], rsp[i]))
        A_n.append(an)
        C_dev.append(an * (a[i] * t[i]) / (0.05 + hbar[i]))
    return A_n, C_dev


# ----------------------------------------------------------- the ledger ----
def test_the_preregistration_is_the_one_that_was_hashed():
    with open(os.path.join(HERE, "prereg_organization.md"), "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == PREREG_SHA


def test_the_cohort_hash_is_recomputed_from_bytes_not_typed(cohort):
    assert cohort.hash == COHORT_SHA
    with open(FIXTURE, "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == cohort.hash


def test_p13_b_a_typed_cohort_hash_cannot_enter():
    """The constructor takes a PATH, never a hash string."""
    import inspect
    sig = inspect.signature(Cohort.__init__)
    assert "fixture_path" in sig.parameters
    assert not any("hash" in p for p in sig.parameters)


# --------------------------------------- R4/R5: the rename is faithful ----
def test_r4_the_rename_is_bit_identical_to_the_pre_rename_arithmetic(cohort):
    A_n, C_dev = _original()
    for i in range(len(cohort.records)):
        assert abs(cohort.alignment(i) - A_n[i]) < 1e-12, i
        assert abs(adg_score(cohort, i, EPS)["value"] - C_dev[i]) < 1e-12, i


def test_r5_kappa_is_the_upper_middle_value_not_a_mean_of_two(cohort):
    A_n, _ = _original()
    assert cohort.kappa == sorted(A_n)[len(A_n) // 2]
    mean_of_middle = (sorted(A_n)[10] + sorted(A_n)[11]) / 2.0
    assert abs(cohort.kappa - mean_of_middle) > 1e-6     # they really differ


def test_the_drafted_score_was_not_a_rename(cohort):
    """R1, kept as evidence.

    The draft computed utility*(d_enc*d_dec)/(eps+noise), dropping the alignment
    factor and putting utility in its place. Different function, different rank
    order. A bit-identical regression would have failed.
    """
    _, C_dev = _original()
    drafted = [cohort.utility[i] * (cohort.d_enc[i] * cohort.d_dec[i])
               / (EPS + cohort.noise[i]) for i in range(len(cohort.records))]
    assert max(abs(c - d) for c, d in zip(C_dev, drafted)) > 1.0
    order_orig = sorted(range(len(C_dev)), key=lambda i: C_dev[i])
    order_draft = sorted(range(len(drafted)), key=lambda i: drafted[i])
    assert order_orig != order_draft


# ---------------------------------------------- P13: cohort relativity ----
def test_p13_a_dropping_one_record_shifts_the_ranks(cohort):
    records = cohort.records
    base = sorted(range(len(records)),
                  key=lambda i: adg_score(cohort, i, EPS)["value"])
    shifted = 0
    for drop in range(len(records)):
        sub = Cohort([r for j, r in enumerate(records) if j != drop], FIXTURE)
        order = sorted(range(len(sub.records)),
                       key=lambda i: adg_score(sub, i, EPS)["value"])
        names = [sub.records[i]["repo"] for i in order]
        expected = [records[i]["repo"] for i in base
                    if records[i]["repo"] != records[drop]["repo"]]
        if names != expected:
            shifted += 1
    assert shifted >= 1, "no single drop moved any rank; the cohort is not relative"


def test_every_emitted_reading_carries_the_hash_and_says_it_is_relative(cohort):
    for i in (0, 5, 21):
        s, r = adg_score(cohort, i, EPS), cfe_render(cohort, i)
        assert s["cohort_hash"] == cohort.hash and s["cohort_relative"] is True
        assert r["cohort_hash"] == cohort.hash and r["cohort_relative"] is True


def test_eps_has_no_default(cohort):
    with pytest.raises(TypeError):
        adg_score(cohort, 0)          # type: ignore[call-arg]


# --------------------------------------------- P14: the permutation null ----
def _separation(values, labels):
    s = [v for v, e in zip(values, labels) if e == 1]
    f = [v for v, e in zip(values, labels) if e == 0]
    return sum(s) / len(s) - sum(f) / len(f)


def _exact_permutation_p(values, labels):
    """One-tailed, EXACT: every relabelling with the same class sizes.

    C(22,6) = 74613, small enough to enumerate in full. A first version capped
    this with itertools.islice, which takes combinations in LEXICOGRAPHIC order
    -- overwhelmingly low indices -- so it was a biased subset, not a null. That
    was a defect in the method, not in the data.
    """
    n, k = len(labels), sum(1 for e in labels if e == 0)
    observed = _separation(values, labels)
    hits = total = 0
    for combo in itertools.combinations(range(n), k):
        lab = [1] * n
        for c in combo:
            lab[c] = 0
        if _separation(values, lab) >= observed:
            hits += 1
        total += 1
    return (hits + 1) / (total + 1), total


def test_the_first_prediction_that_missed(cohort):
    """P14-a. The leaky score separates, but not at p < 0.01 as predicted.

    Exact p = 0.025679 over all 74613 relabellings. Leakage makes the separation
    easier to find (P14-c holds) without making it overwhelming: the label rule
    is a THRESHOLD on days_since_push, and the leaky dissonance is a continuous
    z-gap, so it restates the label loosely rather than exactly.
    """
    labels = [r["E"] for r in cohort.records]
    leaky = cohort.leaky_dissonance()
    scores = [cohort.alignment(i) * (cohort.utility[i] * cohort.d_dec[i])
              / (EPS + leaky[i]) for i in range(len(cohort.records))]
    p, _ = _exact_permutation_p(scores, labels)
    assert p >= 0.01, "the prediction was p < 0.01; record the miss, do not soften it"
    assert p < 0.05


def test_p14_b_the_clean_score_separates_too(cohort):
    """The one the pre-registration flagged as uncertain: 6 failures, 16 survivors."""
    labels = [r["E"] for r in cohort.records]
    scores = [adg_score(cohort, i, EPS)["value"]
              for i in range(len(cohort.records))]
    p, total = _exact_permutation_p(scores, labels)
    assert total == 74613, "the null must be the exact enumeration, not a subset"
    assert p < 0.05, p
    assert p > 0.04, "it clears 0.05 by 0.005; this is thin and should read as thin"


def test_p14_c_the_leaky_p_is_smaller_and_the_gap_is_the_leakage(cohort):
    labels = [r["E"] for r in cohort.records]
    leaky = cohort.leaky_dissonance()
    leaky_scores = [cohort.alignment(i) * (cohort.utility[i] * cohort.d_dec[i])
                    / (EPS + leaky[i]) for i in range(len(cohort.records))]
    clean = [adg_score(cohort, i, EPS)["value"] for i in range(len(cohort.records))]
    p_leaky, _ = _exact_permutation_p(leaky_scores, labels)
    p_clean, _ = _exact_permutation_p(clean, labels)
    assert p_leaky < p_clean


def test_r3_the_shipped_dissonance_carries_no_push_input(cohort):
    """The leakage the draft would have introduced, kept out.

    Perturbing only days_since_push must not move the shipped dissonance, and
    must move the leaky one.
    """
    # a CONSTANT shift would prove nothing: a z-score is affine-invariant, so
    # +500 leaves both dissonances untouched. The first version of this test did
    # exactly that and looked like a failure of the module.
    bumped = [dict(r) for r in cohort.records]
    for r in bumped:
        r["days_since_push"] = r["days_since_push"] ** 2
    other = Cohort(bumped, FIXTURE)
    assert cohort.dissonance == pytest.approx(other.dissonance)
    assert cohort.leaky_dissonance() != pytest.approx(other.leaky_dissonance())


# ------------------------------------------------------------ P15: probes ----
def _probe(name, stars, closed, tau_v, days):
    return {"repo": name, "stargazers": stars, "n_closed": closed,
            "tau_v": tau_v, "pushed_at": "2026-07-17", "archived": False,
            "days_since_push": days, "E": 1}


def test_p15_a_a_zombie_renders_high_dissonance(cohort):
    """Fresh push, very slow enforcement, heavily adopted: a wide say-do gap."""
    c = cohort.with_probe(_probe("probe/zombie", 200000, 3, 250.0, 1), FIXTURE)
    assert cfe_render(c, len(c.records) - 1)["label"] == LABEL_HIGH_DISSONANCE


def test_the_second_prediction_that_missed(cohort):
    """P15-b. The healthy probe renders high_dissonance, not aligned.

    Its alignment is 0.9709, well above kappa 0.8612 -- so on alignment alone it
    IS aligned. But dissonance is |z(adoption) - z(responsiveness)| and the
    absolute value makes it TWO-SIDED: a project far better at "do" than at
    "say" scores exactly like one far better at "say" than at "do". The probe
    has tau_v = 1.2 against a cohort ranging to 251, so its responsiveness
    z-score is extreme and the gap reads 1.5398 against a bound of 0.8822.

    A one-sided gap would separate the two conditions. That is a change to a
    locked specification and is NOT made here: the miss is recorded and the
    decision is the reader's.
    """
    c = cohort.with_probe(_probe("probe/healthy", 50000, 200, 1.2, 2), FIXTURE)
    i = len(c.records) - 1
    assert cfe_render(c, i)["label"] == LABEL_HIGH_DISSONANCE
    assert c.alignment(i) > c.kappa          # aligned on alignment alone
    assert c.dissonance[i] > c.quartile_bound


def test_p15_c_a_probe_changes_the_cohort_hash(cohort):
    c = cohort.with_probe(_probe("probe/any", 100, 10, 5.0, 10), FIXTURE)
    assert c.hash != cohort.hash
    assert PROBE_MARK in c.hash
    assert c.hash.startswith(COHORT_SHA)


def test_the_archived_but_responsive_false_positive_class_is_named():
    """A record can be archived and still look responsive. Named, not hidden."""
    prereg = " ".join(open(os.path.join(HERE, "prereg_organization.md"),
                           encoding="utf-8").read().split())
    assert "synthetic" in prereg
    assert "not evidence that such repositories exist" in prereg


# ------------------------------------------------- A1: the vocabulary rule ----
def test_the_tradition_vocabulary_is_absent_from_the_whole_stack():
    """A1. Word boundaries, per the lexical-detector rule in the ledger.

    Bare substrings would be wrong here twice over: "usr" occurs inside any
    /usr/ path, and "hbar" is not tradition vocabulary at all -- it is the
    physics notation the ORIGINAL code used for its noise term. That one gets
    its own check below, scoped to shipped code so the pre-registration can
    still document the mapping it replaced.
    """
    words = ["sal" + "at", "zak" + "at", "shi" + "rk", "yu" + "sr", "us" + "r"]
    # `\b` is NOT enough: a slash is a word boundary, so \busr\b fires inside
    # "/usr/local". The named decoy below caught that before it shipped, which
    # is what a named decoy is for. Path separators and hyphens are excluded on
    # both sides.
    pattern = re.compile(r"(?<![/\w-])(" + "|".join(words) + r")(?![/\w-])")
    must_not_fire = "the /usr/local path, usr/bin, and the word usher"
    must_fire = "a bare " + "us" + "r token on its own"
    assert not pattern.search(must_not_fire), "decoy fired; the check is too loose"
    assert pattern.search(must_fire), "the check is too tight to catch anything"

    root = os.path.join(ROOT, "stack")
    seen = 0
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith((".py", ".md")) or f.startswith("test_"):
                continue
            path = os.path.join(dirpath, f)
            seen += 1
            hit = pattern.search(open(path, encoding="utf-8").read().lower())
            assert not hit, f"{path} contains {hit.group(0) if hit else ''}"
    assert seen >= 3


def test_physics_notation_stays_out_of_shipped_organization_code():
    """Separate rule, separate scope.

    `hbar` is the reduced Planck constant; carrying it into Layer-1 cohort
    telemetry is the same category error as calling the fidelity product
    thermodynamics. Scoped to .py so the pre-registration can quote the
    original's variable names while documenting what replaced them.
    """
    root = os.path.join(ROOT, "stack")
    pattern = re.compile(r"\bhba" + r"r\b")
    seen = 0
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".py") or f.startswith("test_"):
                continue
            seen += 1
            text = open(os.path.join(dirpath, f), encoding="utf-8").read().lower()
            assert not pattern.search(text), f"{dirpath}/{f}"
    assert seen >= 2


def test_the_adapter_holds_the_mapping_and_computes_nothing():
    sys.path.insert(0, ROOT)
    from ncu.adapter import DISPLAY, PARAMETER_HERITAGE, display_label
    assert set(DISPLAY) == {LABEL_ALIGNED, LABEL_MISALIGNED, LABEL_HIGH_DISSONANCE}
    assert display_label(LABEL_ALIGNED) and display_label(LABEL_HIGH_DISSONANCE)
    assert set(PARAMETER_HERITAGE) == {"utility", "d_enc", "d_dec", "noise",
                                       "dissonance"}
    with pytest.raises(KeyError):
        display_label("not_a_measured_label")


def test_the_label_conflict_is_recorded_rather_than_resolved_silently():
    prereg = " ".join(open(os.path.join(HERE, "prereg_organization.md"),
                           encoding="utf-8").read().split())
    assert "The two halves of the instruction conflict" in prereg
    assert "One constant to change if the other was meant" in prereg


def test_the_module_states_what_the_numbers_are_not():
    from stack.organization import adg_cfe
    doc = " ".join(adg_cfe.__doc__.split())
    assert "NOT a property of a repository" in doc
    assert "NOT causal" in doc
    assert "NOT a health grade" in doc
    assert "a function of the label" in doc
