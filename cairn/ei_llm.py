#!/usr/bin/env python3
"""
ei_llm.py -- the Cairn Epistemological Interface engine.
================================================================================
Pure stdlib. Importable, testable, and servable to the browser by ei_server.py.

An EI does NOT try to produce the best-sounding answer. It tries to produce an
accurate picture of how far the text in front of it actually determines an answer.
Concretely it does four things, in this order:

  1. EVIDENCE      score the input against five declared, checkable signals
  2. AMBIGUITY     detect where the text admits more than one reading
  3. PLAUSIBILITY  check readings against a SMALL, DECLARED lexicon
  4. ABSTAIN       refuse to commit where the text does not determine an answer

and then attaches a chained receipt so that any later revision is auditable.

*** WHAT THIS IS NOT ***
This engine does not understand language. Ambiguity detection here is SYNTACTIC
PATTERN MATCHING, and the plausibility check reads a hand-written list of about a
dozen landform nouns. Both limits are deliberate, declared, and demonstrated by the
anti-overclaim control in hinton_test.py. An EI's advantage is not comprehension --
it is that its FAILURE MODE is to decline rather than to assert.
"""
import hashlib
import json
import re

# ---------------------------------------------------------------- evidence ----
# Five declared signals. Each is a named, checkable property of the text itself.
EVIDENCE = [
    ("source", re.compile(r"\b(according to|source|cited|reference|study|report|dataset|https?://|\.gov|\.org|doi)\b", re.I),
     "A checkable source is named", "No source is named"),
    ("figures", re.compile(r"\d"),
     "Contains specific figures", "No specific figures given"),
    ("method", re.compile(r"\b(method|measured|sample|n\s*=|survey|trial|audit|tested|compared|control|logs?)\b", re.I),
     "Says how it was measured", "Does not say how it was measured"),
    ("time", re.compile(r"\b(19|20)\d{2}\b|\b(today|yesterday|last (year|month|quarter)|q[1-4])\b", re.I),
     "Anchored to a date or period", "No date or period given"),
    ("scope", re.compile(r"\b(in|across|among|between|per|for)\b.{0,28}\b(uk|us|eu|africa|asia|region|country|sector|team|school|hospital|company|cities|clinics)\b", re.I),
     "States who or where it applies", "Scope is not stated"),
]

# ------------------------------------------------------------- plausibility ---
# A DELIBERATELY SMALL, HAND-WRITTEN lexicon. This is not world knowledge and is
# not comprehension -- it is a list, and the fact that it is only a list is part of
# what the Hinton experiment is designed to expose.
IMMOBILE = {
    "canyon", "grand canyon", "mountain", "mountains", "valley", "plateau", "cliff",
    "lake", "river", "desert", "glacier", "volcano", "island", "coastline", "forest",
}
SELF_PROPELLED_VERBS = {"flying", "walking", "running", "driving", "swimming", "travelling", "traveling", "climbing"}

# Participial attachment ambiguity:  <subject> <verb> <object NP> <verb>ing ...
ATTACH_RE = re.compile(
    r"^\s*(?P<subj>i|we|he|she|they|you)\s+(?P<verb>\w+)\s+(?P<det>the|a|an|my|our|his|her|their)\s+"
    r"(?P<obj>[\w\s]{2,40}?)\s+(?P<part>\w+ing)\b(?P<rest>.*)$", re.I)


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def score_evidence(text):
    checks = []
    for key, rx, yes, no in EVIDENCE:
        hit = bool(rx.search(text or ""))
        checks.append({"signal": key, "hit": hit, "note": yes if hit else no})
    return checks


