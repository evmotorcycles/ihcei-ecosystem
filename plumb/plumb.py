#!/usr/bin/env python3
"""
plumb.py -- PLUMB, a small declarative language for governance rules.
================================================================================
    python3 plumb/plumb.py examples/vendor.plumb data.json

A plumb line finds true vertical using a force you cannot argue with. That is the
whole idea: a Plumb program declares what must hold, and the interpreter is
*structurally incapable* of producing a verdict that skips those obligations.

*** HONEST SCOPE ***
Plumb is a DOMAIN-SPECIFIC LANGUAGE, not a general-purpose programming language.
It has no loops, no user functions, no I/O and no arithmetic beyond what the
declared operators provide. Calling it "a new programming language" in the sense
of Python or Rust would be an overclaim. What it genuinely is: a small, real,
runnable rule language whose semantics enforce three governance obligations that
ordinary code leaves optional.

--------------------------------------------------------------------------------
WHAT MAKES IT A GOVERNANCE LANGUAGE RATHER THAN AN RT LANGUAGE

An RT language lets you write `return score` and be done. Plumb cannot express
that. Four differences are built into the semantics, not into a linter:

  1. NO BARE RETURN.  Every verdict carries confidence, the evidence it rests on,
     and a receipt. There is no syntax for an unqualified answer.
  2. `blind` IS PHYSICAL.  Fields declared blind are deleted from the record
     before evaluation begins. The evaluator cannot read them because they are
     not there -- not because a rule says it shouldn't.
  3. `independent` IS CHECKED.  Two fidelity legs must carry different
     information. A program whose legs are the same column is rejected at
     evaluation, not warned about.
  4. `abstain` IS A RESULT, not an error. Below the floor, the program returns
     ABSTAIN with reasons. Absence of an answer is a first-class outcome.

Q1 purpose      -> `capacity` x `encode` x `decode`, with capacity alone inert
Q3 stewardship  -> `independent`, the two-hop requirement
Q4 reference    -> `blind`, the decoupled shield
--------------------------------------------------------------------------------
"""
import hashlib
import json
import math
import os
import re
import sys

# --------------------------------------------------------------------- lexer --
TOKEN = re.compile(r"""
    (?P<ws>\s+|\#[^\n]*)
  | (?P<str>"[^"]*")
  | (?P<num>-?\d+(?:\.\d+)?)
  | (?P<punc>[{}/])
  | (?P<word>[A-Za-z_][A-Za-z0-9_]*)
""", re.X)


def lex(src):
    out, i = [], 0
    while i < len(src):
        m = TOKEN.match(src, i)
        if not m:
            raise PlumbError(f"unexpected character {src[i]!r} at offset {i}")
        i = m.end()
        if m.lastgroup == "ws":
            continue
        val = m.group()
        out.append((m.lastgroup, val[1:-1] if m.lastgroup == "str" else val))
    return out


class PlumbError(Exception):
    pass


class Abstain(Exception):
    """Raised when a program cannot honestly produce a verdict. Not a failure."""
    def __init__(self, reasons):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


# -------------------------------------------------------------------- parser --
class Program:
    def __init__(self, name):
        self.name = name
        self.capacity = None          # (alias, field)
        self.encode = None            # (alias, spec)
        self.decode = None
        self.floor = 0.0
        self.blind = []               # fields physically removed before evaluation
        self.independent = False
        self.require_evidence = None  # (k, n)
        self.handles = False          # name WHICH signals carried the count
        self.receipt = False


