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
  function layout2d(D, keep) {
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
    var out = [];
    for (i = 0; i < m; i++) {
      out.push([
        e.vectors[i][order[0][1]] * Math.sqrt(Math.max(order[0][0], 0)),
        e.vectors[i][order[1] ? order[1][1] : order[0][1]] *
          Math.sqrt(Math.max(order[1] ? order[1][0] : 0, 0)),
      ]);
    }
    return out;
  }

  var API = {
    metricFromLaplacian: metricFromLaplacian,
    meshMetric: meshMetric,
    componentsOf: componentsOf,
    laplacianFromEdges: laplacianFromEdges,
    ringLaplacian: ringLaplacian,
    eigSymmetric: eigSymmetric,
    layout2d: layout2d,
    DEAD_MESH_EPS: DEAD_MESH_EPS,
  };

  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.LMD = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
