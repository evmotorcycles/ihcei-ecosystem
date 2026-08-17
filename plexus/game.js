/* game.js -- Quarry: a game whose map IS the metric. No interface here.
 * ===========================================================================
 * Every position on screen comes from the same LMD engine that reads a bill.
 * There is no level geometry: the dungeon is a graph, and where things are is
 * whatever sqrt(effective resistance) says they are.
 *
 * THE RULE THAT MAKES IT A GAME RATHER THAN A TOY
 * You hold a fixed amount of attention and split it between three things:
 * fighting, looting, and escaping. You win when the Portal is nearer to you
 * than the Boss is.
 *
 *     win  <=>  d(Player, Portal) < d(Player, Boss)
 *
 * That is a COMPARISON OF TWO MEASURED DISTANCES. No threshold was chosen, no
 * score was invented, and no difficulty number is tuned anywhere in this file.
 * The only constant is how much attention you have, which is the rule of the
 * game rather than a property of the world.
 *
 * WHY IT IS NOT TRIVIAL
 * Attention is conserved, so every point spent pulling the Portal closer is a
 * point not spent on the Boss -- but the dungeon graph is wired so that the
 * things you want are structurally tied to the things you do not. Looting drags
 * the Portal along with it; fighting drags the Minion. You are not moving
 * pieces, you are re-weighting a graph and living with what the arithmetic then
 * does to the space.
 *
 * A CLAIM I GOT WRONG, AND THE CORRECTION
 * I first wrote that spending evenly does nothing, because scaling every
 * coupling by the same number scales every distance by 1/sqrt(it) and changes
 * no comparison. That invariance is real -- it is the same one that makes
 * bearings sum to parts minus pieces however you scale the links -- but it does
 * NOT apply here, and a test caught it. An even spend scales only your three
 * attention edges; the dungeon's own ties stay where they are, so the ratio
 * between them moves and the world really does change shape. Measured: even
 * spends of 4/4/4 and 0.4/0.4/0.4 give a distance ratio of 1.9319, not the
 * sqrt(10) = 3.1623 that true global scaling would give.
 *
 * What IS true, and tested: scaling every link including the dungeon's changes
 * no comparison at all. And in this dungeon an even spend, at any size, never
 * flips the verdict -- but that is a measured fact about this wiring, not a
 * theorem, and it is asserted as a measurement.
 */
(function (root) {
  "use strict";

  var LMD = root.LMD || (typeof require === "function" ? require("../smi/lmd.js") : null);

  var PLAYER = "You", BOSS = "The Boss", LOOT = "The Hoard",
      PORTAL = "The Way Out", MINION = "A Minion", LORE = "A Stone";

  var CAST = [PLAYER, BOSS, LOOT, PORTAL, MINION, LORE];

  /* The dungeon, as it is wired before you look at anything. These are the ties
     you cannot spend your way out of; they are what makes the choice hard. */
  function bones() {
    return [
      [PLAYER, MINION, 1.0],
      [MINION, BOSS, 2.0],
      [BOSS, LOOT, 0.8],
      [LOOT, PORTAL, 0.5],
      [PLAYER, LORE, 0.4],
      [LORE, PORTAL, 0.4]
    ];
  }

  var BUDGET = 12;          /* how much attention you have. The one game rule. */
  var FLOOR = 0.05;         /* nothing is ever fully unlooked-at, or it strands */

  function clampSpend(spend) {
    var f = Math.max(FLOOR, spend.fight || 0);
    var g = Math.max(FLOOR, spend.greed || 0);
    var e = Math.max(FLOOR, spend.flee || 0);
    var tot = f + g + e;
    if (tot > BUDGET) { var s = BUDGET / tot; f *= s; g *= s; e *= s; }
    return { fight: f, greed: g, flee: e, spent: f + g + e };
  }

  function links(spend) {
    var s = clampSpend(spend);
    return bones().concat([
      [PLAYER, BOSS, s.fight],
      [PLAYER, LOOT, s.greed],
      [PLAYER, PORTAL, s.flee]
    ]);
  }

  function distances(spend) {
    var ls = links(spend), idx = {}, i;
    for (i = 0; i < CAST.length; i++) idx[CAST[i]] = i;
    var r = LMD.meshMetric(LMD.laplacianFromEdges(CAST.length,
      ls.map(function (l) { return [idx[l[0]], idx[l[1]], l[2]]; })));
    var out = {};
    CAST.forEach(function (n) { out[n] = r.D[idx[PLAYER]][idx[n]]; });
    return out;
  }

  function state(spend) {
    var d = distances(spend);
    var s = clampSpend(spend);
    return {
      spend: s, budget: BUDGET, distances: d,
      toBoss: d[BOSS], toPortal: d[PORTAL], toLoot: d[LOOT],
      /* the whole win condition: two measured numbers compared */
      escaped: d[PORTAL] < d[BOSS],
      /* how close the call is, for the readout only -- never a threshold */
      margin: d[BOSS] - d[PORTAL],
      links: links(spend), cast: CAST
    };
  }

  var API = { CAST: CAST, PLAYER: PLAYER, BOSS: BOSS, LOOT: LOOT, PORTAL: PORTAL,
              MINION: MINION, LORE: LORE, BUDGET: BUDGET, FLOOR: FLOOR,
              bones: bones, links: links, distances: distances, state: state,
              clampSpend: clampSpend };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.QUARRY = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
