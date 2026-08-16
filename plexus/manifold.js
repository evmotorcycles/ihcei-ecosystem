/* manifold.js -- apps, AI and data as nodes, with LMD managing the space.
 * ===========================================================================
 * A SANDBOX, not an operating system. Nothing here installs a real program,
 * runs a real model, or leaves the browser. What it does do is real: it holds a
 * graph of things you registered, raises the coupling between you and the ones
 * your intent names, and lets the tested metric decide how far apart everything
 * then is. The distances are measured, not animated.
 *
 * THE LAW, AND WHERE IT ACTUALLY HOLDS
 * For two nodes joined by ONE route of strength J, the effective resistance is
 * 1/J and the metric is d = sqrt(R), so
 *
 *     d = J^(-1/2)
 *
 * exactly. That is the whole of the "space collapses as coupling rises" claim,
 * and it is worth being precise about, because it is NOT a general law:
 *
 *     one route only          J: 0.02 -> 20    exponent -0.5000 throughout
 *     a second route exists   J: 0.02 -> 20    exponent -0.0192 -> -0.4878
 *
 * Both measured. With another way in, raising the direct coupling buys far less
 * collapse, because the other route was already holding the two ends close. The
 * exponent only returns to -1/2 once the direct link dominates everything else.
 *
 * So exponent(node) is not decoration: it is a live reading of whether a thing
 * is reachable one way or several. A node sitting at -0.500 has a single route
 * to you, and losing that route strands it. That is the same question the rest
 * of Plexus asks -- "is there another way round?" -- arriving here as a number
 * that falls out of the metric rather than a badge someone assigned.
 */
