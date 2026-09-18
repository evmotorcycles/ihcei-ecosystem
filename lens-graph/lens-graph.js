/* lens-graph.js — the graph engine, LIFTED VERBATIM from app-2.html.
 *
 * NOT retyped and NOT re-implemented. The two blocks below are a byte-exact
 * copy of the <script> bodies in app-2.html, which are themselves ports of
 * smi/lmd.py and spar/fathom, parity-checked against the Python engines by
 * smi/test_parity.py and plexus/test_plexus.py over shared graphs.
 *
 * A hand-copy would be a THIRD implementation that nothing tests.
 * test_lens_graph.py asserts this file still matches its source byte for byte;
 * if app-2.html moves and this does not, the suite goes red rather than the
 * two quietly drifting apart.
 */

/* lmd.js -- the LMD metric engine, in the browser.
 * ===========================================================================
 * A faithful port of smi/lmd.py so SMI runs on a phone with no server. A port
 * is a liability unless it is checked: smi/test_parity.py runs both engines
 * over a shared list of graphs and fails if any distance differs by more than
 * 1e-9. The port is not trusted; it is tested.
 *
 * There is no linear-algebra library here on purpose. The Laplacian is real and
 * symmetric, so the cyclic Jacobi eigenvalue algorithm gives an exact
 * eigendecomposition in about forty lines, and the pseudo-inverse is then
 *
 *     pinv(L) = V · diag(1/λ for λ above tolerance, else 0) · Vᵀ
 *
 * which is all this needs. Fifty nodes is well under a millisecond.
 *
 * WHAT IS BEING MEASURED
 * A dependency graph inside running software: which live elements determine
 * which others, and how strongly. J is the strength of a dependency; d is how
 * far apart two elements should sit given all of them. Information layer. Not
 * a claim about matter or physical distance.
 */
