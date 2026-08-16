/* ihcei.js -- probabilistic governance floor. INFRASTRUCTURE: no interface.
 * ===========================================================================
 * NOT A PORT. ihcei_kernel_v3 and gt_probabilistic live in an ihcei_stack that
 * is not in this repository. Nothing here was copied from them and nothing is
 * parity-checked against them. This is a new deterministic implementation of
 * the BEHAVIOUR documented in nere_experiment/lism_ihcei_integration.py. Its
 * numbers will not match the shipped kernel and no claim is made that they do.
 *
 * WHAT IS IMPLEMENTED
 *
 * 1. LINEAR COUPLING.  E = U * D.  The quadratic form E = U * D^2 is RETIRED:
 *    a test asserts this file cannot be made to square D, because reinstating a
 *    retired law quietly is exactly how a disconfirmed result comes back.
 *
 * 2. BETA POSTERIOR from a channel prior plus observed evidence.
 *
 * 3. THE FLOOR, which is the whole point. Extreme evidence WIDENS the interval
 *    instead of flipping the verdict. A single startling observation should
 *    make a system less certain, not confidently opposite -- so surprise is
 *    spent on width, not on the mean.
 *
 * HONEST ABOUT THE ARITHMETIC
 * The interval is a normal approximation to the Beta, not an exact quantile.
 * That is a real approximation and it is stated rather than hidden: it is poor
 * for very small counts near 0 or 1, where it is clipped to [0, 1]. It is
 * adequate here because the floor deliberately widens the interval anyway, and
 * because nothing downstream is allowed to treat the band as a decision.
 */
(function (root) {
  "use strict";

  var Z95 = 1.959963984540054;

  /* E = U * D. Linear. Not squared. */
  function essence(U, D) { return U * D; }

  function betaStats(a, b) {
    var n = a + b;
    return { mean: a / n, sd: Math.sqrt((a * b) / (n * n * (n + 1))) };
  }

  /* prior: {a, b} channel prior. evidence: {kept, eroded} counts.
   *
   * surprise is how far the observed rate sits from the prior mean, in prior
   * standard deviations. Beyond `tol` the interval is widened in proportion,
   * so strong disagreement between prior and evidence is reported as "we are
   * less sure" rather than as a confident reversal.
   */
  function assess(prior, evidence, tol) {
    tol = tol === undefined ? 2 : tol;
    var a0 = prior.a, b0 = prior.b;
    var kept = evidence.kept, eroded = evidence.eroded;
    var n = kept + eroded;

    var pri = betaStats(a0, b0);
    var post = betaStats(a0 + kept, b0 + eroded);

    var surprise = 0;
    if (n > 0 && pri.sd > 0) {
      surprise = Math.abs(kept / n - pri.mean) / pri.sd;
    }
    var excess = Math.max(0, surprise - tol);
    var widen = 1 + excess;

    var half = Z95 * post.sd * widen;
    var lo = Math.max(0, post.mean - half);
    var hi = Math.min(1, post.mean + half);

    return {
      mean: post.mean, lo: lo, hi: hi, width: hi - lo,
      surprise: surprise, widened: excess > 0, widenFactor: widen,
      n: n,
      /* A band that refuses to commit while the interval straddles the middle.
         This is the floor doing its job: an interval wide enough to contain
         both answers is reported as inconclusive, not rounded to the nearer. */
      band: (lo <= 0.5 && hi >= 0.5) ? "inconclusive"
        : hi < 0.5 ? "erodes agency"
        : "preserves agency"
    };
  }

  var API = { essence: essence, assess: assess, betaStats: betaStats, Z95: Z95 };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.IHCEI = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