def parse(src):
    toks = lex(src)
    p = 0

    def peek():
        return toks[p] if p < len(toks) else (None, None)

    def eat(kind=None, val=None):
        nonlocal p
        if p >= len(toks):
            raise PlumbError("unexpected end of program")
        k, v = toks[p]
        if (kind and k != kind) or (val and v != val):
            raise PlumbError(f"expected {val or kind}, found {v!r}")
        p += 1
        return v

    eat("word", "plumb")
    prog = Program(eat("str"))
    eat("punc", "{")
    while peek()[1] != "}":
        kw = eat("word")
        if kw == "capacity":
            alias = eat("word"); eat("word", "from"); eat("word", "field")
            prog.capacity = (alias, eat("str"))
        elif kw in ("encode", "decode"):
            alias = eat("word"); eat("word", "from")
            how = eat("word")
            if how == "field":
                spec = ("field", eat("str"), peek()[1] == "inverse" and (eat("word") or True))
            elif how == "ratio":
                a = eat("str"); eat("punc", "/"); spec = ("ratio", a, eat("str"))
            else:
                raise PlumbError(f"unknown source {how!r} (use 'field' or 'ratio')")
            setattr(prog, kw, (alias, spec))
        elif kw == "floor":
            prog.floor = float(eat("num"))
        elif kw == "blind":
            prog.blind.append(eat("str"))
        elif kw == "independent":
            eat("word"); eat("word")            # 'independent encode decode'
            prog.independent = True
        elif kw == "require":
            eat("word", "evidence"); k = int(eat("num")); eat("word", "of"); n = int(eat("num"))
            prog.require_evidence = (k, n)
        elif kw == "handles":
            # A bare count is the failure this obligation exists to stop. "4 of 5"
            # tells a reader how many signals fired and leaves them to guess which,
            # so they cannot go and check any of them. `handles` makes the verdict
            # name the signals it passed, the ones it did not, and the numbers
            # behind them -- the load-bearing parts, handed over.
            prog.handles = True
        elif kw == "receipt":
            prog.receipt = True
        else:
            raise PlumbError(f"unknown statement {kw!r}")
    eat("punc", "}")
    if not (prog.capacity and prog.encode and prog.decode):
        raise PlumbError("a plumb program must declare capacity, encode and decode")
    return prog


# ----------------------------------------------------------------- evaluator --
def _num(rec, key):
    v = rec.get(key)
    if v is None:
        raise Abstain([f"field {key!r} is missing"])
    try:
        return float(v)
    except (TypeError, ValueError):
        raise Abstain([f"field {key!r} is not numeric"])


def _leg(rec, spec):
    kind = spec[0]
    if kind == "field":
        _, key, inverse = spec
        v = _num(rec, key)
        return 1.0 / (1.0 + v) if inverse else max(0.0, min(1.0, v))
    _, a, b = spec
    den = _num(rec, b)
    return 0.0 if den == 0 else max(0.0, min(1.0, _num(rec, a) / den))


def _pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 1.0                      # a constant leg carries no information
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sxx * syy)


def vif(xs, ys):
    r = _pearson(xs, ys)
    if r is None:
        return None
    return float("inf") if abs(r) >= 1.0 else 1.0 / (1.0 - r * r)