(function (root) {
  "use strict";

  var DEAD_MESH_EPS = 1e-12;

  /* A coupling below this is DECLARED FADING: still connected, but too weak to
   * show at display precision. Without a name for it, a wire reading 0.00 in
   * the readout while the legend insists "live" is a fourth, unnamed state --
   * the interface saying connected and the arithmetic saying I move nothing. */
  var FADE_BELOW = 0.01;

  /* Cyclic Jacobi for a real symmetric matrix. Returns { values, vectors }
   * where vectors[i][k] is component i of eigenvector k. */
  function eigSymmetric(Ain, sweeps) {
    var n = Ain.length, i, j, k, p, q, s;
    var A = Ain.map(function (r) { return r.slice(); });
    var V = [];
    for (i = 0; i < n; i++) {
      V.push(new Array(n).fill(0));
      V[i][i] = 1;
    }
    sweeps = sweeps || 60;
    for (s = 0; s < sweeps; s++) {
      var off = 0;
      for (i = 0; i < n; i++) for (j = i + 1; j < n; j++) off += A[i][j] * A[i][j];
      if (off < 1e-30) break;
      for (p = 0; p < n - 1; p++) {
        for (q = p + 1; q < n; q++) {
          if (Math.abs(A[p][q]) < 1e-300) continue;
          var theta = (A[q][q] - A[p][p]) / (2 * A[p][q]);
          var t = Math.sign(theta || 1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
          var c = 1 / Math.sqrt(t * t + 1), sn = t * c;
          for (k = 0; k < n; k++) {
            var akp = A[k][p], akq = A[k][q];
            A[k][p] = c * akp - sn * akq;
            A[k][q] = sn * akp + c * akq;
          }
          for (k = 0; k < n; k++) {
            var apk = A[p][k], aqk = A[q][k];
            A[p][k] = c * apk - sn * aqk;
            A[q][k] = sn * apk + c * aqk;
          }
          for (k = 0; k < n; k++) {
            var vkp = V[k][p], vkq = V[k][q];
            V[k][p] = c * vkp - sn * vkq;
            V[k][q] = sn * vkp + c * vkq;
          }
        }
      }
    }
    var vals = [];
    for (i = 0; i < n; i++) vals.push(A[i][i]);
    return { values: vals, vectors: V };
  }

  /* d_ij = sqrt(R_ij), R_ij = L⁺_ii + L⁺_jj − 2·L⁺_ij. Same as the Python. */
  function metricFromLaplacian(L) {
    var n = L.length, i, j, k;
    var e = eigSymmetric(L);
    var maxAbs = 0;
    for (i = 0; i < n; i++) maxAbs = Math.max(maxAbs, Math.abs(e.values[i]));
    // the same rank tolerance numpy/jax use for pinv on a symmetric matrix
    var tol = maxAbs * n * 2.220446049250313e-16;

    var P = [];
    for (i = 0; i < n; i++) P.push(new Array(n).fill(0));
    for (k = 0; k < n; k++) {
      if (Math.abs(e.values[k]) <= tol) continue;
      var inv = 1 / e.values[k];
      for (i = 0; i < n; i++) {
        var vik = e.vectors[i][k];
        if (vik === 0) continue;
        for (j = 0; j < n; j++) P[i][j] += inv * vik * e.vectors[j][k];
      }
    }
    var D = [];
    for (i = 0; i < n; i++) {
      D.push(new Array(n).fill(0));
      for (j = 0; j < n; j++) {
        var R = P[i][i] + P[j][j] - 2 * P[i][j];
        D[i][j] = Math.sqrt(R > 0 ? R : 0);
      }
    }
    return D;
  }

  /* Which nodes can actually reach which. pinv neither knows nor cares that a
   * graph is in pieces; this does. */
  function componentsOf(L, tol) {
    tol = tol || 1e-12;
    var n = L.length, label = new Array(n).fill(-1), next = 0, i, u, v;
    for (i = 0; i < n; i++) {
      if (label[i] !== -1) continue;
      var stack = [i];
      label[i] = next;
      while (stack.length) {
        u = stack.pop();
        for (v = 0; v < n; v++) {
          if (v !== u && Math.abs(L[u][v]) > tol && label[v] === -1) {
            label[v] = next;
            stack.push(v);
          }
        }
      }
      next++;
    }
    return label;
  }

  /* The distance matrix an interface may actually trust: the raw metric with
   * the two places pinv lies removed.
   *   - pairs in different pieces come back Infinity, not a small number
   *   - a mesh with no coupling left comes back all-Infinity, not all-zero */
  function meshMetric(L) {
    var n = L.length, i, j, off = 0, D;
    for (i = 0; i < n; i++) for (j = 0; j < n; j++) if (i !== j) off += Math.abs(L[i][j]);
    if (off < DEAD_MESH_EPS) {
      D = [];
      for (i = 0; i < n; i++) {
        D.push(new Array(n).fill(Infinity));
        D[i][i] = 0;
      }
      return { D: D, labels: Array.from({ length: n }, function (_, k) { return k; }), dead: true };
    }
    D = metricFromLaplacian(L);
    var lab = componentsOf(L);
    var pieces = Math.max.apply(null, lab);
    for (i = 0; i < n; i++) {
      for (j = 0; j < n; j++) {
        if (i === j) D[i][j] = 0;
        else if (pieces > 0 && lab[i] !== lab[j]) D[i][j] = Infinity;
      }
    }
    return { D: D, labels: lab, dead: false };
  }

  function laplacianFromEdges(n, edges) {
    var W = [], i;
    for (i = 0; i < n; i++) W.push(new Array(n).fill(0));
    edges.forEach(function (e) {
      if (e[0] === e[1]) throw new Error("a node cannot depend on itself: " + e[0]);
      W[e[0]][e[1]] = W[e[1]][e[0]] = e[2];
    });
    var L = [];
    for (i = 0; i < n; i++) {
      L.push(W[i].map(function (w) { return -w; }));
      L[i][i] = W[i].reduce(function (a, b) { return a + b; }, 0);
    }
    return L;
  }

  function ringLaplacian(n, J) {
    var edges = [], i;
    for (i = 0; i < n; i++) edges.push([i, (i + 1) % n, J]);
    return laplacianFromEdges(n, edges);
  }

  /* Classical MDS: double-centre the squared distances, take the top two
   * eigenvectors. The flat picture that best preserves the metric. */
  /* `axes` selects WHICH two eigenvectors, by rank. (0,1) is the classical
   * choice and keeps the most total structure. It is not always the one that
   * keeps the most useful structure -- see bestAxes. */
  function layout2d(D, keep, axes) {
    axes = axes || [0, 1];
    var m = keep.length, i, j;
    var B = [];
    for (i = 0; i < m; i++) B.push(new Array(m).fill(0));
    var sq = [];
    for (i = 0; i < m; i++) {
      sq.push(new Array(m).fill(0));
      for (j = 0; j < m; j++) {
        var d = D[keep[i]][keep[j]];
        sq[i][j] = d * d;
      }
    }
    var rowMean = sq.map(function (r) { return r.reduce(function (a, b) { return a + b; }, 0) / m; });
    var grand = rowMean.reduce(function (a, b) { return a + b; }, 0) / m;
    for (i = 0; i < m; i++) {
      for (j = 0; j < m; j++) B[i][j] = -0.5 * (sq[i][j] - rowMean[i] - rowMean[j] + grand);
    }
    var e = eigSymmetric(B);
    var order = e.values.map(function (v, k) { return [v, k]; })
      .sort(function (a, b) { return b[0] - a[0]; });
    var p1 = order[Math.min(axes[0], m - 1)], p2 = order[Math.min(axes[1], m - 1)];
    var out = [];
    for (i = 0; i < m; i++) {
      out.push([
        e.vectors[i][p1[1]] * Math.sqrt(Math.max(p1[0], 0)),
        e.vectors[i][p2[1]] * Math.sqrt(Math.max(p2[0], 0)),
      ]);
    }
    return out;
  }

  /* The worst pair in a layout, as a fraction of its true distance. 1.0 means
   * every distance on screen is the real one. */
  function flatness(D, keep, xy) {
    var worst = 1.0, a = -1, b = -1, i, j;
    for (i = 0; i < keep.length; i++) {
      for (j = i + 1; j < keep.length; j++) {
        var trueD = D[keep[i]][keep[j]];
        if (!isFinite(trueD) || trueD <= 0) continue;
        var ratio = Math.hypot(xy[i][0] - xy[j][0], xy[i][1] - xy[j][1]) / trueD;
        if (ratio < worst) { worst = ratio; a = keep[i]; b = keep[j]; }
      }
    }
    return { ratio: worst, a: a, b: b };
  }

  /* The plane that leaves NO pair collapsed, if there is one.
   *
   * Classical MDS minimises strain, which is a TOTAL -- and a total can be
   * excellent while one pair is destroyed. On the mesh SMI ships, the
   * strain-best plane draws two elements on top of each other (0% of their true
   * distance) while a different plane draws every pair at 71% or better.
   * Neither view is wrong; they answer different questions. */
  function bestAxes(D, keep, limit) {
    limit = Math.min(limit || 4, keep.length);
    var best = [0, 1], bestRatio = -1, i, j;
    for (i = 0; i < limit; i++) {
      for (j = i + 1; j < limit; j++) {
        var r = flatness(D, keep, layout2d(D, keep, [i, j])).ratio;
        if (r > bestRatio) { bestRatio = r; best = [i, j]; }
      }
    }
    return { axes: best, ratio: bestRatio };
  }

  /* ------------------------------------------------------- frame alignment --
   * Classical MDS fixes an embedding only up to rotation and reflection: the
   * eigenvectors are defined up to sign, so a small change in the graph can
   * hand back the same picture upside down. Deterministic per input, and to a
   * person dragging it, the map flipping under their finger reads as the
   * positions being arbitrary -- which is exactly the claim SMI makes against.
   *
   * So each new embedding is rotated/reflected onto the previous one, choosing
   * whichever orthogonal transform moves the shared nodes least. Real change
   * still shows; the cosmetic flips stop. This is the orthogonal Procrustes
   * problem, solved in closed form because 2-D needs no SVD.
   */
  function procrustes2d(Q, P) {
    var n = Math.min(Q.length, P.length), i;
    if (n < 2) return Q.slice();
    var qc = [0, 0], pc = [0, 0];
    for (i = 0; i < n; i++) {
      qc[0] += Q[i][0]; qc[1] += Q[i][1];
      pc[0] += P[i][0]; pc[1] += P[i][1];
    }
    qc = [qc[0] / n, qc[1] / n];
    pc = [pc[0] / n, pc[1] / n];

    function residual(theta, flip) {
      var c = Math.cos(theta), s2 = Math.sin(theta), tot = 0;
      for (var k = 0; k < n; k++) {
        var qx = (Q[k][0] - qc[0]) * (flip ? -1 : 1), qy = Q[k][1] - qc[1];
        var x = c * qx - s2 * qy, y = s2 * qx + c * qy;
        tot += (x - (P[k][0] - pc[0])) * (x - (P[k][0] - pc[0])) +
               (y - (P[k][1] - pc[1])) * (y - (P[k][1] - pc[1]));
      }
      return tot;
    }
    function bestAngle(flip) {
      var num = 0, den = 0;
      for (var k = 0; k < n; k++) {
        var qx = (Q[k][0] - qc[0]) * (flip ? -1 : 1), qy = Q[k][1] - qc[1];
        var px = P[k][0] - pc[0], py = P[k][1] - pc[1];
        num += qx * py - qy * px;
        den += qx * px + qy * py;
      }
      return Math.atan2(num, den);
    }
    var best = null;
    [false, true].forEach(function (flip) {
      var th = bestAngle(flip), r = residual(th, flip);
      if (best === null || r < best.r) best = { r: r, th: th, flip: flip };
    });
    var c = Math.cos(best.th), sn = Math.sin(best.th), out = [];
    for (i = 0; i < Q.length; i++) {
      var qx = (Q[i][0] - qc[0]) * (best.flip ? -1 : 1), qy = Q[i][1] - qc[1];
      out.push([c * qx - sn * qy + pc[0], sn * qx + c * qy + pc[1]]);
    }
    return out;
  }

  var API = {
    procrustes2d: procrustes2d,
    FADE_BELOW: FADE_BELOW,
    metricFromLaplacian: metricFromLaplacian,
    meshMetric: meshMetric,
    componentsOf: componentsOf,
    laplacianFromEdges: laplacianFromEdges,
    ringLaplacian: ringLaplacian,
    eigSymmetric: eigSymmetric,
    layout2d: layout2d,
    flatness: flatness,
    bestAxes: bestAxes,
    DEAD_MESH_EPS: DEAD_MESH_EPS,
  };

  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.LMD = API;
})(typeof globalThis !== "undefined" ? globalThis : this);

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
