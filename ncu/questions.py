#!/usr/bin/env python3
"""questions.py -- the five governance questions, and what may be said about each.

    python3 ncu/questions.py

WHY THIS FILE EXISTS
plumb/GOVERNANCE_VS_RT.md answers three of five and says so plainly. But it names
the other two only as "Q2 and Q5", and NEVER STATES WHAT THEY ARE. A boundary you
have not written down is not a boundary; it is a gap with a label on it. All five
are stated here.

THE DISTINCTION THIS FILE TURNS ON
Software never ANSWERS any of the five. It can only CHECK an obligation:

    operational check   an executable test that a duty was discharged.
                        Fails loudly. Says nothing about whether the duty was
                        the right one.
    substantive answer  what the question actually asks. Relational, not causal:
                        for-what, for-whom, against-what, who-discloses.
                        No measurement returns one, on any dataset, ever.

The first is engineering. The second travels only as a schema -- a figure that
installs a way of seeing, carrying no evidential weight. Confusing the two in
either direction is the whole failure mode this repository is built against:
mistaking a passed check for an answer, or demanding measurement of a schema.

WHAT CHANGED
Three of the five had an operational check (Q1, Q3, Q4). Two more now do:

    Q2  SPAR's conserved total is exactly parts - pieces, so a structure that
        has come apart says so in arithmetic nobody had to ask for.
    Q5  SMI measures what its own projection destroyed and prints it.

That is a real advance and it is NOT an advance from three answers to five. It
is an advance from three checks to five. The count of answers is still zero, and
this file will keep saying so.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

STAMP = "PROVES: NOTHING"
ANSWERS = "SUBSTANTIVE ANSWERS FROM MEASUREMENT: 0 of 5"


def _read(rel, path):
    """Pull one field out of a results file. Fails loudly if it is not there."""
    data = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
    cur = data
    for key in path.split("."):
        cur = cur[int(key)] if isinstance(cur, list) else cur[key]
    return cur


@dataclass(frozen=True)
class Check:
    """An executable test that a duty was discharged. Not an answer."""
    module: str
    checks: str
    source: str
    field: str
    value: object
    does_not_supply: str


@dataclass(frozen=True)
class Figure:
    """A schema. Carries the question's meaning; carries no evidence."""
    figure: str
    drawn_from: str
    schema: str
    proves: str = STAMP


@dataclass(frozen=True)
class Question:
    n: int
    name: str
    asks: str
    why_no_measurement_answers_it: str
    check: object            # Check, or None where nothing executable exists
    figures: list = field(default_factory=list)
    newly_checked: bool = False

    def as_dict(self):
        d = asdict(self)
        for f in d["figures"]:
            assert f["proves"] == STAMP, "the stamp is not editable"
        return d


