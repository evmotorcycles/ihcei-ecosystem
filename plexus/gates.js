/* gates.js -- do your gates cover every outcome? KERNEL: no interface.
 * ===========================================================================
 * A pre-registration exists to remove judgement AFTER the data arrives. It only
 * does that if its gates partition the whole outcome space. If some result
 * falls in a gap between them, the gap is exactly where post-hoc reasoning
 * walks in -- and it walks in wearing the authority of a locked file.
 *
 * THE DEFECT THIS WAS BUILT FROM, FOUND IN A REAL PROTOCOL
 * A hypothesis claimed "at least 20% of load-bearing dependencies are abandoned
 * or single-maintainer". Its gate read "if fewer than 10%, the hypothesis
 * fails". Both look careful. Together they say nothing at all about a measured
 * 15%: too low to support a claim of 20%, too high to trigger the stated
 * failure. One number in six has no verdict, and it is the middle one -- the
 * region a real result is most likely to land in.
 *
 * WHAT THIS CHECKS AND WHAT IT CANNOT
 * It checks NUMERIC coverage: given what a hypothesis claims and what its gate
 * fails on, is there a range with no verdict? That is arithmetic.
 *
 * It cannot check whether the gate measures the thing the hypothesis is about.
 * A gate can partition the space perfectly and still be pointed at the wrong
 * quantity, and no amount of interval arithmetic will notice. That one needs a
 * reader.
 */
(function (root) {
  "use strict";

  /* ">= 0.20", "< 0.10", "> 3", "<= 0.5" -> { op, value } */
  function parse(s) {
    var m = /^\s*(>=|<=|>|<)\s*([0-9.]+)\s*$/.exec(String(s || ""));
    if (!m) return null;
    return { op: m[1], value: parseFloat(m[2]) };
  }

  function holds(cond, x) {
    if (cond.op === ">=") return x >= cond.value;
    if (cond.op === ">") return x > cond.value;
    if (cond.op === "<=") return x <= cond.value;
    return x < cond.value;
  }

  /* Sample the space finely enough to find any gap whose width is above tol.
     Deliberately a sweep rather than interval algebra: the conditions are
     simple, the space is one-dimensional, and a sweep cannot be wrong about a
     case it actually evaluated. */
  function coverage(spec, opts) {
    var o = opts || {};
    var lo = o.lo === undefined ? 0 : o.lo;
    var hi = o.hi === undefined ? 1 : o.hi;
    var steps = o.steps === undefined ? 20001 : o.steps;

    var supports = parse(spec.supportsIf);
    var fails = parse(spec.failsIf);
    if (!supports || !fails) {
      return { ok: false, why: ["supportsIf and failsIf must each read like " +
                                "'>= 0.20' or '< 0.10'"] };
    }

    var gaps = [], both = [], i, x, s, f, inGap = false, gapStart = 0;
    var step = (hi - lo) / (steps - 1);
    for (i = 0; i < steps; i++) {
      x = lo + i * step;
      s = holds(supports, x);
      f = holds(fails, x);
      if (s && f) both.push(x);
      if (!s && !f) {
        if (!inGap) { inGap = true; gapStart = x; }
      } else if (inGap) {
        gaps.push([gapStart, x - step]);
        inGap = false;
      }
    }
    if (inGap) gaps.push([gapStart, hi]);

    var width = gaps.reduce(function (a, g) { return a + (g[1] - g[0]); }, 0);
    return {
      ok: true, why: [],
      id: spec.id,
      supportsIf: spec.supportsIf, failsIf: spec.failsIf,
      gaps: gaps.map(function (g) {
        return { from: Math.round(g[0] * 1e6) / 1e6, to: Math.round(g[1] * 1e6) / 1e6 };
      }),
      uncoveredWidth: Math.round(width * 1e6) / 1e6,
      uncoveredShare: Math.round((width / (hi - lo)) * 1e6) / 1e6,
      contradicts: both.length > 0,
      partitions: gaps.length === 0 && both.length === 0,
      says: gaps.length === 0 && both.length === 0
        ? "Every outcome has a verdict."
        : both.length
          ? "Some outcomes both support and fail it. The gate contradicts the hypothesis."
          : "There are outcomes with no verdict. That gap is where a decision " +
            "gets made after the data arrives, under a locked file's authority.",
    };
  }

  var API = { coverage: coverage, parse: parse, holds: holds };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.GATES = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
