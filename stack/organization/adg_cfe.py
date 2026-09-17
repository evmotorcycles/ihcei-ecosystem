"""Organization-graph telemetry. Layer 1, correlational, cohort-relative.

A faithful rename of the arithmetic in `adg-tqg/experiment.py`, with engineering
parameter names. Tradition vocabulary never appears here; it is reachable only
through `ncu/adapter.py` for display.

WHAT THESE NUMBERS ARE NOT, in the same size type as what they are
==================================================================
  * NOT a property of a repository. Every input is min-max normalised WITHIN
    this cohort, and kappa and the quartile bound are order statistics of it. A
    score is a property of a repository IN THIS LIST. Change the list and the
    score changes.
  * NOT causal. A high score does not make a project survive. The labels come
    from push dates; no score influenced them.
  * NOT a health grade. `aligned` means the alignment cosine sits above the
    cohort median. That is a position in a list, not a verdict.
  * NOT free of the cohort. Every emitted reading carries the cohort hash, and
    the hash is computed from the fixture BYTES -- a typed hash cannot enter.

WHY DISSONANCE DOES NOT USE PUSH DATES
======================================
The fixture's label rule is `E = 0 iff archived or days_since_push > 365`. A
dissonance built from push recency would therefore be a function of the label,
and any separation it showed would be partly tautological. The original states
this in its own header: "push-date/archived are NOT inputs to A_n or C_dev".
`leaky_dissonance` exists ONLY so the leakage can be measured and reported; it
is never used by `adg_score` or by the renderer.
"""

from __future__ import annotations

import hashlib
import math

#: labels name what was measured. A top-quartile say-do gap is a gap, and
#: calling it "chaos" would overstate it -- the same rule that demoted Foster
#: from "health" to an assembly check.
LABEL_ALIGNED = "aligned"
LABEL_MISALIGNED = "misaligned"
LABEL_HIGH_DISSONANCE = "high_dissonance"

PROBE_MARK = "+probe:"


class CohortHashError(ValueError):
    pass


def cohort_hash_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def minmax(xs):
    """Bit-identical to adg-tqg/experiment.py: a flat column reads 0.5."""
    lo, hi = min(xs), max(xs)
    return [(x - lo) / (hi - lo) if hi > lo else 0.5 for x in xs]


def cosine_to_ones(v):
    n = len(v)
    num = sum(v)
    den = math.sqrt(sum(x * x for x in v)) * math.sqrt(n)
    return num / den if den > 0 else 0.0


def _z(xs):
    m = sum(xs) / len(xs)
    var = sum((x - m) ** 2 for x in xs) / len(xs)
    s = math.sqrt(var)
    return [(x - m) / s for x in xs] if s > 0 else [0.0] * len(xs)


class Cohort:
    """The list a score is relative to. The hash comes from the file, not a caller."""

    def __init__(self, records, fixture_path, _probe_count: int = 0):
        if not records:
            raise ValueError("an empty cohort has nothing to normalise against")
        self.hash = cohort_hash_of(fixture_path)
        if _probe_count:
            # a probe reading can never be mistaken for a fixture reading
            self.hash = f"{self.hash}{PROBE_MARK}{_probe_count}"
        self.records = list(records)

        self.utility = minmax([math.log1p(r["stargazers"]) for r in self.records])
        self.d_dec = minmax([math.log1p(r["n_closed"]) for r in self.records])
        self.d_enc = minmax([1.0 / (1.0 + r["tau_v"]) for r in self.records])
        self.noise = minmax([r["tau_v"] for r in self.records])

        self.phi = [(self.utility[i], self.d_dec[i], self.d_enc[i])
                    for i in range(len(self.records))]
        self._alignment = [cosine_to_ones(p) for p in self.phi]

        # sorted()[n//2], NOT a mean of the two middle values. On n=22 those
        # differ -- 0.861235 against 0.844392 -- and records between them would
        # render on opposite sides.
        self.kappa = sorted(self._alignment)[len(self._alignment) // 2]

        #: say-do gap: adoption against responsiveness. Chosen columns; another
        #: pair is another quantity with the same name. Carries NO push input.
        self.dissonance = [abs(a - b) for a, b in zip(
            _z([math.log1p(r["stargazers"]) for r in self.records]),
            _z([-math.log1p(r["tau_v"]) for r in self.records]))]
        self.quartile_bound = self._quantile(self.dissonance, 0.75)

    @staticmethod
    def _quantile(xs, q):
        s = sorted(xs)
        if len(s) == 1:
            return s[0]
        pos = q * (len(s) - 1)
        lo = int(math.floor(pos))
        hi = min(lo + 1, len(s) - 1)
        return s[lo] + (s[hi] - s[lo]) * (pos - lo)

    def alignment(self, i=None):
        return self._alignment if i is None else self._alignment[i]

    def leaky_dissonance(self):
        """NOT used by any shipped reading. Exists so the leakage is measurable.

        Built from push recency, which is what the label rule is built from, so
        any separation it shows is partly a restatement of the label.
        """
        return [abs(a - b) for a, b in zip(
            _z([float(r["days_since_push"]) for r in self.records]),
            _z([-math.log1p(r["tau_v"]) for r in self.records]))]

    def survived(self, i) -> bool:
        r = self.records[i]
        return not (r.get("archived") or r.get("days_since_push", 0) > 365)

    def with_probe(self, record, fixture_path):
        """Append a synthetic record. The hash changes, so the reading is marked."""
        return Cohort(self.records + [record], fixture_path,
                      _probe_count=self.hash.count(PROBE_MARK) + 1)


def adg_score(cohort: Cohort, i: int, eps: float) -> dict:
    """alignment * (utility * d_dec) / (eps + noise). Carries the cohort hash."""
    if eps is None:
        raise TypeError("eps required; there is no default worth inheriting")
    value = (cohort.alignment(i) * (cohort.utility[i] * cohort.d_dec[i])
             / (eps + cohort.noise[i]))
    return {"value": float(value), "cohort_hash": cohort.hash,
            "cohort_relative": True}


def cfe_render(cohort: Cohort, i: int) -> dict:
    """A position in a list, not a verdict. Carries the cohort hash."""
    if cohort.dissonance[i] > cohort.quartile_bound:
        label = LABEL_HIGH_DISSONANCE
    elif cohort.alignment(i) > cohort.kappa:
        label = LABEL_ALIGNED
    else:
        label = LABEL_MISALIGNED
    return {"label": label, "cohort_hash": cohort.hash, "cohort_relative": True}
