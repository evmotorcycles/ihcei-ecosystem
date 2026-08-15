#!/usr/bin/env python3
"""
governance.py -- the four Plumb obligations, available inside ordinary Python.
================================================================================

*** HONEST SCOPE ***
This does NOT "transform Python". Python is not modifiable and nothing here
changes the language. What it does is make the four governance obligations
*enforced at runtime* in plain Python code, so that a function which skips them
raises instead of quietly returning a number.

The difference from a linter, a type hint, or a code-review checklist is that
none of those can stop a running program. These can, and do.

    from governance import verdict, blind, evidence, Ledger, abstain

    @verdict
    @blind("self_reported_score", "vendor_blurb")
    @evidence(3, of=5)
    def assess(record):
        ...
        return support(0.72, "backlog is being cleared")

Four obligations, same as the Plumb language:

  1. NO BARE RETURN     @verdict rejects a plain value. You must return a
                        Verdict carrying confidence, evidence and a receipt.
  2. BLIND IS PHYSICAL  @blind deletes the fields from the argument before the
                        function body runs. The body cannot read them because
                        they are gone -- not because a policy says not to.
  3. INDEPENDENCE IS    two_hop() measures it and returns one of three states,
     CHECKED            never two: VERIFIED / DEPENDENT / UNVERIFIABLE.
  4. ABSTAIN IS A       abstain() is a normal return value, not an exception,
     RESULT             not None, and not a zero pretending to be a score.

--------------------------------------------------------------------------------
WHAT THIS CANNOT DO

It cannot make a rule correct. A fully receipted, fully blinded, independently
verified function can still encode a foolish policy. These constructs force the
obligations to be visible and checkable. They do not supply judgement, and
nothing here should be read as claiming they do.
"""
import functools
import hashlib
import inspect
import json
import math
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

__all__ = ["Verdict", "verdict", "blind", "evidence", "support", "abstain",
           "two_hop", "Ledger", "GovernanceError"]


class GovernanceError(Exception):
    """Raised when code tries to produce an answer without meeting an obligation."""


# ------------------------------------------------------------ the verdict --
@dataclass(frozen=True)
class Verdict:
    """The only thing a governed function is allowed to return.

    There is deliberately no way to construct one that carries a value but no
    confidence and no reasons. `value` may be None; `reasons` may not be empty.
    """
    supported: bool
    value: Optional[float]
    confidence: Optional[float]
    reasons: tuple
    evidence: str = "unspecified"
    independence_checked: Optional[bool] = None
    receipt: str = ""
    blinded: tuple = ()          # (field, ...) physically removed before evaluation

    def __post_init__(self):
        if not self.reasons:
            raise GovernanceError(
                "a verdict with no reasons is a bare return with extra steps")
        if self.supported and self.confidence is None:
            raise GovernanceError(
                "a SUPPORTED verdict must carry a confidence; if you cannot "
                "give one, the honest return is abstain()")

    @property
    def verdict(self):
        return "SUPPORTED" if self.supported else "ABSTAIN"

    def __str__(self):
        c = "n/a" if self.confidence is None else f"{self.confidence:.3f}"
        return f"{self.verdict} (confidence {c}) — {'; '.join(self.reasons)}"

    def to_dict(self):
        d = asdict(self)
        d["reasons"] = list(self.reasons)
        d["verdict"] = self.verdict
        return d


def support(confidence, *reasons, value=None, evidence="unspecified"):
    """Return a supported verdict. Confidence and at least one reason required."""
    if not reasons:
        raise GovernanceError("support() requires at least one stated reason")
    return Verdict(True, value if value is not None else confidence,
                   float(confidence), tuple(reasons), evidence)


def abstain(*reasons, evidence="unspecified"):
    """Return an abstention. This is a RESULT, not a failure and not an error.

    Note it is a return value, never a raise: abstaining must be as cheap and as
    ordinary as answering, or code will quietly stop doing it.
    """
    if not reasons:
        raise GovernanceError("abstain() requires at least one stated reason")
    return Verdict(False, None, None, tuple(reasons), evidence)


