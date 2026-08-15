/* engines.js -- SPAR and FATHOM in the browser, on top of the tested LMD engine.
 * ===========================================================================
 * Loaded after smi/lmd.js, which supplies meshMetric, laplacianFromEdges,
 * layout2d, procrustes2d and the two guards. That engine is parity-checked
 * against the JAX engine over fourteen graphs; nothing here re-implements it.
 *
 * These two are checked the same way, by plexus/test_plexus.py, against the
 * Python in spar/spar.py and fathom/fathom.py.
 */
(function (root) {
  "use strict";

  var LMD = root.LMD || (typeof require === "function" ? require("../smi/lmd.js") : null);

  /* ------------------------------------------------------------- SPAR ---- */
  /* bearing = w * R = P(this link is in a random spanning tree) = how often the
   * link is the thing holding the structure together. The bearings sum to
   * exactly parts - pieces, by Foster's theorem, which is why nothing here is a
   * score somebody chose. */
  function bearings(names, links) {
    var idx = {}, i;
    for (i = 0; i < names.length; i++) idx[names[i]] = i;
    if (!links.length) {
      return { links: [], total: 0, pieces: names.length, parts: names.length,
               expected: 0, conserved: true, dead: true };
    }
    var r = LMD.meshMetric(LMD.laplacianFromEdges(
      names.length, links.map(function (l) { return [idx[l[0]], idx[l[1]], l[2]]; })));
    var pieces = Math.max.apply(null, r.labels) + 1;
    var rows = [], total = 0;
    links.forEach(function (l, k) {
      var d = r.D[idx[l[0]]][idx[l[1]]];
      var b = l[2] * d * d;
      total += b;
      rows.push({ i: k, from: l[0], to: l[1], weight: l[2], bearing: b,
                  soleRoute: b >= 0.999 });
    });
    var expected = names.length - pieces;
    return { links: rows, total: total, pieces: pieces, parts: names.length,
             expected: expected, conserved: Math.abs(total - expected) < 1e-9,
             dead: false };
  }

  /* Which PARTS everything passes through. A link's bearing cannot answer this,
   * and it is computed by removal rather than by a formula. */
  function singlePoints(names, links) {
    if (names.length < 3 || !links.length) return [];
    var base = bearings(names, links).pieces, out = [];
    names.forEach(function (n) {
      var rest = names.filter(function (x) { return x !== n; });
      var kept = links.filter(function (l) { return l[0] !== n && l[1] !== n; });
      // NOT skipped when kept is empty: a part whose removal leaves no links at
      // all is the most complete break there is.
      var after = kept.length ? bearings(rest, kept).pieces : rest.length;
      if (after > base) out.push({ part: n, piecesAfter: after });
    });
    return out;
  }

  /* ----------------------------------------------------------- FATHOM ---- */
  var GROUND = "\u0000ground";   // cannot collide with a real name

  function support(names, links, sources, drop) {
    var keep = sources.filter(function (s) { return s !== drop; });
    if (!keep.length) return null;
    var live = links.filter(function (l) { return l[0] !== drop && l[1] !== drop; });
    var isSrc = {};
    keep.forEach(function (s) { isSrc[s] = true; });

    /* pairs are kept as ARRAYS. An earlier version joined the two names into a
       string key and split it back with split(""), which splits into single
       characters -- it worked only for one-character names and silently built
       nonsense graphs for everything else. */
    var pairs = [], seen = {};
    live.forEach(function (l) {
      var a = isSrc[l[0]] ? GROUND : l[0], b = isSrc[l[1]] ? GROUND : l[1];
      if (a === b) return;                        // inside the contracted ground
      var lo = a < b ? a : b, hi = a < b ? b : a;
      var key = lo + "\u0000" + hi;
      if (key in seen) { pairs[seen[key]][2] += l[2]; return; }
      seen[key] = pairs.length;
      pairs.push([lo, hi, l[2]]);
    });
    if (!pairs.length) return null;

    var nm = [], set = {};
    pairs.forEach(function (p) {
      [p[0], p[1]].forEach(function (n) {
        if (!(n in set)) { set[n] = true; nm.push(n); }
      });
    });
    nm.sort();
    var idx = {}, i;
    for (i = 0; i < nm.length; i++) idx[nm[i]] = i;
    return { nm: nm, idx: idx, pairs: pairs };
  }

  function conductance(names, links, sources, conclusion, drop) {
    var g = support(names, links, sources, drop);
    if (!g || !(conclusion in g.idx) || !(GROUND in g.idx)) return 0;
    var edges = g.pairs.map(function (p) { return [g.idx[p[0]], g.idx[p[1]], p[2]]; });
    var r = LMD.meshMetric(LMD.laplacianFromEdges(g.nm.length, edges));
    if (r.dead) return 0;
    var d = r.D[g.idx[conclusion]][g.idx[GROUND]];
    if (!isFinite(d) || d <= 0) return 0;
    return 1 / (d * d);
  }

  /* dependence(s) = 1 - support without s / support with all.
   * Contraction is the move: it stops asking "is there another way round this
   * link" and starts asking "is there another way IN". */
  function sound(names, links, sources, conclusion) {
    var base = conductance(names, links, sources, conclusion, null);
    var rows = sources.map(function (s) {
      var without = conductance(names, links, sources, conclusion, s);
      var dep = base > 0 ? 1 - without / base : 1;
      return { source: s, dependence: dep, carriesItAlone: dep >= 0.999 };
    });
    rows.sort(function (a, b) { return b.dependence - a.dependence; });
    var deepest = rows.length ? rows[0] : null;
    return {
      conclusion: conclusion, support: base, bySource: rows,
      deepest: deepest ? deepest.dependence : 1,
      restsOnOneThread: !!(deepest && deepest.carriesItAlone),
      remaining: deepest ? 1 - deepest.dependence : 0,
    };
  }

  /* ------------------------------------------------- suggested links ----- */
  /* Shared labels only. This is a SUGGESTION and never a measurement: two
   * things sharing a word are not thereby dependent on one another, and
   * nothing computed here is fed into a bearing or a sounding unless a person
   * confirms the link first. */
  function suggest(items) {
    var out = [], i, j;
    for (i = 0; i < items.length; i++) {
      for (j = i + 1; j < items.length; j++) {
        var a = items[i].tags || [], b = items[j].tags || [];
        if (!a.length || !b.length) continue;
        var inter = a.filter(function (t) { return b.indexOf(t) >= 0; });
        if (!inter.length) continue;
        var union = a.concat(b.filter(function (t) { return a.indexOf(t) < 0; }));
        out.push({ a: items[i].name, b: items[j].name,
                   shared: inter, score: inter.length / union.length });
      }
    }
    out.sort(function (x, y) { return y.score - x.score; });
    return out;
  }

  var API = { bearings: bearings, singlePoints: singlePoints, sound: sound,
              conductance: conductance, suggest: suggest, GROUND: GROUND };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.PLEXUS = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
