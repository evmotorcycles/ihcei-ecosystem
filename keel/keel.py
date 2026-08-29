#!/usr/bin/env python3
"""keel.py — a structural survey for anyone building a project, human or machine.

THE CARRIER (stage 2), and it is a lens rather than a picture
============================================================
A rope whose strands were all spun from one fibre.

It looks like many strands. It is counted, sold and trusted as many strands.
But it was spun from one fibre, so:

  1. cut the fibre and every strand parts at once,
  2. the further from the spinner, the more each strand frays,
  3. counting strands overstates the rope by the number of strands.

Every one of those three is a MEASUREMENT already in this repository, not a
flourish:

  1. `hf-cohort/swarm` A3 -- revoke the hub and all 12 nodes below it halt,
     max tau_v 4 hops. Every dependent halted; none survived on its own.
  2. `hf-cohort/swarm` A2 -- fidelity decays with lineage depth, corr -0.89
     across 500 simulated nodes on real HF branching.
  3. `oss-audit` RUN A -- four models derive from Qwen/Qwen3.6-27B and each
     settles 0.0625 = 1/16. Four supports, one fibre.

WHAT THE CARRIER PREDICTS THAT NOBODY HERE CONTROLS
On a project graph written by someone who never read any of this, the count of
declared supports will overstate independent support by the same law. If a
project is found whose supports are genuinely independent at the rate its own
manifest claims, the carrier is wrong and this file should be deleted rather
than adjusted.

THE CONTRACT (stage 3), inherited from the 992-repository governance cohort
==========================================================================
`governance-learning/results_gla.json` (N = 992) measured seven governance
properties of a learner. They are the service's contract here, by number:

  L1  it DECLINES. Measured abstain rate 0.2568 on the cohort. A survey that
      always answers is not being careful, it is being agreeable.
  L3  blinding is PHYSICAL. An input field the survey does not accept cannot
      change a reading, because there is nowhere to put it (`validate` refuses
      unknown keys rather than ignoring them).
  L4  the independence gate HALTS. If declared supports collapse onto one
      origin, the count reading does not shrink -- it stops. Reporting "1 of 4"
      would still be reporting a number about a thing that is not four.
  L5  no bare return. Every readout carries its own reason.
  L6  self-training refused. A survey will not accept its own output as input.
  L7  calibration measured, never gated.

WHAT IS NEVER DONE HERE
The three readouts are never added, averaged or combined. Structure, repetition
and latency are different kinds of quantity, and a single "project health score"
would be the mask this whole stack is arranged against. There is no such field
and `test_keel.py` greps for one.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from spar.spar import Structure, bearings, single_points   # noqa: E402
from fathom.fathom import Claim, sound                     # noqa: E402
from tau_v_monitor.core import Event, assess               # noqa: E402

ACCEPTED = {"name", "parts", "links", "conclusion", "supports", "events", "now"}

CANNOT = [
    "It does not know what your project is for, and cannot tell you whether it "
    "is a good idea.",
    "It only knows the parts you entered. A dependency you did not declare is "
    "invisible to it and will not appear in any reading.",
    "A reading of 'one fibre' is about what you declared, never about what is "
    "true of your system.",
    "It never says a project is healthy. There is no such reading here.",
]

GO_CHECK = [
    "Take the step it named as having no second way round, and write down on "
    "paper what you would do this week if it stopped.",
    "Take two supports it says share an origin, and ask the person responsible "
    "for each whether that is news to them.",
    "Open your own tracker and read the three oldest things still open.",
]


class Refused(Exception):
    """Raised rather than returning a number nobody can check."""


# ── L3: blinding is physical ────────────────────────────────────────────────
def validate(project: dict) -> None:
    """Enforcement by SUBTRACTION. A field the survey does not accept is not
    ignored -- it is refused, because a field that is merely ignored today is a
    field somebody wires up tomorrow. There is nowhere to put popularity here.
    """
    if not isinstance(project, dict):
        raise Refused("that is not a project")
    extra = sorted(set(project) - ACCEPTED)
    if extra:
        raise Refused(
            "this survey has nowhere to put: " + ", ".join(extra) +
            ". Stars, downloads, age and popularity are not structure, and a "
            "field with nowhere to go cannot quietly become a reading.")
    if "parts" not in project or not project["parts"]:
        raise Refused("a project needs parts before anything can be read")
    # L6: refuses its own output as input
    if "_keel" in str(project.get("name", "")) or "readouts" in project:
        raise Refused("this is a survey, not a project. A survey will not read "
                      "its own output back in as evidence.")


@dataclass
class Readout:
    """L5: no bare return. Every readout says what it is and why."""
    kind: str
    status: str                 # READ | ABSTAINED | HALTED
    says: str
    detail: dict = field(default_factory=dict)


@dataclass
class Survey:
    name: str
    sole_routes: Readout
    counted_twice: Readout
    latency: Readout
    cannot: list = field(default_factory=lambda: list(CANNOT))
    go_check: list = field(default_factory=lambda: list(GO_CHECK))

    def as_dict(self) -> dict:
        d = asdict(self)
        # the readouts are three separate quantities and are never fused.
        # asserted by test_keel.py rather than trusted.
        return d


# ── readout 1: what has no second way round ─────────────────────────────────
def read_sole_routes(parts, links) -> Readout:
    if not links:
        return Readout("sole_routes", "ABSTAINED",
                       "Nothing joins anything yet. With no links there is no "
                       "structure to read, which is not the same as a structure "
                       "with nothing wrong with it.")
    st = Structure(list(parts), [tuple(x) for x in links])
    b = bearings(st)
    sp = [r["part"] for r in single_points(st)]
    return Readout("sole_routes", "READ",
                   (f"{len(sp)} part{'' if len(sp) == 1 else 's'} would break "
                    f"this into more pieces if removed."
                    if sp else
                    "No single part breaks this. Every part has another way "
                    "round it."),
                   {"single_points": sp,
                    "pieces": b["pieces"],
                    "parts": len(parts),
                    "total_bearing": b["total"],
                    "conserved": b["conserved"]})


# ── readout 2: supports that were spun from one fibre ───────────────────────
def read_counted_twice(conclusion, supports, links) -> Readout:
    """`supports` is what the builder CLAIMS holds the conclusion up. The
    origins are what those supports actually hang off in the graph they drew.
    """
    if not conclusion or not supports:
        return Readout("counted_twice", "ABSTAINED",
                       "Nothing was claimed to hold anything up, so there is "
                       "nothing to count.")
    if len(supports) < 2:
        return Readout("counted_twice", "ABSTAINED",
                       "One support is not a count. There is nothing here that "
                       "could be overstated.")

    origins = {}
    for a, b, *_ in links:
        if a in supports:
            origins.setdefault(a, set()).add(b)
    distinct = set()
    for s in supports:
        distinct |= origins.get(s, {s})

    r = sound(Claim(conclusion, list(supports), [tuple(x) for x in links]))
    settles = {x["source"]: x["dependence"] for x in r["by_source"]}

    # L4: the independence gate HALTS rather than reporting a smaller number.
    if len(distinct) == 1 and len(supports) > 1:
        return Readout("counted_twice", "HALTED",
                       (f"These are not {len(supports)} supports. They are one "
                        f"support, counted {len(supports)} times -- every one "
                        f"of them hangs off the same thing. No count is given, "
                        f"because any count would be a number about something "
                        f"that is not there."),
                       {"claimed": len(supports),
                        "distinct_origins": 1,
                        "the_one_origin": sorted(distinct)[0],
                        "each_settles": round(1.0 / (len(supports) ** 2), 12)})

    return Readout("counted_twice", "READ",
                   (f"{len(supports)} supports resting on {len(distinct)} "
                    f"separate things."),
                   {"claimed": len(supports),
                    "distinct_origins": len(distinct),
                    "settles": {k: round(v, 12) for k, v in settles.items()},
                    "deepest_dependence": r["deepest_dependence"],
                    "rests_on_one_thread": r["rests_on_one_thread"]})


# ── readout 3: is your own time-to-fix rising, against your own history ─────
def read_latency(events, now: Optional[datetime]) -> Readout:
    if not events:
        return Readout("latency", "ABSTAINED",
                       "No history given. This reading is against your own "
                       "past and cannot be borrowed from anyone else's.")
    a = assess(events, now=now)
    if a.status == "INSUFFICIENT_DATA":
        return Readout("latency", "ABSTAINED",
                       "Not enough closed items to calibrate against your own "
                       "history. It says so rather than guessing.",
                       {"reasons": a.reasons})
    return Readout("latency", "READ",
                   {"OK": "Your time-to-fix is not rising against your own past.",
                    "WATCH": "One of the two latency signals is elevated.",
                    "ALERT": "Your time-to-fix is rising AND is high against "
                             "your own past."}.get(a.status, a.status),
                   {"status": a.status, "trend": a.trend_direction,
                    "trend_p": a.trend_p,
                    "baseline_tau_v": a.baseline_tau_v,
                    "current_tau_v": a.current_tau_v})


def survey(project: dict) -> Survey:
    validate(project)
    parts = project["parts"]
    links = project.get("links") or []
    return Survey(
        name=project.get("name", "unnamed"),
        sole_routes=read_sole_routes(parts, links),
        counted_twice=read_counted_twice(project.get("conclusion"),
                                         project.get("supports") or [], links),
        latency=read_latency(project.get("events") or [], project.get("now")),
    )


def abstained(s: Survey) -> list:
    return [r.kind for r in (s.sole_routes, s.counted_twice, s.latency)
            if r.status != "READ"]