def build():
    return [
        Question(
            n=1,
            name="Purpose",
            asks="What is this system for, such that we could tell if it had failed?",
            why_no_measurement_answers_it=(
                "A correct program optimises whatever objective it was given. "
                "Correctness is silent on whether that objective was worth "
                "pursuing, and no amount of further measurement makes it speak."),
            check=Check(
                module="plumb",
                checks="E = capacity x encode x decode. The terms MULTIPLY, so "
                       "reach with a broken channel scores zero. Arithmetic, not "
                       "a mission statement, so a stranger can check it.",
                source="lism-cohorts/results_meta.json",
                field="cohorts.D_swarm.meanD_last",
                value=_read("lism-cohorts/results_meta.json", "cohorts.D_swarm.meanD_last"),
                does_not_supply="whether the objective is worth pursuing at all"),
            figures=[Figure(
                figure="Speaking through a wall and being heard through a wall. "
                       "Neither wall has to be thick; two thin ones multiply.",
                drawn_from="LISM E = U*D, mean D falling 0.838 -> 0.014 over 39 hops",
                schema="A purpose has two sides that compound. Saying it well does "
                       "not survive being received badly, and capacity is not "
                       "achievement.")]),

        Question(
            n=2,
            name="Scope",
            asks="What else does this system govern, that I cannot see from where "
                 "I am standing?",
            why_no_measurement_answers_it=(
                "A program can enumerate what is in its scope. It cannot "
                "enumerate what is outside it, because the thing doing the "
                "enumerating is inside. Every survey of the boundary is taken "
                "from within the boundary."),
            check=Check(
                module="spar",
                checks="The conserved total is exactly parts - pieces (Foster's "
                       "theorem). So a structure that has come apart reports the "
                       "break in arithmetic nobody had to ask for -- the count of "
                       "pieces is not a diagnostic somebody remembered to run.",
                source="spar/results_spar.json",
                field="invoice.expected_total",
                value=_read("spar/results_spar.json", "invoice.expected_total"),
                does_not_supply="anything about parts that were never entered. It "
                                "reveals separation WITHIN what you described, not "
                                "the existence of what you did not"),
            newly_checked=True,
            figures=[Figure(
                figure="Two rooms with no door between them, and a tape measure "
                       "that still reports a short distance because it went round "
                       "the outside of the building.",
                drawn_from="LMD H2 -- disconnected pairs return a finite 1.118, "
                           "nearer than a genuine 1.732 inside one piece",
                schema="Proximity is not connection. Something can appear close "
                       "and have no path to you at all, and only checking for the "
                       "door tells them apart.")]),

        Question(
            n=3,
            name="Stewardship",
            asks="Who is checking, and are they actually independent?",
            why_no_measurement_answers_it=(
                "Two checks can both pass while testing the same thing. "
                "Independence is a fact about how the checks were OBTAINED, "
                "which is upstream of anything either check can report."),
            check=Check(
                module="plumb + LISM validity gates",
                checks="Variance inflation between the two hops must be under 5. "
                       "Yeast passes at 1.003; SEC EDGAR fails at 6.4 with a "
                       "circular outcome and is refused as a valid test.",
                source="lism-cohorts/results_meta.json",
                field="cohorts.A_yeast.VIF",
                value=_read("lism-cohorts/results_meta.json", "cohorts.A_yeast.VIF"),
                does_not_supply="independence of anything not measured -- two "
                                "collinear sources score badly, two conspiring "
                                "ones may not"),
            figures=[Figure(
                figure="Two witnesses who turn out to have been standing together "
                       "the whole time. There was only ever one account.",
                drawn_from="LISM invariant I1, VIF 1.003 against 6.4",
                schema="Independence is a property of how testimony was obtained, "
                       "not of how much of it there is. Agreement between two "
                       "things that share a source is not corroboration.")]),

        Question(
            n=4,
            name="Reference-lock",
            asks="What is the answer measured against, and could the measurer "
                 "have reached it?",
            why_no_measurement_answers_it=(
                "A program can read anything in its scope, so 'we did not look' "
                "is a promise. Promises are not checkable; only absences are."),
            check=Check(
                module="plumb",
                checks="The reference field is DELETED before the run, and the "
                       "deletion is committed inside the receipt digest. An "
                       "auditor verifies the blinding from the receipt rather "
                       "than trusting that it happened.",
                source="smi/results_smi.json",
                field="phase2_test.H3_zero_coupling_collapses.d_at_J0",
                value=_read("smi/results_smi.json",
                            "phase2_test.H3_zero_coupling_collapses.d_at_J0"),
                does_not_supply="anything about the ten fields you did not blind, "
                                "or the rows you did not include"),
            figures=[Figure(
                figure="A room so dark that everything seems to be touching you.",
                drawn_from="LMD H3 -- with every coupling at zero the metric "
                           "returns distance 0.000000, so a dead mesh measures as "
                           "perfectly contracted",
                schema="Total absence of connection can read, from inside, exactly "
                       "like total connection. The two are told apart by checking, "
                       "not by how it feels.")]),

        Question(
            n=5,
            name="Disclosure",
            asks="What did it not tell me, and would I know if it hadn't?",
            why_no_measurement_answers_it=(
                "A ledger cannot contain its own omissions. Absence of a record "
                "is not a record of absence, and no completeness claim made from "
                "inside a record can be checked from inside that record. "
                "keel/run.plumb HALTS on exactly this rather than reporting "
                "completeness it cannot establish."),
            check=Check(
                module="smi",
                checks="The projection measures what it destroyed and prints it. "
                       "On the mesh SMI ships, two elements are drawn on top of "
                       "each other while being 70.7% of the whole mesh's diameter "
                       "apart -- stated in a sentence, a readout cell and a mark "
                       "on the drawing.",
                source="smi/results_flatness.json",
                field="default_plane.share_of_diameter_hidden",
                value=_read("smi/results_flatness.json",
                            "default_plane.share_of_diameter_hidden"),
                does_not_supply="any blind spot it cannot COMPUTE. A projection "
                                "loss is computable because both the true and the "
                                "drawn distance exist. An omission from a record "
                                "is not. This check reaches the first kind and "
                                "provably not the second"),
            newly_checked=True,
            figures=[Figure(
                figure="Asking only the people who arrived how they found the road.",
                drawn_from="LISM invariant I2 -- a test is valid only where the "
                           "failing region is populated; the GitHub cohort splits "
                           "750 fail / 242 survive",
                schema="A claim that has never been given the chance to come out "
                       "false has not been examined. The ones who did not make it "
                       "have to be in the count."),
                Figure(
                figure="Cut the trunk and every branch is still a branch, still "
                       "shaped like a branch, and connected to nothing.",
                drawn_from="the swarm S4 -- removing the root leaves 200 of 200 "
                           "descendants at infinite distance, immediately",
                schema="A structure wholly dependent on one source does not "
                       "degrade gracefully when the source is withdrawn. It is "
                       "intact and inert at the same moment -- which is why a "
                       "system that looks unchanged is not thereby disclosed as "
                       "working.")]),
    ]


