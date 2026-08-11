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



# ============================== CLAIM-TYPE ROUTER ==============================
# THE MOST IMPORTANT FIX FROM THE FIELD AUDITS.
# Audits showed ordinary users pasting dictionary definitions and getting a red
# 0/5 INSUFFICIENT_EVIDENCE. That is not a failed audit -- it is text the engine
# was never designed to audit, and reporting it as failure makes a correct system
# look broken. An empirical auditor must first ask "is this even an empirical
# claim?" and say OUT_OF_SCOPE when it is not.
CONCEPTUAL_RE = re.compile(
    r"(\bis (the|a|an) (study|branch|theory|field|concept|term|word|practice|process|state|quality)\b"
    r"|\bis defined as\b|\bmeans\b|\brefers to\b|\bdefinition of\b"
    r"|\bby definition\b|^\s*\w+\s*[:—-]\s*(the|a|an)\b)", re.I)
MATHY_RE = re.compile(r"^\s*[\d\s()+\-*/^=.]+\s*$")
OPINION_RE = re.compile(r"\b(i think|i believe|in my opinion|i feel|should be|ought to|is better than|is the best|is amazing|is terrible|prefer)\b", re.I)
QUESTION_RE = re.compile(r"^\s*(what|who|when|where|why|how|is|are|do|does|did|can|could|should|would|will)\b.*\?\s*$", re.I)
IMPERATIVE_RE = re.compile(r"^\s*(mix|add|combine|apply|take|use|heat|stir|install|run|pour|dissolve|blend)\b", re.I)

# Domains where STRUCTURAL soundness is NOT safety. The field audit that scored an
# un-emulsified glycolic-acid serum 3/5 is exactly why this exists: the claim was
# well-formed and chemically unstable at the same time.
DOMAIN_RISK = {
    "chemistry/formulation": re.compile(r"\b(acid|ph\b|emulsif|oil|solvent|dissolve|concentration|serum|formulation|mix(ing)?|bleach|ammonia)\b", re.I),
    # Widened after a coverage study found the original missed 61% of a sealed
    # set of health texts -- it fired on clinical vocabulary (dose, patient,
    # therapy) and missed infectious disease, mortality, oncology and
    # vaccination entirely, which is most of what ordinary people forward.
    # Written against the DEV split only; see safety-coverage/.
    "medical/health":        re.compile(
        r"\b(dose|dosage|mg\b|ml\b|supplement|treatment|symptom|diagnos|medication|serum"
        r"|skin|ingest|therapy|clinical trial|metabolic|nutrition|placebo|patient"
        r"|participants"
        # infectious disease and outbreaks
        r"|infect\w*|outbreak|epidemic|pandemic|bacteri\w*|virus|viral|fungal|parasit\w*"
        r"|contagio\w*|antibiotic|antimicrobial|pathogen\w*|contaminat\w*|quarantine"
        r"|measles|cholera|influenza|bird flu|covid"
        # mortality and severity
        r"|death[s]?|died|dying|fatal\w*|mortality|lethal|survive|survival|kill(s|ed)?"
        r"|life-threatening|amputat\w*|wound[s]?|illness|disease|disorder|syndrome"
        # oncology and chronic conditions
        r"|cancer|tumou?r|malignan\w*|biopsy|carcinom\w*|diabet\w*|blood pressure"
        r"|cholesterol|kidney|cardiac|stroke|asthma"
        # prevention and care
        r"|vaccin\w*|immunis\w*|immuniz\w*|booster|screening|hospital\w*|clinic\w*"
        r"|doctor|nurse|prescription|fever|nausea)\b", re.I),
    "legal/regulatory":      re.compile(
        r"\b(contract|clause|liabilit\w*|complian\w*|regulat\w*|statute|gdpr|licen[cs]e"
        r"|jurisdiction|appeal|waive[sd]?|legal|lawsuit|court|breach|terminat\w*"
        r"|disclos\w*|entitle\w*|tribunal)\b", re.I),
    "financial":             re.compile(
        r"\b(revenue|profit|forecast|invest\w*|valuation|roi\b|interest rate|loan|credit"
        r"|guaranteed returns?|returns? of|pension|tax|apr\b|mortgage|debt|refund"
        r"|deposit|payment|withdraw\w*)\b", re.I),
    "safety-critical":       re.compile(
        r"\b(voltage|electrical|structural|load-bearing|pressure|gas|flammable|dosing"
        r"|carbon monoxide|scaffold\w*|toxic|fumes|corrosive|explosi\w*|asbestos"
        r"|brake[s]?|overheat\w*|wiring|flue|ventilat\w*|pesticide|solvent)\b", re.I),
}


def classify_claim(text):
    """Route the input BEFORE auditing it. Returns (kind, human explanation).

    Only EMPIRICAL text is auditable. Everything else gets OUT_OF_SCOPE, which is a
    neutral outcome and must never be rendered as a failure.
    """
    t = (text or "").strip()
    if not t:
        return "EMPTY", "Nothing to look at yet."
    if QUESTION_RE.match(t):
        return "QUESTION", ("That's a question, not a claim. I audit statements — paste an answer "
                            "you've been given and I'll tell you how far it can be trusted.")
    if MATHY_RE.match(t):
        return "CONCEPTUAL", ("That's arithmetic. It's true by definition, so there's nothing for me "
                              "to verify against the world.")
    if CONCEPTUAL_RE.search(t) and not re.search(r"\d", t):
        return "CONCEPTUAL", ("That's a definition or a concept. Definitions are true by agreement, not "
                              "by measurement — so there's no source, date or figure for me to check. "
                              "This isn't a failure; it's simply outside what I audit.")
    if OPINION_RE.search(t):
        return "OPINION", ("That's a preference or a judgement. I can't audit what someone values — only "
                           "claims about what is measurably the case.")
    if IMPERATIVE_RE.match(t):
        return "INSTRUCTION", ("That's a set of instructions. I can check whether it's specified precisely "
                               "enough to follow — but NOT whether following it is safe or correct.")
    return "EMPIRICAL", ""


