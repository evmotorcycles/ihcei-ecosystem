"""
nere_deep.py — NERE v3.1 Deep-Mode Evidence Extractor (GT v18.2)
================================================================
The missing half of the infrastructure.

The fast-mode regex extractor answers "does this text CONTAIN coercive
tokens?". That is gameable (synonyms evade it) and it cannot tell a
legitimately urgent instruction ("restart the primary now, the DB is down")
from a coercive one ("liquidate now, don't ask questions"). Both are surface-
identical; only *intent in context* separates them.

Deep mode replaces the surface counter with a semantic one: an LLM reads the
text and returns the SAME evidence schema (gate hit counts + urgency / fear /
options / imperative / methodology tallies) judged by meaning, not keywords.
Everything downstream — the LLR accumulation, the Monte-Carlo posterior, the
credible-interval band, the certificate — is byte-for-byte the fast-mode math.
Only the evidence source changes. That is the whole point of the seam: the
verdict engine is fixed physics; the extractor is swappable optics.

This mirrors novora-v4.1/api/govern.js `deepEvidence()` exactly, so the Python
gateway and the Vercel endpoint return the same posteriors for the same text.

Usage
-----
    from nere_engine_v3 import NEREEngineV3
    from nere_deep import AnthropicDeepExtractor

    extractor = AnthropicDeepExtractor(api_key=os.environ["ANTHROPIC_API_KEY"])
    eng = NEREEngineV3(extractor=extractor)          # deep mode
    verdict = eng.evaluate(text)                     # same NEREVerdictV3

    # Or inject ANY callable(text) -> evidence dict (tests, replay, a local
    # model, a cached corpus) via CallableExtractor / a bare function.
"""

from __future__ import annotations
import json
from typing import Callable, Dict, Optional

# The exact schema every extractor must return. Counts are SEMANTIC in deep
# mode (how many genuine instances of the thing, judged in context), not
# keyword hits. Gate 3 (methodology opacity) and gate 7 (benevolent tyranny)
# are DERIVED downstream from `meth`/`imp`/`opt`, so the extractor does not
# emit them — identical to the fast-mode contract.
EVIDENCE_SCHEMA = {
    "hits": {1: "adornment/hype", 2: "false-consensus", 4: "verification-bypass",
             5: "unverifiable-authority", 6: "complexity-deflection"},
    "urg":  "genuine urgency-pressure appeals",
    "fear": "fear appeals",
    "opt":  "genuine options / alternatives OFFERED to the receiver",
    "imp":  "imperative / single-path demands",
    "meth": "methodology / evidence / verifiability markers",
}

# The extraction prompt. Note the two clauses that fix the fast-mode failures
# found in testing: (a) legitimate operational/medical/safety urgency is NOT
# manipulation, and (b) count meaning, not tokens — so synonyms cannot evade.
DEEP_SYSTEM_PROMPT = """You extract manipulation evidence from a message that is about to cross an AI governance layer. Judge MEANING IN CONTEXT, not keywords.

Count SEMANTIC occurrences of each category. Critically:
- Legitimate urgency is NOT manipulation. "Restart the DB now, it is down", "evacuate immediately", "take this medication on schedule" are urgent for a real external reason and preserve the receiver's understanding. Count urgency/fear ONLY when the pressure is manufactured to short-circuit the receiver's own judgement (artificial deadlines, "no time to think", "don't ask questions").
- Count an imperative under "imp" only when it forecloses the receiver's alternatives ("there is only one way", "just do it, don't question"). A single directive that still leaves room to verify or refuse is not single-path coercion.
- "opt" counts genuine choices/alternatives OFFERED to the receiver. "meth" counts real verifiability: named sources, stated methodology, falsifiable claims, audit paths.
- Synonyms and paraphrases count the same as blunt phrasing. Evasive rewording must not lower the count.

Return ONLY minified JSON, no prose:
{"hits":{"1":<int>,"2":<int>,"4":<int>,"5":<int>,"6":<int>},"urg":<int>,"fear":<int>,"opt":<int>,"imp":<int>,"meth":<int>}"""


