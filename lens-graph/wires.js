/* wires.js — the scaffold layer between a flat list and the graph engine.
 * ===========================================================================
 * The engine (lens-graph.js) is lifted verbatim and is not touched here. This
 * file answers one question the engine deliberately does not: WHEN IS THERE
 * ENOUGH DECLARED STRUCTURE THAT DRAWING A MESH TELLS THE USER ANYTHING?
 *
 * THE HAZARD THIS EXISTS TO STOP
 * A flat list of seven steps can always be drawn as a chain. It will look like
 * a structure, carry the cadence of one, and be a picture of nothing — the list
 * re-plotted. That is the similar-yet-dissimilar failure: the shape of a
 * measured thing, without the thing.
 *
 * TWO MEASURED FACTS SET THE GATES BELOW.
 *
 * 1. A STAR DEGENERATES. Five supports wired straight to one conclusion, equal
 *    weight, return dependence 0.200000 each — exactly 1/5. Wire the same five
 *    to each other instead and they separate to 0.333 / 0.333 / 0.333 / 0 / 0.
 *    So on a star the readout is arithmetic on the COUNT. It is what you get
 *    from counting to five, and rendering it as a finding would be hollow.
 *
 * 2. BEARINGS SUM TO parts − pieces, ALWAYS (Foster). Nothing here is a score
 *    anyone chose, and no wire can be made to look more important without
 *    another looking less. That is also why a total cannot be read as health.
 *
 * WHAT THIS CANNOT DO
 *   * It cannot tell whether a wire the user drew is REAL. Every wire is a
 *     declaration by a person; the engine audits the drawing, not the world.
 *   * A perfectly drawn mesh of wrong steps computes exactly like a perfectly
 *     drawn mesh of right ones.
 *   * It never reports "sound". Structure is not correctness.
 */
(function (root) {
  "use strict";

  var LMD = root.LMD, PLEXUS = root.PLEXUS;

  /* A mesh is worth drawing only when wires connect PARTS TO EACH OTHER.
   * `centreOnly` is the star case above: every wire lands on the same part. */
  function meshEarnsItsPlace(parts, wires, centre) {
    if (!wires || wires.length < 1) {
      return { draw: false, why: "nothing-declared" };
    }
    if (centre) {
      var offCentre = wires.filter(function (w) {
        return w[0] !== centre && w[1] !== centre;
      });
      if (!offCentre.length) {
        return { draw: false, why: "star", n: wires.length };
      }
    }
    return { draw: true, why: "ok" };
  }

  /* The sentence the screen shows when it refuses to draw. Ordinary words, and
   * it names what the person can DO next — the refusal opens the next move
   * rather than closing the question. */
  function refusal(state) {
    if (state.why === "nothing-declared") {
      return {
        head: "Nothing is holding anything up yet.",
        body: "These are steps on their own, not a structure. Pull a wire " +
              "between two of them — pick one that cannot start until another " +
              "comes back — and this will start showing what rests on what.",
        cta: "Add the first wire"
      };
    }
    if (state.why === "star") {
      return {
        head: "Every wire goes to the same place.",
        body: "With " + state.n + " wires all landing on one step, each one " +
              "carries exactly the same share — one " + state.n + "th. That is " +
              "counting, not structure. Wire two steps to EACH OTHER and there " +
              "will be something to see.",
        cta: "Wire two steps together"
      };
    }
    return null;
  }

  /* Bearings, with the ordinary-language reading attached. `soleRoute` is the
   * engine's own flag: nothing else does this job. */
  function readWires(parts, wires) {
    var b = PLEXUS.bearings(parts, wires);
    var rows = b.links.map(function (r) {
      var others = Math.max(1, Math.round(1 / r.bearing) - 1);
      return {
        i: r.i, from: r.from, to: r.to, bearing: r.bearing,
        kind: r.soleRoute ? "hold" : r.bearing < 0.25 ? "spare" : "share",
        say: r.soleRoute
          ? "Nothing else does this. Cut it and the pieces below come down."
          : "There " + (others === 1 ? "is 1 other way" : "are about " + others +
            " other ways") + " round this."
      };
    });
    return { rows: rows, total: b.total, parts: b.parts, pieces: b.pieces,
             expected: b.expected, conserved: b.conserved };
  }

  /* What comes down if this wire is cut — computed by REMOVAL, not by formula.
   * The mobile metaphor is only honest if the fall is actually measured. */
  function whatFalls(parts, wires, cutIndex, anchor) {
    var kept = wires.filter(function (_, i) { return i !== cutIndex; });
    var idx = {};
    parts.forEach(function (p, i) { idx[p] = i; });
    if (!kept.length) return parts.filter(function (p) { return p !== anchor; });
    var r = LMD.meshMetric(LMD.laplacianFromEdges(
      parts.length, kept.map(function (w) { return [idx[w[0]], idx[w[1]], w[2]]; })));
    var a = idx[anchor];
    return parts.filter(function (p, k) {
      return p !== anchor && (r.dead || !isFinite(r.D[a][k]));
    });
  }

  /* The weakest wire, for "cut the weakest". Weakest = smallest declared
   * strength, not smallest bearing: the person set the strength, so the person
   * can predict which one goes. */
  function weakest(wires) {
    var w = -1, best = Infinity;
    wires.forEach(function (x, i) { if (x[2] < best) { best = x[2]; w = i; } });
    return w;
  }

  /* THE LIMIT. Same size type as the promise, on every screen that draws. */
  var LIMIT =
    "This shows what rests on what, using only the wires you drew. A perfectly " +
    "drawn mesh of wrong steps looks exactly like a perfectly drawn mesh of " +
    "right ones. It cannot tell you whether any step is worth doing, or whether " +
    "anything you wrote down is true.";

  var API = { meshEarnsItsPlace: meshEarnsItsPlace, refusal: refusal,
              readWires: readWires, whatFalls: whatFalls, weakest: weakest,
              LIMIT: LIMIT };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.WIRES = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
