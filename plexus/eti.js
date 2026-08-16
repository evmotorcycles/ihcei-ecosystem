/* eti.js -- Elastic Topology Interface: a spatial view of a structure.
 * ===========================================================================
 * A SKIN, not a second engine. Every number here comes out of smi/lmd.js and
 * plexus/engines.js, which are parity-checked against the Python. Nothing in
 * this file invents a quantity, and nothing in it is tuned.
 *
 * WHY SPACE COLLAPSES AS COUPLING RISES
 * This is not an effect that was added; it is what the metric already does.
 * A bearing is b_ij = w_ij * R_ij, and the layout metric is d_ij = sqrt(R_ij),
 * so for any link
 *
 *     d_ij = sqrt(b_ij / w_ij)
 *
 * By Rayleigh's monotonicity law, raising any conductance cannot raise any
 * effective resistance. Turn a coupling up and the two ends must come closer;
 * turn it down and space opens between them. Measured on a four-part structure,
 * multiplying one coupling by 256 pulled its ends from 1.1547 to 0.1245 apart.
 * The view is therefore a picture of the arithmetic rather than a decoration
 * laid over it. test_eti.py fails if that monotonicity ever breaks.
 *
 * WHAT INTEGRITY IS
 * Foster's theorem: the bearings of a structure sum to parts - pieces, exactly.
 * A structure in one piece therefore carries parts - 1, which is the most any
 * structure on those parts can carry. Integrity is what it actually carries
 * over its own ceiling:
 *
 *     integrity = (parts - pieces) / (parts - 1)
 *
 * 1.0 whole, 0.0 when every part stands alone. No threshold was picked and no
 * weight was chosen -- it is the conserved quantity the "Holding it up" tab
 * already prints, divided by the largest value it could take.
 */
(function (root) {
  "use strict";

  var LMD = root.LMD || (typeof require === "function" ? require("../smi/lmd.js") : null);
  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);

  function integrity(names, links) {
    var b = ENG.bearings(names, links);
    var ceiling = b.parts - 1;
    return {
      parts: b.parts, pieces: b.pieces, total: b.total,
      integrity: ceiling > 0 ? (b.parts - b.pieces) / ceiling : 0
    };
  }

  /* One frame of the view. `prev` is the previous frame; passing it keeps the
     picture from turning over between redraws, because classical MDS fixes an
     embedding only up to rotation and reflection. */
  function frame(names, links, view, prev) {
    view = view || {};
    var W = view.w || 360, H = view.h || 320, PAD = view.pad || 30;
    var idx = {}, i;
    for (i = 0; i < names.length; i++) idx[names[i]] = i;

    var r = LMD.meshMetric(LMD.laplacianFromEdges(names.length,
      links.map(function (l) { return [idx[l[0]], idx[l[1]], l[2]]; })));

    /* Only the largest piece is laid out. A part in another piece has NO finite
       distance to this one, and drawing it at some plausible position is the
       exact lie the metric guards exist to prevent -- so it is set down along
       the foot of the view instead, visibly out of the structure. */
    var counts = {}, main = null;
    for (i = 0; i < names.length; i++) {
      var lab = r.dead ? "x" + i : String(r.labels[i]);
      counts[lab] = (counts[lab] || 0) + 1;
    }
    Object.keys(counts).forEach(function (lab) {
      if (main === null || counts[lab] > counts[main] ||
          (counts[lab] === counts[main] && lab < main)) main = lab;
    });
    var keep = [], stranded = [];
    for (i = 0; i < names.length; i++) {
      ((!r.dead && String(r.labels[i]) === main) ? keep : stranded).push(i);
    }

    var xy = [];
    if (keep.length >= 2) {
      xy = LMD.layout2d(r.D, keep);
      if (prev && prev.keep && prev.xy && prev.xy.length) {
        var shared = [], order = [], rest = [];
        keep.forEach(function (node, ii) {
          var jj = prev.keep.indexOf(node);
          (jj >= 0 ? order : rest).push(ii);
          if (jj >= 0) shared.push(prev.xy[jj]);
        });
        if (shared.length >= 2) {
          var seq = order.concat(rest);
          var aligned = LMD.procrustes2d(seq.map(function (ii) { return xy[ii]; }), shared);
          seq.forEach(function (ii, slot) { xy[ii] = aligned[slot]; });
        }
      }
    } else if (keep.length === 1) {
      xy = [[0, 0]];
    }

    var footH = stranded.length ? 44 : 0;
    var loX = PAD, hiX = W - PAD, loY = PAD, hiY = H - PAD - footH;
    var b0x = Infinity, b1x = -Infinity, b0y = Infinity, b1y = -Infinity;
    xy.forEach(function (p) {
      b0x = Math.min(b0x, p[0]); b1x = Math.max(b1x, p[0]);
      b0y = Math.min(b0y, p[1]); b1y = Math.max(b1y, p[1]);
    });
    /* Fill the frame. Taking the smallest scale that merely separates things
       draws the picture in a corner of an empty card -- measured once already
       in this codebase, at 55% of the width. */
    var s = xy.length > 1
      ? Math.min((hiX - loX) / ((b1x - b0x) || 1e-9), (hiY - loY) / ((b1y - b0y) || 1e-9))
      : 1;
    var cx = (loX + hiX) / 2 - (b0x + b1x) / 2 * s;
    var cy = (loY + hiY) / 2 - (b0y + b1y) / 2 * s;

    var nodes = [], pos = {};
    keep.forEach(function (node, ii) {
      var nd = { name: names[node], x: cx + xy[ii][0] * s, y: cy + xy[ii][1] * s,
                 stranded: false };
      nodes.push(nd); pos[nd.name] = nd;
    });
    stranded.forEach(function (node, ii) {
      var nd = { name: names[node], stranded: true,
                 x: (ii + 1) * W / (stranded.length + 1), y: H - 22 };
      nodes.push(nd); pos[nd.name] = nd;
    });

    var bear = ENG.bearings(names, links), byPair = {};
    bear.links.forEach(function (b) { byPair[b.from + "\u0000" + b.to] = b; });

    var edges = links.map(function (l) {
      var b = byPair[l[0] + "\u0000" + l[1]];
      var a = pos[l[0]], c = pos[l[1]];
      return {
        from: l[0], to: l[1], weight: l[2],
        bearing: b ? b.bearing : 0,
        sole: !!(b && b.soleRoute),
        /* the space itself: d = sqrt(R) = sqrt(bearing / weight) */
        distance: r.dead ? Infinity : r.D[idx[l[0]]][idx[l[1]]],
        x1: a ? a.x : 0, y1: a ? a.y : 0, x2: c ? c.x : 0, y2: c ? c.y : 0,
        cut: !!(a && c && (a.stranded || c.stranded))
      };
    });

    var g = integrity(names, links);
    return {
      nodes: nodes, edges: edges, keep: keep, xy: xy,
      integrity: g.integrity, parts: g.parts, pieces: g.pieces, total: g.total,
      stranded: stranded.length, dead: r.dead
    };
  }

  var API = { integrity: integrity, frame: frame };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.ETI = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
