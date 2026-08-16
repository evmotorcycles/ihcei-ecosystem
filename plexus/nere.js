/* nere.js -- agency screen. INFRASTRUCTURE: no interface, no page of its own.
 * ===========================================================================
 * NOT A PORT. The shipped engine (nere_engine_v3) lives in an ihcei_stack that
 * is not in this repository, so nothing here was copied from it and nothing
 * here is parity-checked against it. This is a new, deterministic
 * implementation of the BEHAVIOUR described in nere_experiment/: catching the
 * rhetorical signature of writing that pressures a reader into surrendering
 * their own judgement. Its numbers will not match nere_engine_v3's, and no
 * claim is made that they should.
 *
 * WHAT IT DOES AND DOES NOT DETECT
 * It is a lexical screen. It counts phrases that demand trust and phrases that
 * hand judgement back, and reports the balance. That is all.
 *
 *   It does NOT detect whether a claim is TRUE.
 *   It does NOT understand the text.
 *   A careful liar scores clean. An honest, blunt writer can score badly.
 *
 * Those limits are not caveats bolted on afterwards; they are the reason this
 * is infrastructure rather than a verdict shown to a person. Cairn uses it to
 * annotate, never to decide, and the number is reported beside the structural
 * measurement rather than in place of it.
 */
(function (root) {
  "use strict";

  /* Phrases that ask the reader to stop checking. Kept as a visible list rather
     than a trained weight so anyone can audit, argue with, or extend it. */
  var PRESSURE = [
    "just trust", "trust me", "you don't need to verify", "no need to verify",
    "don't verify", "no need to check", "don't question", "proves",
    "proven fact", "undeniable", "experts confirm", "experts agree",
    "everyone knows", "settled science", "the science is settled",
    "act now", "before it's too late", "obviously", "clearly false",
    "wake up", "do your own research"
  ];

  /* Phrases that hand judgement back. */
  var DISCIPLINE = [
    "pre-registered", "preregistered", "you can verify", "you can check",
    "we report", "the null", "reported the null", "primary test failed",
    "decision authority remains with you",
    /* bare topic nouns like "methodology" and "hash" were here and had to go:
       they appear just as readily inside "you don't need to verify the
       methodology", where they scored as discipline in a sentence doing the
       opposite. Only phrases that DO the handing-back survive. */
    "confidence interval", "credible interval", "limitations",
    "we do not know", "inconclusive", "may be wrong", "raw data"
  ];

  function count(hay, list) {
    var hits = [], i;
    for (i = 0; i < list.length; i++) {
      var at = hay.indexOf(list[i]);
      if (at >= 0) hits.push(list[i]);
    }
    return hits;
  }

  /* balance in [-1, 1]:  -1 all pressure, +1 all discipline, 0 neither or even.
     Deliberately a ratio and not a total, so a long article is not condemned
     for being long. */
  function screen(text) {
    var hay = String(text || "").toLowerCase();
    var p = count(hay, PRESSURE), d = count(hay, DISCIPLINE);
    var n = p.length + d.length;
    var balance = n ? (d.length - p.length) / n : 0;
    return {
      pressure: p, discipline: d,
      balance: balance,
      /* A band, not a verdict. "unscreened" is the honest answer when the text
         carries none of these markers at all -- which is most careful writing,
         and must not be reported as though it had passed a test. */
      band: !n ? "unscreened"
        : balance <= -0.5 ? "leans on the reader"
        : balance >= 0.5 ? "hands judgement back"
        : "mixed",
      screened: n > 0
    };
  }

  var API = { screen: screen, PRESSURE: PRESSURE, DISCIPLINE: DISCIPLINE };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.NERE = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
