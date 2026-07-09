#!/usr/bin/env python3
"""
kaggle_dataset_screen.py
=======================
Screens candidate datasets (Kaggle or any open portal) for LISM two-hop
eligibility BEFORE any pre-registration is locked. It operationalizes the three
hard invariants from PREREGISTRATION_generalization.md:

  I1  Genuine channel independence  — D_enc and D_dec from independent sources
  I2  Populated failing region      — real low-fidelity variance, N_fail >= 100
  I3  Measured, non-circular outcome — E observed downstream, not protocol-defined

A dataset passes only if a human can identify, from its schema, two fidelity
signals drawn from DIFFERENT sources plus a downstream measured outcome that can
be linked at the unit level. Convenient single-table datasets almost always fail
I1 or I3 — that is the expected, informative result (a documented non-test), not
a null.

DATA SOURCE (pick one)
  --endpoint URL   a Kaggle proxy that returns JSON dataset metadata for a query
                   (e.g. a Vercel function like api/bill-text.js, with a
                   KAGGLE_KEY server-side). None is deployed at time of writing.
  --kaggle-cli     use the local `kaggle datasets list -s <q> --json` (needs
                   ~/.kaggle/kaggle.json credentials and network egress).
  --results-json   a pre-fetched JSON array of dataset metadata (offline).

Each dataset record may carry: ref/title/subtitle/description, and optionally a
`columns` list. The screen reads these; it never downloads data.

NOTE: this tool reports *eligibility for a two-hop test*, not dataset quality.
A "NON-TEST" verdict means the dataset cannot support the linear-vs-quadratic
comparison — it does not mean the dataset is bad.
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.request
import urllib.parse

DOMAIN_QUERIES = {
    "clinical": [
        "patient safety incident reporting outcomes",
        "root cause analysis adverse events mortality",
        "hospital incident reports readmission",
    ],
    "contract": [
        "contract clauses litigation outcome",
        "court cases contract breach ruling",
        "legal judgments enforcement",
    ],
    "legislation": [
        "congress bills enacted repealed",
        "legislation text implementation rulemaking",
        "statutes federal register durability",
    ],
}

# Signals that a field/description plausibly supplies each hop or the outcome.
ENC = re.compile(r"\b(text|clause|report|narrative|document|specificity|wording|bill|statute|note)\b", re.I)
DEC = re.compile(r"\b(review|audit|enforce\w*|implementation|rulemaking|root[- ]cause|rca|compliance|adjudicat\w*|court|agency|inspection)\b", re.I)
OUTCOME = re.compile(r"\b(mortality|readmission|survival|outcome|death|harm|breach|nullif\w*|repeal\w*|sustained|durab\w*|recurrence)\b", re.I)
SINGLE_SRC = re.compile(r"\b(single|one table|synthetic|generated|sample)\b", re.I)


def fetch_endpoint(url, q):
    full = url + ("&" if "?" in url else "?") + "q=" + urllib.parse.quote(q)
    with urllib.request.urlopen(full, timeout=30) as r:
        data = json.load(r)
    return data.get("datasets") or data.get("results") or data if isinstance(data, (list, dict)) else []


def fetch_cli(q):
    try:
        out = subprocess.check_output(
            ["kaggle", "datasets", "list", "-s", q, "--csv"], timeout=60).decode()
    except Exception as e:
        print(f"  [kaggle-cli] failed for {q!r}: {e}", file=sys.stderr)
        return []
    lines = out.strip().splitlines()
    if len(lines) < 2:
        return []
    hdr = lines[0].split(",")
    return [dict(zip(hdr, ln.split(","))) for ln in lines[1:]]


def text_of(d):
    parts = [str(d.get(k, "")) for k in ("ref", "title", "subtitle", "description", "name")]
    cols = d.get("columns") or []
    parts += [str(c.get("name", c) if isinstance(c, dict) else c) for c in cols]
    return " ".join(parts)


def screen(d):
    t = text_of(d)
    has_enc = bool(ENC.search(t))
    has_dec = bool(DEC.search(t))
    has_out = bool(OUTCOME.search(t))
    single = bool(SINGLE_SRC.search(t))
    # I1: need BOTH hop signals AND no explicit single-source flag. Even then,
    # independence of *source* cannot be proven from metadata -> at best REVIEW.
    i1 = "REVIEW" if (has_enc and has_dec and not single) else "FAIL"
    i3 = "REVIEW" if has_out else "FAIL"
    i2 = "REVIEW"  # variance/N can only be checked on the data itself
    if i1 == "FAIL" or i3 == "FAIL":
        verdict = "NON-TEST"
    else:
        verdict = "CANDIDATE (manual linkage review required)"
    reasons = []
    if i1 == "FAIL":
        reasons.append("no evidence of two independent hops (I1)")
    if i3 == "FAIL":
        reasons.append("no downstream measured outcome (I3)")
    return {"ref": d.get("ref") or d.get("title") or "?",
            "I1": i1, "I2": i2, "I3": i3, "verdict": verdict, "why": "; ".join(reasons)}


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--endpoint")
    src.add_argument("--kaggle-cli", action="store_true")
    src.add_argument("--results-json")
    ap.add_argument("--domain", choices=list(DOMAIN_QUERIES) + ["all"], default="all")
    a = ap.parse_args()

    domains = list(DOMAIN_QUERIES) if a.domain == "all" else [a.domain]
    print("=" * 78)
    print("LISM dataset eligibility screen — three-invariant gate (I1/I2/I3)")
    print("=" * 78)

    candidates = 0
    total = 0
    for dom in domains:
        print(f"\n### DOMAIN: {dom}")
        seen = {}
        for q in DOMAIN_QUERIES[dom]:
            if a.results_json:
                recs = json.load(open(a.results_json))
                recs = recs.get(dom, recs) if isinstance(recs, dict) else recs
            elif a.endpoint:
                try:
                    recs = fetch_endpoint(a.endpoint, q)
                except Exception as e:
                    print(f"  [endpoint] {q!r}: {e}"); recs = []
            else:
                recs = fetch_cli(q)
            for d in (recs or []):
                ref = d.get("ref") or d.get("title") or json.dumps(d)[:40]
                if ref in seen:
                    continue
                seen[ref] = 1
                s = screen(d)
                total += 1
                if s["verdict"].startswith("CANDIDATE"):
                    candidates += 1
                mark = "•" if s["verdict"].startswith("CANDIDATE") else "×"
                print(f"  {mark} {s['ref'][:52]:52s} I1={s['I1']:6s} I3={s['I3']:6s} "
                      f"-> {s['verdict']}")
                if s["why"]:
                    print(f"      {s['why']}")
        if not seen:
            print("  (no datasets returned for this domain's queries)")

    print("\n" + "-" * 78)
    print(f"screened {total} datasets; {candidates} passed the metadata gate "
          f"(still require manual unit-level linkage review for I1/I2).")
    if candidates == 0:
        print("VERDICT: no convenient dataset supports a two-hop test. This is the")
        print("expected non-test outcome — the linked, independent two-hop telemetry")
        print("LISM requires is not available as an off-the-shelf download. Proceed")
        print("via the Stage 1 Registered Report data-holder partnership instead")
        print("(PREREGISTRATION_generalization.md).")
    print("=" * 78)


if __name__ == "__main__":
    main()