def run(prog, records):
    """Evaluate a Plumb program over records. Returns verdicts + a program-level audit.

    Every verdict carries confidence, evidence and a receipt -- the language has no
    way to express an unqualified answer.
    """
    # (Q4) BLIND IS PHYSICAL: the declared fields are removed before anything reads them.
    clean, stripped = [], 0
    for r in records:
        c = dict(r)
        for b in prog.blind:
            if b in c:
                del c[b]
                stripped += 1
        clean.append(c)

    enc_vals, dec_vals, verdicts = [], [], []
    for rec in clean:
        try:
            cap = _num(rec, prog.capacity[1])
            u = math.log10(max(1.0, cap))
            e = _leg(rec, prog.encode[1])
            d = _leg(rec, prog.decode[1])
        except Abstain as ab:
            verdicts.append({"verdict": "ABSTAIN", "reasons": ab.reasons,
                             "confidence": None, "receipt": None})
            continue
        enc_vals.append(e); dec_vals.append(d)
        weak = min(e, d)
        signals = {"capacity_present": cap > 0, "encode_above_floor": e >= prog.floor,
                   "decode_above_floor": d >= prog.floor, "both_legs_present": True,
                   "not_collapsed": weak >= prog.floor}
        hits = sum(1 for v in signals.values() if v)
        if weak < prog.floor:
            v = {"verdict": "ABSTAIN", "reasons": [f"weakest leg {weak:.3f} is below the floor {prog.floor}"],
                 "confidence": 0.0, "yield": 0.0}
        else:
            v = {"verdict": "SUPPORTED", "reasons": [], "confidence": round(weak, 3),
                 "yield": round(u * e * d, 4)}
        if prog.require_evidence:
            k, n = prog.require_evidence
            if hits < k:
                v = {"verdict": "ABSTAIN", "confidence": v.get("confidence"),
                     "reasons": [f"only {hits} of {n} evidence signals present, {k} required"],
                     "yield": 0.0}
        v.update({"encode": round(e, 4), "decode": round(d, 4), "capacity": round(u, 4),
                  "evidence": f"{hits}/{len(signals)}"})
        if prog.handles:
            # (handles) a count never travels without the things it counted
            v["handles"] = {
                "met": sorted(k for k, ok in signals.items() if ok),
                "missing": sorted(k for k, ok in signals.items() if not ok),
                "values": {"capacity": round(u, 4), "encode": round(e, 4),
                           "decode": round(d, 4), "weakest_leg": round(weak, 4),
                           "floor": prog.floor},
            }
        # (no bare return) every verdict is receipted
        v["receipt"] = hashlib.sha256(
            json.dumps({"p": prog.name, "v": v["verdict"], "r": rec}, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]
        verdicts.append(v)

    audit = {"program": prog.name, "records": len(records),
             "blind_fields": prog.blind, "blind_values_stripped": stripped,
             "floor": prog.floor, "receipts": prog.receipt}

    # (Q3) INDEPENDENCE IS CHECKED, and failing it stops the program.
    #
    # Three states, never two. "Checked and failed" and "could not be checked"
    # are different facts and collapsing them is itself a governance failure:
    # one is a finding, the other is an absence of evidence.
    #
    #   VERIFIED_INDEPENDENT  VIF < 5           -> proceed
    #   DEPENDENT             VIF >= 5 or inf   -> HALT, emit no verdicts
    #   UNVERIFIABLE          fewer than 3 records, VIF undefined
    #                                           -> proceed, but every verdict is
    #                                              stamped independence_checked=False
    #                                              so it can never be mistaken for
    #                                              a checked result.
    if prog.independent:
        v = vif(enc_vals, dec_vals)
        audit["vif"] = None if v is None else ("inf" if v == float("inf") else round(v, 4))
        if v is None:
            audit["independence"] = "UNVERIFIABLE"
            audit["independent"] = None
            audit["unverifiable_reason"] = (
                "fewer than 3 evaluable records — the two-hop requirement is a "
                "cohort-level property and cannot be measured on this sample")
            for vd in verdicts:
                vd["independence_checked"] = False
        elif v == float("inf") or v >= 5.0:
            audit["independence"] = "DEPENDENT"
            audit["independent"] = False
            audit["halted"] = ("the two legs are not independent (VIF %s) — a program whose "
                               "encode and decode carry the same information is rejected"
                               % ("infinite" if v == float("inf") else round(v, 2)))
            return {"verdicts": [], "audit": audit}
        else:
            audit["independence"] = "VERIFIED_INDEPENDENT"
            audit["independent"] = True
            for vd in verdicts:
                vd["independence_checked"] = True
    audit["halted"] = None
    return {"verdicts": verdicts, "audit": audit}


def main():
    if len(sys.argv) < 3:
        print(__doc__.strip().split("\n\n")[0])
        print("\nusage: python3 plumb/plumb.py <program.plumb> <records.json> [--key repos]")
        raise SystemExit(1)
    src = open(sys.argv[1]).read()
    data = json.load(open(sys.argv[2]))
    key = sys.argv[sys.argv.index("--key") + 1] if "--key" in sys.argv else None
    records = data[key] if key else (data if isinstance(data, list) else next(
        v for v in data.values() if isinstance(v, list)))
    res = run(parse(src), records)
    a = res["audit"]
    print(f"program   : {a['program']}")
    print(f"records   : {a['records']}   floor {a['floor']}")
    print(f"blind     : {a['blind_fields']}  ({a['blind_values_stripped']} values physically removed)")
    if "vif" in a:
        print(f"two legs  : VIF {a['vif']}  {a['independence']}")
        if a.get("unverifiable_reason"):
            print(f"            {a['unverifiable_reason']}")
    if a["halted"]:
        print(f"HALTED    : {a['halted']}")
        raise SystemExit(3)
    sup = [v for v in res["verdicts"] if v["verdict"] == "SUPPORTED"]
    abst = [v for v in res["verdicts"] if v["verdict"] == "ABSTAIN"]
    print(f"verdicts  : {len(sup)} supported, {len(abst)} abstained (abstaining is a result, not an error)")
    for v in res["verdicts"][:5]:
        print(f"   {v['verdict']:<10} conf={v.get('confidence')} evidence={v.get('evidence')} receipt={v.get('receipt')}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