def domain_flags(text):
    """Domains where a good structural score does NOT mean the content is sound."""
    return [d for d, rx in DOMAIN_RISK.items() if rx.search(text or "")]


def next_steps(checks, kind):
    """Never hand back uncertainty without a concrete move (field-audit finding)."""
    if kind == "QUESTION":
        return ["Paste the answer you were given, and I'll audit that instead."]
    if kind in ("CONCEPTUAL", "OPINION"):
        return ["Add a measurement, a date or a source and it becomes something I can check.",
                "For definitions, an ordinary assistant or a dictionary is the right tool."]
    missing = [c for c in checks if not c["hit"]]
    fix = {"source": "Name where it came from — a study, a report, a link.",
           "figures": "Add the actual numbers.",
           "method": "Say how it was measured.",
           "time": "Add when it was measured.",
           "scope": "Say who or where it applies to."}
    return [fix[c["signal"]] for c in missing[:3]] or ["Nothing material is missing."]


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
    kind, kind_note = classify_claim(text)
    checks = score_evidence(text)
    hits = sum(1 for c in checks if c["hit"])
    words = len(text.split()) if text else 0
    amb = detect_ambiguity(text)
    impossible = check_impossible_assertion(text)
    domains = domain_flags(text)

    # OUT OF SCOPE is neutral, not a failure. This is the single biggest fix from
    # the field audits: a definition scoring 0/5 red made a correct system look broken.
    if kind in ("CONCEPTUAL", "OPINION", "QUESTION", "EMPTY"):
        rcpt = _sha((parent_receipt or "") + "|" + json.dumps({"t": text, "m": model, "v": "OUT_OF_SCOPE"}, sort_keys=True))
        return {
            "input": text, "model": model, "verdict": "OUT_OF_SCOPE", "claim_type": kind,
            "committed_answer": None, "confidence": None, "band": "not applicable",
            "evidence": [], "evidence_hits": 0, "evidence_total": len(EVIDENCE),
            "ambiguity": amb, "implausible": None, "domain_flags": domains,
            "explanation": kind_note, "question": None,
            "next_steps": next_steps(checks, kind),
            "receipt": rcpt, "parent_receipt": parent_receipt, "abstained": False,
            "engine": "cairn-ei/1.1 (python)",
            "limits": "Out of scope is not a failure. I audit empirical claims; this text is not one.",
        }

    conf = hits / len(EVIDENCE)
    if words < 4:
        conf = 0.0
    if model in ("granite", "quartz"):
        conf = min(1.0, conf * 1.12)
    if amb["ambiguous"]:
        conf = min(conf, 0.35)

    if amb["ambiguous"]:
        verdict, committed = "AMBIGUOUS", None
        question = (f"Which did you mean: were you {amb['participle']}, "
                    f"or was the {amb['object']} {amb['participle']}?")
    elif impossible:
        verdict, committed = "IMPLAUSIBLE", None
        question = "Did you mean this literally, or is a word missing?"
    elif conf < 0.25:
        verdict, committed = "INSUFFICIENT_EVIDENCE", None
        question = "Add a source, a figure, a date, a method or a scope and I can work with it."
    else:
        verdict, committed = "SUPPORTED", text
        question = None

    band = ("high" if conf >= 0.7 else "moderate" if conf >= 0.45
            else "low" if conf >= 0.25 else "insufficient")
    rcpt = _sha((parent_receipt or "") + "|" + json.dumps({"t": text, "m": model, "v": verdict}, sort_keys=True))

    return {
        "input": text, "model": model, "verdict": verdict, "claim_type": kind,
        "committed_answer": committed, "confidence": round(conf, 3), "band": band,
        "evidence": checks, "evidence_hits": hits, "evidence_total": len(EVIDENCE),
        "ambiguity": amb, "implausible": impossible, "domain_flags": domains,
        "explanation": kind_note, "question": question,
        "next_steps": next_steps(checks, kind),
        "receipt": rcpt, "parent_receipt": parent_receipt,
        "abstained": verdict in ("AMBIGUOUS", "IMPLAUSIBLE", "INSUFFICIENT_EVIDENCE"),
        "engine": "cairn-ei/1.1 (python)",
        "limits": ("I check STRUCTURE, not subject-matter correctness, and I do not understand language. "
                   "A high score means the claim is well-specified enough to check — NOT that it is true, "
                   "safe or sound." +
                   (" Domain risk detected (" + ", ".join(domains) + "): a specialist must review the content itself."
                    if domains else "")),
    }


if __name__ == "__main__":
    import sys
    print(json.dumps(assay(" ".join(sys.argv[1:]) or "I saw the Grand Canyon flying to Chicago."), indent=2))