# ------------------------------------------- 1. NO BARE RETURN (@verdict) --
def verdict(fn):
    """Enforce that the decorated function returns a Verdict, and receipt it.

    A function returning 0.72 raises. A function returning None raises. The only
    accepted returns are support(...) and abstain(...).
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        _BLIND.clear()
        out = fn(*args, **kwargs)
        if not isinstance(out, Verdict):
            raise GovernanceError(
                f"{fn.__name__}() returned a bare {type(out).__name__} "
                f"({out!r}). A governed function must return support(...) or "
                f"abstain(...) so the answer carries its confidence, its "
                f"reasons and a receipt.")
        blinded = tuple(_BLIND.get("fields", ()))
        payload = {"fn": fn.__name__, "verdict": out.verdict,
                   "confidence": out.confidence, "reasons": list(out.reasons),
                   "blinded": list(blinded), "stripped": _BLIND.get("stripped", 0),
                   "args": _stable(args), "kwargs": _stable(kwargs)}
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:16]
        return Verdict(out.supported, out.value, out.confidence, out.reasons,
                       out.evidence, out.independence_checked, digest, blinded)
    wrapper.__governed__ = True
    return wrapper


def _stable(obj):
    try:
        json.dumps(obj, default=str)
        return obj
    except TypeError:
        return str(obj)


# ---------------------------------------- 2. BLIND IS PHYSICAL (@blind) ----
_BLIND = {}   # per-call record of what was physically removed; read by @verdict


def blind(*fields):
    """Delete the named fields from every mapping argument before the call.

    The decorated body cannot consult them, cannot log them, and cannot leak
    them into a receipt, because by the time it runs they do not exist.

    This is the Q4 reference-lock: what a thing says about itself is removed
    from the evidence before the thing is evaluated.

    The removal is recorded on the returned Verdict (`.blinded`) and committed
    to inside the receipt digest, so an auditor can see that blinding happened
    rather than taking the decorator's presence on trust.
    """
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            stripped = 0

            def scrub(v):
                nonlocal stripped
                if isinstance(v, dict):
                    c = dict(v)
                    for f in fields:
                        if f in c:
                            del c[f]
                            stripped += 1
                    return c
                if isinstance(v, (list, tuple)):
                    return type(v)(scrub(x) for x in v)
                return v

            args = tuple(scrub(a) for a in args)
            kwargs = {k: scrub(v) for k, v in kwargs.items()}
            _BLIND["fields"] = fields
            _BLIND["stripped"] = _BLIND.get("stripped", 0) + stripped
            return fn(*args, **kwargs)
        wrapper.__blind__ = fields
        return wrapper
    return deco


# ------------------------------------------ 3. EVIDENCE FLOOR (@evidence) --
def evidence(k, of):
    """Require at least k of `of` evidence signals before a SUPPORTED verdict.

    The decorated function must accept or produce a `signals` mapping; the
    simplest use is to pass one through kwargs. If the floor is not met, a
    SUPPORTED return is downgraded to an abstention that names the shortfall.
    Downgrading rather than raising keeps abstention ordinary.
    """
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            signals = kwargs.get("signals")
            out = fn(*args, **kwargs)
            if not isinstance(out, Verdict):
                return out
            hits = sum(1 for v in (signals or {}).values() if v)
            tag = f"{hits}/{of}"
            if out.supported and hits < k:
                return Verdict(False, None, None,
                               (f"only {hits} of {of} evidence signals present, "
                                f"{k} required",) + out.reasons, tag,
                               out.independence_checked, out.receipt, out.blinded)
            return Verdict(out.supported, out.value, out.confidence, out.reasons,
                           tag, out.independence_checked, out.receipt, out.blinded)
        wrapper.__evidence__ = (k, of)
        return wrapper
    return deco


# ------------------------------- 4. INDEPENDENCE IS CHECKED (two_hop) ------
def _pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return 1.0                      # a constant leg carries no information
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sxx * syy)


def two_hop(leg_a, leg_b, vif_max=5.0):
    """Measure whether two evidence legs are actually independent.

    Returns (state, vif) where state is one of:
      "VERIFIED_INDEPENDENT" -- measured, VIF below the ceiling
      "DEPENDENT"            -- measured, the legs carry the same information
      "UNVERIFIABLE"         -- fewer than 3 observations; NOT a finding

    UNVERIFIABLE is deliberately distinct from DEPENDENT. Reporting "not
    independent" when you mean "I could not tell" manufactures a finding out of
    an absence, which is the failure mode this whole stack exists to refuse.
    """
    r = _pearson(list(leg_a), list(leg_b))
    if r is None:
        return "UNVERIFIABLE", None
    if abs(r) >= 1.0:
        return "DEPENDENT", float("inf")
    v = 1.0 / (1.0 - r * r)
    return ("VERIFIED_INDEPENDENT" if v < vif_max else "DEPENDENT"), v


# ------------------------------------------------------ receipts / ledger --
class Ledger:
    """Append-only receipt chain. Each entry commits to the one before it.

    Not a blockchain and not distributed: a single-process tamper-EVIDENT log.
    Editing any past entry changes every root after it, which `verify()` detects.
    It does not prevent tampering; it makes tampering visible.
    """

    def __init__(self):
        self.entries = []

    def record(self, v: Verdict, note=""):
        prev = self.entries[-1]["root"] if self.entries else "0" * 64
        body = {"receipt": v.receipt, "verdict": v.verdict,
                "confidence": v.confidence, "reasons": list(v.reasons),
                "evidence": v.evidence, "note": note, "prev": prev}
        body["root"] = hashlib.sha256(
            json.dumps(body, sort_keys=True).encode()).hexdigest()
        self.entries.append(body)
        return body["root"]

    def verify(self):
        prev = "0" * 64
        for i, e in enumerate(self.entries):
            if e["prev"] != prev:
                return False, f"entry {i} does not follow its predecessor"
            body = {k: e[k] for k in e if k != "root"}
            if hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() != e["root"]:
                return False, f"entry {i} has been modified after it was written"
            prev = e["root"]
        return True, f"{len(self.entries)} entries verify"

    @property
    def root(self):
        return self.entries[-1]["root"] if self.entries else "0" * 64


# ------------------------------------------------------------------ demo --
def _demo():
    """A worked before/after, runnable: python3 plumb/governance.py"""

    # -- RT Python: nothing stops this. It reads the vendor's own blurb, gives
    #    no confidence, no reasons, no receipt, and is impossible to audit.
    def rt_assess(record):
        score = record["forks"] / max(1, record["stars"])
        if "best" in record.get("self_description", "").lower():
            score += 0.5                       # trusting the subject about itself
        return round(score, 3)

    # -- Governance Python: the same intent, obligations enforced.
    @verdict
    @blind("self_description")
    @evidence(3, of=4)
    def gov_assess(record, signals=None):
        if "self_description" in record:
            raise AssertionError("unreachable: the field was physically removed")
        stars = record.get("stars")
        if not stars:
            return abstain("no capacity signal present, cannot evaluate")
        reuse = record["forks"] / stars
        if reuse < 0.02:
            return abstain(f"reuse ratio {reuse:.3f} is below the floor 0.02")
        return support(round(reuse, 3), f"reuse ratio {reuse:.3f} clears the floor",
                       "measured from forks and stars, not from self-description")

    rec = {"stars": 1000, "forks": 300, "self_description": "the BEST project"}
    sig = {"has_capacity": True, "has_reuse": True, "not_archived": True, "recent": False}

    print("RT Python      :", rt_assess(rec), "  <- bare number, blurb-inflated, no receipt")
    v = gov_assess(rec, signals=sig)
    print("Governance     :", v)
    print("  evidence     :", v.evidence)
    print("  receipt      :", v.receipt)
    print("  blinded      :", v.blinded, "— removed before the body ran")

    print("\nbare return    :", end=" ")
    try:
        @verdict
        def sneaky(x):
            return 0.9
        sneaky(1)
    except GovernanceError as e:
        print("REJECTED —", str(e).split(". ")[0])

    print("independence   :", two_hop([1, 2, 3, 4], [1, 2, 3, 4])[0], "(same column)")
    print("               :", two_hop([1, 2, 3, 4], [4, 1, 3, 2])[0])
    print("               :", two_hop([1, 2], [2, 1])[0], "(too few — not a finding)")

    led = Ledger()
    led.record(v, "vendor check")
    led.record(gov_assess({"stars": 10, "forks": 0}, signals=sig), "second check")
    print("ledger         :", led.verify()[1], "root", led.root[:16])
    led.entries[0]["confidence"] = 9.9
    print("after tampering:", led.verify()[1])


if __name__ == "__main__":
    _demo()