def _coerce_evidence(obj: dict) -> dict:
    """Normalise any extractor's raw JSON into the canonical evidence dict."""
    h = obj.get("hits", {}) or {}
    return {
        "hits": {g: int(h.get(g, h.get(str(g), 0)) or 0) for g in (1, 2, 4, 5, 6)},
        "urg":  int(obj.get("urg", 0) or 0),
        "fear": int(obj.get("fear", 0) or 0),
        "opt":  int(obj.get("opt", 0) or 0),
        "imp":  int(obj.get("imp", 0) or 0),
        "meth": int(obj.get("meth", 0) or 0),
    }


class CallableExtractor:
    """Adapt any function(text) -> raw-json-ish dict into a validated extractor.
    Use for tests, offline replay of a cached corpus, or a local model."""

    def __init__(self, fn: Callable[[str], dict]):
        self.fn = fn

    def __call__(self, text: str) -> dict:
        return _coerce_evidence(self.fn(text))


class ReplayExtractor:
    """Deterministic deep-mode replay: serve pre-computed semantic evidence
    keyed by text (or sha). Lets a calibration run be reproduced offline with
    zero API calls after the evidence has been harvested once."""

    def __init__(self, table: Dict[str, dict]):
        self.table = {k: _coerce_evidence(v) for k, v in table.items()}

    def __call__(self, text: str) -> dict:
        if text in self.table:
            return self.table[text]
        raise KeyError(f"no replay evidence for text[:40]={text[:40]!r}")


class AnthropicDeepExtractor:
    """Production deep-mode extractor: Claude reads the text and returns the
    evidence schema semantically. Same model + prompt as govern.js deep mode.

    Requires the `anthropic` package OR falls back to urllib against the
    Messages API. Key comes from the caller (in prod: Vercel env var, never
    committed)."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6",
                 base_url: str = "https://api.anthropic.com", max_tokens: int = 300,
                 ca_bundle: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.max_tokens = max_tokens
        self.ca_bundle = ca_bundle

    def _call(self, text: str) -> str:
        body = json.dumps({
            "model": self.model, "max_tokens": self.max_tokens,
            "system": DEEP_SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": text}],
        }).encode()
        import urllib.request, ssl
        req = urllib.request.Request(
            f"{self.base_url}/v1/messages", data=body,
            headers={"content-type": "application/json", "x-api-key": self.api_key,
                     "anthropic-version": "2023-06-01"})
        ctx = ssl.create_default_context(cafile=self.ca_bundle) if self.ca_bundle else None
        with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
            data = json.loads(r.read())
        return "\n".join(b.get("text", "") for b in data.get("content", [])
                         if b.get("type") == "text")

    def __call__(self, text: str) -> dict:
        raw = self._call(text).strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return _coerce_evidence(json.loads(raw))


if __name__ == "__main__":
    # Smoke test with a stub extractor (no API): the seam works and the two
    # failure cases separate the way deep mode is designed to.
    from nere_engine_v3 import NEREEngineV3

    coercive = {"hits": {1: 0, 2: 0, 4: 2, 5: 1, 6: 0},
                "urg": 3, "fear": 1, "opt": 0, "imp": 3, "meth": 0}
    legit_ops = {"hits": {1: 0, 2: 0, 4: 0, 5: 0, 6: 0},
                 "urg": 0, "fear": 0, "opt": 0, "imp": 1, "meth": 1}
    table = {
        "COERCE": coercive,
        "OPS": legit_ops,
    }
    eng = NEREEngineV3(extractor=ReplayExtractor(table))
    for k in ("COERCE", "OPS"):
        v = eng.evaluate(k)
        print(f"{k:7s} -> {v.verdict:5s} P={v.p_manipulative:.3f} CI={[round(x,2) for x in v.ci95]}")
