#!/usr/bin/env python3
"""emit.py — Page Code writes its audit as a Plumb program, and runs it.

WHY THE AUDIT GOES THROUGH A LANGUAGE INSTEAD OF STRAIGHT TO A NUMBER
====================================================================
`page-code/run_audit.py` already produces the readings. It could print them.
The reason it does not is that a printed number carries none of its own
obligations: nothing in a JSON field stops popularity reaching the answer,
nothing forces the verdict to name which signals fired, and nothing records
what produced it.

Writing the same audit as a Plumb program moves those obligations from the
author's care into the interpreter. The program below DELETES stars and
downloads before evaluation, is refused if it does not declare where each leg
came from, and cannot return a bare figure.

THE MAPPING, AND IT IS A CHOICE — SO IT IS WRITTEN DOWN
=======================================================
    capacity  files_scanned          how much there is to work with
    encode    files_in_graph / files_scanned
              can a file be reached from the rest of the project at all
    decode    edges / files_scanned
              how much of it is actually used by something else

That mapping is a judgement, not a measurement. `files_scanned` is a count of
files, and whether it stands for "capacity" is exactly the kind of thing Plumb
CANNOT check — see spec.py. It is stated here so a reader can disagree with it
rather than having to reverse-engineer it from a number.

THE FLOOR IS A PREFERENCE
=========================
`floor 0.02` says where this audit chooses to stop reporting. It is not a
prediction that a project below it will fail. A hard fidelity gate that CLAIMED
to predict failure was retired at p = 0.735 and does not come back here.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from plumb.plumb import parse, run          # noqa: E402
from plumb.spec import lint                 # noqa: E402

PROGRAM = '''\
# structure.plumb -- written by Page Code, run by Plumb.
#
# The question: of everything in this project, how much of it is actually
# joined to the rest, and how much gets used by something else?

plumb "project-structure" {

  capacity  U    from field "files_scanned"

  # leg 1: can a file be reached from the rest of the project at all?
  encode    Denc from ratio "files_in_graph"/"files_scanned"

  # leg 2: how much of the project is used by something else in it?
  decode    Ddec from ratio "edges"/"files_scanned"

  floor 0.02

  # popularity is DELETED, not ignored. A project is not better structured
  # because more people starred it, and there is now nowhere for that to enter.
  blind "stars"
  blind "downloads"
  blind "description"

  independent encode decode
  require evidence 3 of 5
  handles
  receipt
}
'''


def records_from_audit(path: str = None) -> list:
    """The audit rows, as records Plumb can read. ABSENT projects are dropped
    rather than passed in as zeros -- a project that does not exist is not a
    project scoring nothing."""
    path = path or os.path.join(ROOT, "page-code", "results_audit.json")
    d = json.load(open(path))
    out = []
    for group in ("third_party", "products"):
        for name, r in d[group].items():
            if r.get("status") == "ABSENT":
                continue
            c = r["counts"]
            out.append({
                "name": name,
                "group": group,
                "files_scanned": c["files_scanned"],
                "files_in_graph": c["files_in_graph"],
                "edges": c["edges"],
                # deliberately present so `blind` has something real to delete;
                # if blinding ever stops being physical this is what leaks.
                "stars": 0,
                "description": f"{name} is the best library of its kind",
            })
    return out


def audit_as_plumb(path: str = None) -> dict:
    problems = [p.as_dict() for p in lint(PROGRAM)]
    prog = parse(PROGRAM)
    recs = records_from_audit(path)
    result = run(prog, recs)
    named = []
    for rec, v in zip(recs, result["verdicts"]):
        row = dict(v)
        row["name"] = rec["name"]
        row["group"] = rec["group"]
        named.append(row)
    return {"program": PROGRAM, "lint": problems,
            "n_records": len(recs), "verdicts": named,
            "audit": result["audit"]}


if __name__ == "__main__":
    r = audit_as_plumb()
    print("lint problems:", len(r["lint"]))
    print("records:", r["n_records"])
    print("audit:", json.dumps(r["audit"], indent=1)[:600])
    print("\nverdicts:")
    for v in r["verdicts"]:
        c = v.get("confidence")
        print(f"  {v['name']:16s} {v['verdict']:9s} "
              f"conf={'-' if c is None else format(c, '.3f')}  "
              f"{(v.get('reasons') or [''])[0][:58]}")
