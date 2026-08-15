#!/usr/bin/env python3
"""metaphor.py -- layer-1 telemetry, abstracted into a metaphor. One direction.

    python3 ncu/metaphor.py

This package computes NOTHING. It reads numbers that were measured elsewhere and
states, for each one, what it can be used to *illustrate*. Every entry carries
`PROVES: NOTHING`, in the data, because a stamp in a footnote is a stamp
somebody can crop.

The rule, in one line: a measurement may be abstracted INTO a metaphor; a
metaphor may never be abstracted back into a measurement. See FIREWALL.md.

Nafs is taken here as a cognitive essence whose primary functions are Salat and
Zakat. Those are philosophy-layer terms and they stay in this package -- a test
fails if any of them appears in a measurement module.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

STAMP = "PROVES: NOTHING"


@dataclass(frozen=True)
class Abstraction:
    """One measured number, and the one thing it can be used to illustrate."""
    measured: str          # what was measured, in layer-1 words
    source: str            # the file it came from
    field: str             # the field inside that file
    value: object          # the number itself, re-read at runtime
    figure: str            # the metaphor
    illustrates: str       # what philosophy point it illustrates
    proves: str = STAMP    # never anything else

    def as_dict(self):
        d = asdict(self)
        assert d["proves"] == STAMP, "the stamp is not editable"
        return d


def _read(rel, path):
    """Pull one field out of a results file. Fails loudly if it is not there."""
    data = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
    cur = data
    for key in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(key)]
        else:
            if key not in cur:
                raise KeyError(f"{rel} has no field {path!r} — a metaphor may not "
                               f"cite a number that does not exist")
            cur = cur[key]
    return cur


def build():
    """The abstractions, each tied to a number that is re-read from disk."""
    out = []

    # ---------------------------------------------------------------- LMD ---
    out.append(Abstraction(
        measured="Scaling every coupling by the same factor rescales every distance "
                 "and changes nothing else: slope −0.5, R² 1.000000, on every graph.",
        source="smi/results_smi.json", field="phase2_test.H0_identity.slope",
        value=_read("smi/results_smi.json", "phase2_test.H0_identity.slope"),
        figure="Turning every lamp in a room up together changes how bright the room "
               "is and nothing about where anything sits.",
        illustrates="A uniform change in intensity is not a change in structure. "
                    "Effort applied evenly to everything moves the whole scene and "
                    "rearranges none of it."))

    out.append(Abstraction(
        measured="Raising the coupling on ONE link moves the nearest elements most, "
                 "and the effect falls off monotonically with hop distance.",
        source="smi/results_smi.json", field="phase2_test.H4_local_pull_is_local.by_hop.0",
        value=_read("smi/results_smi.json", "phase2_test.H4_local_pull_is_local.by_hop.0"),
        figure="Pulling one thread in a net: what is knotted to it moves a lot, the "
               "next ring moves less, the far edge barely stirs.",
        illustrates="A particular attention has a reach, and the reach is finite and "
                    "graded. It is not the same act as turning everything up."))

    out.append(Abstraction(
        measured="Two elements with no path between them come back from the raw "
                 "pseudo-inverse at a FINITE distance (1.118) — nearer than a real "
                 "distance inside one piece (1.732). The engine has to detect the "
                 "break itself and return infinity.",
        source="smi/results_smi.json", field="phase2_test.H2_disconnected_is_finite.raw",
        value=_read("smi/results_smi.json", "phase2_test.H2_disconnected_is_finite.raw"),
        figure="Two rooms with no door between them, and a tape measure that still "
               "reports a short distance because it went round the outside of the "
               "building.",
        illustrates="Proximity is not connection. Something can appear close and have "
                    "no path to you at all, and only checking for the door tells them "
                    "apart."))

    out.append(Abstraction(
        measured="With every coupling at zero the metric returns distance 0.000000 — "
                 "a completely dead mesh measures as PERFECTLY CONTRACTED, identical "
                 "to a perfectly coupled one.",
        source="smi/results_smi.json", field="phase2_test.H3_zero_coupling_collapses.d_at_J0",
        value=_read("smi/results_smi.json", "phase2_test.H3_zero_coupling_collapses.d_at_J0"),
        figure="A room so dark that everything seems to be touching you.",
        illustrates="Total absence of connection can read, from inside, exactly like "
                    "total connection. The two are told apart by checking, not by how "
                    "it feels."))

    # -------------------------------------------------------------- swarm ---
    out.append(Abstraction(
        measured="Fidelity falls with lineage depth: Spearman ρ = −0.75 over 40 "
                 "simulated swarms.",
        source="swarm-lmd/results_swarm.json", field="S1_decay_with_depth.rho",
        value=_read("swarm-lmd/results_swarm.json", "S1_decay_with_depth.rho"),
        figure="A message passed down a long line of people arrives thinner than it "
               "left, and each retelling costs something.",
        illustrates="What is inherited attenuates. Distance from the source is not "
                    "neutral, and nothing preserves itself by being passed on."))

    out.append(Abstraction(
        measured="Capacity buys reach and nothing else: ρ(U, descendants) = +0.34, "
                 "ρ(U, fidelity received) = −0.01.",
        source="swarm-lmd/results_swarm.json", field="S5_what_capacity_does.rho_U_descendants",
        value=_read("swarm-lmd/results_swarm.json", "S5_what_capacity_does.rho_U_descendants"),
        figure="A loud voice gathers a bigger crowd and does not, by being loud, "
               "receive a truer account of anything.",
        illustrates="Reach and soundness are separate quantities. Growing the first "
                    "has no effect on the second, which is why counting an audience "
                    "measures the wrong thing."))

    out.append(Abstraction(
        measured="Removing the root's outbound coupling leaves 200 of 200 descendants "
                 "at infinite distance — every one of them, immediately.",
        source="swarm-lmd/results_swarm.json", field="S4_revocation.cut_off",
        value=_read("swarm-lmd/results_swarm.json", "S4_revocation.cut_off"),
        figure="Cut the trunk and every branch is still a branch, still shaped like a "
               "branch, and connected to nothing.",
        illustrates="A structure entirely dependent on one source does not degrade "
                    "gracefully when the source is withdrawn. It is intact and inert "
                    "at the same moment."))

    # --------------------------------------------------------------- LISM ---
    # E = U*D, with D = D_enc * D_dec -- two multiplicative fidelity hops.
    out.append(Abstraction(
        measured="D is the PRODUCT of two hops, encode and decode. Across the "
                 "swarm cohort mean D falls from 0.838 at the first remove to "
                 "0.014 at the 39th.",
        source="lism-cohorts/results_meta.json", field="cohorts.D_swarm.meanD_last",
        value=_read("lism-cohorts/results_meta.json", "cohorts.D_swarm.meanD_last"),
        figure="Speaking through a wall and being heard through a wall. Neither "
               "wall has to be thick; two thin ones multiply.",
        illustrates="Transmission has two sides and they compound rather than "
                    "add. Saying it well does not survive being received badly, "
                    "and a fault on either side is a fault in the whole."))

    out.append(Abstraction(
        measured="The accelerating law E = U·D² was pre-registered and LOST: on "
                 "992 real repositories the linear law reaches AUC ~0.73 and the "
                 "quadratic ~0.59 under cross-validation. Four cohorts out of "
                 "four: the plain law was enough.",
        source="lism-cohorts/results_meta.json", field="cohorts.B_github.verdict",
        value=_read("lism-cohorts/results_meta.json", "cohorts.B_github.verdict"),
        figure="Expecting that effort rewards itself faster and faster, and "
               "finding it only ever pays what it pays.",
        illustrates="A hope for acceleration is worth writing down before "
                    "looking, precisely so that it can be given up. Nothing in "
                    "the record improves by being wished at."))

    out.append(Abstraction(
        measured="A dataset counts as a valid test only if the two hops come from "
                 "physically distinct measurements (VIF < 5). Yeast passes at "
                 "1.003; SEC EDGAR fails at 6.4 and its outcome is circular.",
        source="lism-cohorts/results_meta.json", field="cohorts.A_yeast.VIF",
        value=_read("lism-cohorts/results_meta.json", "cohorts.A_yeast.VIF"),
        figure="Two witnesses who turn out to have been standing together the "
               "whole time. There was only ever one account.",
        illustrates="Independence is a property of how testimony was OBTAINED, "
                    "not of how much of it there is. Agreement between two "
                    "things that share a source is not corroboration."))

    out.append(Abstraction(
        measured="A test is only valid if the failing region is populated: at "
                 "least 100 real cases where the outcome did NOT occur. The "
                 "GitHub cohort splits 750 fail / 242 survive.",
        source="lism-cohorts/results_meta.json", field="cohorts.B_github.split",
        value=_read("lism-cohorts/results_meta.json", "cohorts.B_github.split"),
        figure="Asking only the people who arrived how they found the road.",
        illustrates="A claim that has never been given the chance to come out "
                    "false has not been examined. The ones who did not make it "
                    "have to be in the count."))

    out.append(Abstraction(
        measured="The knowledge cohort passed every validity gate and the effect "
                 "was still weak: AUC 0.58-0.62 on N=793, with a time confound "
                 "recorded rather than removed.",
        source="lism-cohorts/results_meta.json", field="cohorts.C_knowledge.effect",
        value=_read("lism-cohorts/results_meta.json", "cohorts.C_knowledge.effect"),
        figure="A properly conducted search that finds very little, written up "
               "at exactly the size it was.",
        illustrates="Doing the procedure correctly does not entitle anyone to a "
                    "result. A small finding reported small is worth more than "
                    "the same finding reported large."))

    return out


# -------------------------------------------------------------- the Nafs ----
# Layer-3 vocabulary. Present here and nowhere else in the repository.
NAFS = {
    "what": "a cognitive essence",
    "primary_functions": ["Salat", "Zakat"],
    "note": "These are philosophy-layer terms. They describe no measured quantity, "
            "index no dataset, and are never computed with. A test fails if any of "
            "them appears in a measurement module.",
}

FUNCTION_FIGURES = [
    {"function": "Salat",
     "figure": "the pull on one thread, applied deliberately and repeatedly to the "
               "same place",
     "drawn_from": "H4 — a local pull moves the near ring most and falls off with "
                   "distance; it is the only gesture that rearranges anything",
     "not": "This does not define, model, measure or evidence Salat. It borrows the "
            "SHAPE of a measured falloff to picture a philosophy point.",
     "proves": STAMP},
    {"function": "Zakat",
     "figure": "what is passed outward down the lineage, against a measured "
               "attenuation of ρ = −0.75 per remove",
     "drawn_from": "S1 — fidelity falls with depth, so anything handed on arrives "
                   "thinner than it left",
     "not": "This does not define, model, measure or evidence Zakat. It borrows the "
            "SHAPE of a measured decay to picture a philosophy point.",
     "proves": STAMP},
]

CANNOT = ("No dataset and no computer simulation can prove NCU. The swarm data is "
          "simulated; the LMD numbers are measurements of a pseudo-inverse. What is "
          "done here is abstraction of computational telemetry into metaphorical "
          "representation to illustrate a governance philosophy — one direction, and "
          "no evidential weight in either.")


def render():
    return {
        "firewall": "layer-1 telemetry → metaphor. Nothing returns.",
        "cannot": CANNOT,
        "nafs": NAFS,
        "function_figures": FUNCTION_FIGURES,
        "abstractions": [a.as_dict() for a in build()],
    }


if __name__ == "__main__":
    r = render()
    print("=" * 78)
    print("  LAYER-1 TELEMETRY, ABSTRACTED INTO METAPHOR")
    print("=" * 78)
    print(f"\n  {r['cannot']}\n")
    for a in r["abstractions"]:
        print("-" * 78)
        print(f"  MEASURED   {a['measured']}")
        print(f"             {a['source']} :: {a['field']} = {a['value']}")
        print(f"  FIGURE     {a['figure']}")
        print(f"  ILLUSTRATES {a['illustrates']}")
        print(f"  {a['proves']}")
    print("-" * 78)
    print(f"\n  NAFS — {NAFS['what']}; primary functions "
          f"{', '.join(NAFS['primary_functions'])}")
    for f in FUNCTION_FIGURES:
        print(f"\n  {f['function']}")
        print(f"    figure      {f['figure']}")
        print(f"    drawn from  {f['drawn_from']}")
        print(f"    NOT         {f['not']}")
    print()
    json.dump(r, open(os.path.join(HERE, "results_ncu.json"), "w"), indent=1)
    print(f"  wrote {os.path.relpath(os.path.join(HERE, 'results_ncu.json'), ROOT)}")