(function (root) {
  "use strict";

  var LMD = root.LMD || (typeof require === "function" ? require("../smi/lmd.js") : null);
  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);
  var ETI = root.ETI || (typeof require === "function" ? require("./eti.js") : null);

  var YOU = "You";
  var KINDS = ["app", "ai", "data"];

  /* Residual coupling is what remains when no intent names a thing. It is not
     zero: at zero the node has NO route to you at all, the metric correctly
     refuses to place it, and it would vanish from the picture rather than drift
     to the edge of it. Small-but-present is the honest model of "installed and
     idle". */
  function defaults() {
    return { nodes: [], affinities: [], intent: {}, residual: 0.02, boost: 12 };
  }

  function graph(state) {
    var names = [YOU], links = [], seen = {};
    state.nodes.forEach(function (n) {
      if (seen[n.name] || n.name === YOU) return;
      seen[n.name] = true;
      names.push(n.name);
      links.push([YOU, n.name, state.residual + (state.intent[n.name] ? state.boost : 0)]);
    });
    /* Affinities are couplings BETWEEN registered things -- an AI that reads a
       dataset, an app that owns a file. They are what create a second route,
       and therefore what makes the exponent readable. */
    state.affinities.forEach(function (a) {
      if (seen[a[0]] && seen[a[1]] && a[0] !== a[1]) links.push([a[0], a[1], a[2]]);
    });
    return { names: names, links: links };
  }

  function metric(state) {
    var g = graph(state), idx = {}, i;
    for (i = 0; i < g.names.length; i++) idx[g.names[i]] = i;
    if (!g.links.length) return { g: g, idx: idx, D: null, dead: true };
    var r = LMD.meshMetric(LMD.laplacianFromEdges(g.names.length,
      g.links.map(function (l) { return [idx[l[0]], idx[l[1]], l[2]]; })));
    return { g: g, idx: idx, D: r.D, dead: r.dead };
  }

  function distance(state, name) {
    var m = metric(state);
    if (m.dead || !(name in m.idx)) return Infinity;
    return m.D[m.idx[YOU]][m.idx[name]];
  }

  /* The measured exponent: d log d / d log J on the You-to-name coupling.
     Computed by actually perturbing the coupling and re-running the metric,
     rather than by assuming the -1/2 that only holds for a single route. */
  function exponent(state, name, h) {
    h = h || 1.0001;
    var d0 = distance(state, name);
    if (!isFinite(d0) || d0 <= 0) return NaN;
    var bumped = {
      nodes: state.nodes, affinities: state.affinities, intent: state.intent,
      residual: state.residual, boost: state.boost, _bump: null
    };
    /* rebuild with just this one coupling multiplied */
    var g = graph(state);
    var links = g.links.map(function (l) {
      var isThis = (l[0] === YOU && l[1] === name) || (l[1] === YOU && l[0] === name);
      return [l[0], l[1], isThis ? l[2] * h : l[2]];
    });
    var idx = {}, i;
    for (i = 0; i < g.names.length; i++) idx[g.names[i]] = i;
    var r = LMD.meshMetric(LMD.laplacianFromEdges(g.names.length,
      links.map(function (l) { return [idx[l[0]], idx[l[1]], l[2]]; })));
    var d1 = r.D[idx[YOU]][idx[name]];
    void bumped;
    if (!isFinite(d1) || d1 <= 0) return NaN;
    return Math.log(d1 / d0) / Math.log(h);
  }

  /* Everything the readout needs, measured in one pass. */
  function telemetry(state) {
    var m = metric(state);
    var rows = state.nodes.map(function (n) {
      var d = (m.dead || !(n.name in m.idx)) ? Infinity : m.D[m.idx[YOU]][m.idx[n.name]];
      return {
        name: n.name, kind: n.kind, intent: !!state.intent[n.name],
        distance: d, exponent: exponent(state, n.name),
        coupling: state.residual + (state.intent[n.name] ? state.boost : 0)
      };
    });
    rows.sort(function (a, b) { return a.distance - b.distance; });
    var chosen = rows.filter(function (r) { return r.intent && isFinite(r.distance); });
    var span = 0;
    if (chosen.length && !m.dead) {
      chosen.forEach(function (a) {
        chosen.forEach(function (b) {
          var dd = m.D[m.idx[a.name]][m.idx[b.name]];
          if (isFinite(dd) && dd > span) span = dd;
        });
      });
    }
    var g = graph(state);
    var gi = g.links.length ? ETI.integrity(g.names, g.links)
                            : { integrity: 0, parts: g.names.length, pieces: g.names.length, total: 0 };
    return { rows: rows, span: span, chosen: chosen.length, integrity: gi.integrity,
             parts: gi.parts, pieces: gi.pieces, total: gi.total };
  }

  function frame(state, view, prev) {
    var g = graph(state);
    if (!g.links.length) {
      return { nodes: [], edges: [], keep: [], xy: [], integrity: 0,
               parts: g.names.length, pieces: g.names.length, total: 0,
               stranded: g.names.length, dead: true, hiddenLabels: [] };
    }
    return ETI.frame(g.names, g.links, view, prev);
  }

  function install(state, name, kind) {
    name = String(name || "").trim();
    if (!name) return "Give it a name.";
    if (name === YOU) return "That name is taken by you.";
    if (KINDS.indexOf(kind) < 0) return "Pick app, AI or data.";
    if (state.nodes.some(function (n) { return n.name === name; })) {
      return "There is already something called " + name + ".";
    }
    state.nodes.push({ name: name, kind: kind });
    return null;
  }

  function uninstall(state, name) {
    state.nodes = state.nodes.filter(function (n) { return n.name !== name; });
    state.affinities = state.affinities.filter(function (a) {
      return a[0] !== name && a[1] !== name;
    });
    delete state.intent[name];
  }

  function couple(state, a, b, w) {
    if (a === b) return "A thing cannot be coupled to itself.";
    var has = state.nodes.some(function (n) { return n.name === a; }) &&
              state.nodes.some(function (n) { return n.name === b; });
    if (!has) return "Both have to be installed first.";
    var dup = state.affinities.some(function (x) {
      return (x[0] === a && x[1] === b) || (x[0] === b && x[1] === a);
    });
    if (dup) return a + " and " + b + " are already coupled.";
    state.affinities.push([a, b, w || 1]);
    return null;
  }

  var API = {
    YOU: YOU, KINDS: KINDS, defaults: defaults, graph: graph, distance: distance,
    exponent: exponent, telemetry: telemetry, frame: frame,
    install: install, uninstall: uninstall, couple: couple
  };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.MANIFOLD = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
