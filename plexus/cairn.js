/* cairn.js -- the verification engine. INFRASTRUCTURE: no interface.
 * ===========================================================================
 * Cairn answers "what does this rest on?" with a structure, never with a
 * paragraph. It runs the already-tested engines -- bearings and sound from
 * plexus/engines.js, parity-checked against spar/ and fathom/ -- and returns
 * their numbers. It generates no text about the world and has no model in it.
 *
 * THE FIREWALL, WHICH IS THE WHOLE DESIGN
 * Two different measurements are made here and they are NEVER combined:
 *
 *   STRUCTURE  (Layer 1)  what the claim rests on, from the graph a person
 *                         entered. Measured. Reproducible. Says nothing about
 *                         whether any source is true.
 *   RHETORIC   (screen)   whether the wording leans on the reader. Lexical.
 *                         Says nothing about whether the claim is true either.
 *
 * A single "credibility score" fusing the two would be the most saleable thing
 * this file could produce and the most dishonest. Text that hands judgement
 * back can still rest on one unverified blog post; text full of pressure can be
 * perfectly sound. They are reported side by side, and `combined` is absent on
 * purpose -- a test asserts no such field is ever added.
 *
 * WHAT CAIRN CANNOT DO
 * It cannot tell you a claim is true. It knows only the sources you listed and
 * the links you drew. If two sources secretly share an origin you did not
 * enter, it will report them as independent, and it will be wrong.
 */
(function (root) {
  "use strict";

  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);
  var NERE = root.NERE || (typeof require === "function" ? require("./nere.js") : null);
  var IHCEI = root.IHCEI || (typeof require === "function" ? require("./ihcei.js") : null);

  /* A weak, deliberately uninformative channel prior. Beta(1,1) is uniform: it
     asserts nothing about the channel before evidence arrives, which is the
     right default when the "channel" is an arbitrary page someone pasted. */
  function defaultPrior() { return { a: 1, b: 1 }; }

  /* Split pasted text into candidate lines a person can mark up. Deterministic
     and dumb on purpose: it does not decide what a claim IS, it only breaks the
     text where a reader would. Nothing is measured until a person says which
     lines are sources and how they connect. */
  function lines(text) {
    return String(text || "")
      .split(/[\n\r]+|(?<=[.!?])\s+/)
      .map(function (s) { return s.trim(); })
      .filter(function (s) { return s.length > 0; });
  }

  function verify(spec) {
    var parts = spec.parts || [];
    var links = spec.links || [];
    var sources = spec.sources || [];
    var conclusion = spec.conclusion;

    var structure = null;
    if (parts.length >= 2 && links.length) {
      var bear = ENG.bearings(parts, links);
      var sound = ENG.sound(parts, links, sources, conclusion);
      structure = {
        parts: bear.parts, pieces: bear.pieces, total: bear.total,
        conserved: bear.conserved,
        soleRoutes: bear.links.filter(function (b) { return b.soleRoute; }).length,
        support: sound.support,
        deepest: sound.deepest,
        restsOnOneThread: sound.restsOnOneThread,
        remaining: sound.remaining,
        bySource: sound.bySource
      };
    }

    /* The screen runs on the words. Its counts ARE the evidence handed to the
       governance floor -- literal observed markers, not a threshold anyone
       picked. */
    var rhetoric = NERE.screen(spec.text || "");
    var agency = IHCEI.assess(
      spec.prior || defaultPrior(),
      { kept: rhetoric.discipline.length, eroded: rhetoric.pressure.length }
    );

    return {
      conclusion: conclusion,
      structure: structure,
      rhetoric: rhetoric,
      agency: agency,
      /* Said out loud in the payload, so anything rendering this cannot claim
         it was not told. */
      firewall: "structure and rhetoric are measured separately and never combined"
    };
  }

  var API = { verify: verify, lines: lines, defaultPrior: defaultPrior };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.CAIRN = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