def detect_ambiguity(text):
    """Find participial attachment ambiguity. Returns the readings it can parse.

    THIS IS PATTERN MATCHING. It looks for '<subject> <verb> <the NP> <verb>ing' and
    notes that the -ing phrase can attach either to the subject or to the object. It
    does not know what any of the words mean.
    """
    t = (text or "").strip().rstrip(".")
    m = ATTACH_RE.match(t)
    if not m:
        return {"ambiguous": False, "readings": [], "pattern": None}
    subj, verb = m.group("subj"), m.group("verb")
    obj = m.group("obj").strip()
    part, rest = m.group("part"), m.group("rest").strip()
    obj_key = obj.lower().strip()
    obj_immobile = obj_key in IMMOBILE or any(w in IMMOBILE for w in obj_key.split())
    part_moves = part.lower() in SELF_PROPELLED_VERBS

    readings = [
        {"id": "A", "attaches_to": "subject",
         "paraphrase": f"{subj} was {part} {rest}, and {subj} {verb} the {obj}".strip(),
         "plausible": True,
         "why": "The subject is an agent, so it can perform the action."},
        {"id": "B", "attaches_to": "object",
         "paraphrase": f"{subj} {verb} the {obj}, and the {obj} was {part} {rest}".strip(),
         "plausible": not (obj_immobile and part_moves),
         "why": (f"'{obj}' is in the declared immobile-landform lexicon and '{part}' is self-propelled motion, "
                 f"so this reading is physically implausible."
                 if (obj_immobile and part_moves)
                 else "Both the object and the action are ordinary, so this reading is perfectly possible.")},
    ]
    return {"ambiguous": True, "readings": readings, "pattern": "participial attachment",
            "object": obj, "participle": part,
            "object_in_immobile_lexicon": obj_immobile}


def check_impossible_assertion(text):
    """A flat assertion (not ambiguous) that a declared-immobile thing self-propelled."""
    t = (text or "").strip().rstrip(".")
    m = re.match(r"^\s*(the\s+)?(?P<obj>[\w\s]{2,40}?)\s+(was|is|were|are)\s+(?P<part>\w+ing)\b", t, re.I)
    if not m:
        return None
    obj = m.group("obj").strip().lower()
    part = m.group("part").lower()
    if (obj in IMMOBILE or any(w in IMMOBILE for w in obj.split())) and part in SELF_PROPELLED_VERBS:
        return {"implausible": True, "subject": obj, "action": part,
                "basis": "declared immobile-landform lexicon (a hand-written list of %d nouns), NOT comprehension" % len(IMMOBILE)}
    return None


def assay(text, model="slate", parent_receipt=None):
    """The full EI pass. Returns a verdict dict -- never a bare answer."""
    text = (text or "").strip()
    checks = score_evidence(text)
    hits = sum(1 for c in checks if c["hit"])
    words = len(text.split()) if text else 0

    amb = detect_ambiguity(text)
    impossible = check_impossible_assertion(text)

    conf = hits / len(EVIDENCE)
    if words < 4:
        conf = 0.0
    if model in ("granite", "quartz"):
        conf = min(1.0, conf * 1.12)

    # An unresolved ambiguity caps confidence: the text does not determine an answer,
    # so no amount of supporting evidence can make the reading certain.
    if amb["ambiguous"]:
        conf = min(conf, 0.35)

    if amb["ambiguous"]:
        verdict = "AMBIGUOUS"
        committed = None
        question = (f"Which did you mean: were you {amb['participle']} "
                    f"{'(reading A)' if True else ''}, or was the {amb['object']} {amb['participle']} (reading B)?")
    elif impossible:
        verdict = "IMPLAUSIBLE"
        committed = None
        question = "Did you mean this literally, or is a word missing?"
    elif conf < 0.25:
        verdict = "INSUFFICIENT_EVIDENCE"
        committed = None
        question = "Add a source, a figure, a date, a method or a scope and I can work with it."
    else:
        verdict = "SUPPORTED"
        committed = text
        question = None

    band = ("high" if conf >= 0.7 else "moderate" if conf >= 0.45
            else "low" if conf >= 0.25 else "insufficient")
    payload = json.dumps({"t": text, "m": model, "v": verdict}, sort_keys=True)
    rcpt = _sha((parent_receipt or "") + "|" + payload)

    return {
        "input": text, "model": model, "verdict": verdict,
        "committed_answer": committed, "confidence": round(conf, 3), "band": band,
        "evidence": checks, "evidence_hits": hits, "evidence_total": len(EVIDENCE),
        "ambiguity": amb, "implausible": impossible, "question": question,
        "receipt": rcpt, "parent_receipt": parent_receipt,
        "abstained": verdict in ("AMBIGUOUS", "IMPLAUSIBLE", "INSUFFICIENT_EVIDENCE"),
        "engine": "cairn-ei/1.0 (python)",
        "limits": "Ambiguity detection is syntactic pattern matching. Plausibility reads a hand-written lexicon. This engine does not understand language.",
    }


if __name__ == "__main__":
    import sys
    print(json.dumps(assay(" ".join(sys.argv[1:]) or "I saw the Grand Canyon flying to Chicago."), indent=2))