CANNOT = (
    "None of the five is answered here. Each has an executable check that a duty "
    "was discharged, and a figure that carries what the question means. A check "
    "is not an answer and a figure is not evidence. No dataset and no simulation "
    "can supply the answers; what is done is abstraction of measurement into "
    "schema, one direction, with no evidential weight in either.")


def render():
    qs = build()
    return {
        "answers_from_measurement": ANSWERS,
        "cannot": CANNOT,
        "checked": sum(1 for q in qs if q.check is not None),
        "newly_checked": [q.name for q in qs if q.newly_checked],
        "questions": [q.as_dict() for q in qs],
    }


def main():
    r = render()
    print("=" * 78)
    print("  THE FIVE GOVERNANCE QUESTIONS")
    print("=" * 78)
    print(f"\n  {r['answers_from_measurement']}")
    print(f"  operational checks: {r['checked']} of 5"
          f"   (newly checked: {', '.join(r['newly_checked']) or 'none'})\n")
    for q in r["questions"]:
        print("-" * 78)
        print(f"  Q{q['n']} — {q['name']}{'   [NEWLY CHECKED]' if q['newly_checked'] else ''}")
        print(f"    asks        {q['asks']}")
        print(f"    unmeasurable {q['why_no_measurement_answers_it']}")
        c = q["check"]
        if c:
            print(f"    CHECK       [{c['module']}] {c['checks']}")
            print(f"                {c['source']} :: {c['field']} = {c['value']}")
            print(f"    NOT SUPPLIED {c['does_not_supply']}")
        else:
            print("    CHECK       none exists")
        for f in q["figures"]:
            print(f"    FIGURE      {f['figure']}")
            print(f"                from {f['drawn_from']}")
            print(f"    SCHEMA      {f['schema']}")
            print(f"    {f['proves']}")
    print("-" * 78)
    print(f"\n  {r['cannot']}\n")
    path = os.path.join(HERE, "results_questions.json")
    json.dump(r, open(path, "w", encoding="utf-8"), indent=2)
    print(f"  wrote ncu/results_questions.json\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
