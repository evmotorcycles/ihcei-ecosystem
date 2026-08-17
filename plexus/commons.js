/* commons.js -- the structure commons. KERNEL: no interface, no network, ever.
 * ===========================================================================
 * WHAT A CONTRIBUTED STRUCTURE IS, AND WHAT IT IS NOT
 * A structure is parts and links. Nothing else. Not the water bill -- the
 * SHAPE of a water bill. Not somebody's dependency tree -- the shape "many
 * things, one registry". That distinction is the reason a commons can exist at
 * all without breaking the promise the vault makes: you can give a shape away
 * without giving anything away.
 *
 * So the schema is enforced by SUBTRACTION. A structure may carry exactly four
 * keys -- parts, links, sources, conclusion -- and validate() refuses any
 * fifth. Not because a fifth key is necessarily personal data, but because the
 * moment the shape has a free-text field somebody will put a name in it, and
 * then the commons is a database and the promise is gone. There is no
 * allow-list to argue about and no field to sanitise: there is nowhere to put
 * it.
 *
 * THREE SLOTS, AND THE TWO NUMBERS BETWEEN THEM
 * An entry is not one graph, it is up to three:
 *
 *   drawn    how the thing is usually described
 *   actual   what the dependencies really are
 *   remedy   the structure after the fix   (optional)
 *
 * and the numbers worth having are the GAPS:
 *
 *   blind spot = deepest(actual) - deepest(drawn)   how much worse than you thought
 *   relief     = deepest(actual) - deepest(remedy)  how much the fix actually buys
 *
 * A single graph tells you your situation. Two graphs tell you how wrong your
 * account of it was, and that is the part nobody can get from their own data,
 * because the wrong drawing is the one they already have.
 *
 * WHY THIS TRANSFERS
 * sound() never reads a label. Two graphs with the same shape and no word in
 * common return the same numbers, bit for bit. That is not a nice property, it
 * is the entire asset: it means "many things, one registry" measured once in a
 * package manager is already measured for a model hub, an audit programme and
 * a maintainer. test_commons.py checks it at 1e-12 across three domains, and if
 * it ever fails the library is worthless and should be deleted.
 *
 * A LIMIT, IN THE OPEN
 * FATHOM's sources are DISJUNCTIVE -- more sources always means less depends on
 * each one. Plenty of real structures are conjunctive: caches.addAll needs all
 * twelve assets or none. There is no conjunction operator here. A conjunction
 * has to be drawn as a chain, and the star somebody draws instead is wrong by
 * 0.917. The engine cannot warn you; only an entry in the library can, which is
 * roughly the whole argument for having one.
 */
(function (root) {
  "use strict";

  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);

  var SLOTS = ["drawn", "actual", "remedy"];
  var STRUCTURE_KEYS = ["parts", "links", "sources", "conclusion"];
  var ENTRY_KEYS = ["id", "title", "problem", "provenance", "drawn", "actual", "remedy", "note"];
  var PROVENANCE_KINDS = ["measured-here", "cited"];
  var LICENCE = "CC0-1.0";

  function keysOutside(obj, allowed) {
    return Object.keys(obj).filter(function (k) { return allowed.indexOf(k) < 0; });
  }

  /* Refusals come back as reasons, in the order a person would want to fix
     them, and never as exceptions -- a bad contribution must not be able to
     take the page down with it. */
  function checkStructure(s, where) {
    var why = [], seen = {}, i;
    if (!s || typeof s !== "object") return [where + " is not a structure"];

    var extra = keysOutside(s, STRUCTURE_KEYS);
    if (extra.length) {
      why.push(where + " carries " + extra.join(", ") +
               ": a structure is parts and links, and there is nowhere to put anything else");
    }
    if (!Array.isArray(s.parts) || s.parts.length < 2) {
      return why.concat([where + " needs at least two parts"]);
    }
    for (i = 0; i < s.parts.length; i++) {
      if (typeof s.parts[i] !== "string" || !s.parts[i].trim()) {
        why.push(where + " has a part with no name");
      } else if (s.parts[i].indexOf("\u0000") >= 0) {
        /* NUL is FATHOM's contracted ground. A part carrying one could be
           silently absorbed into the ground it is meant to be measured
           against. Written as an ESCAPE: a literal NUL has now been put into
           this codebase three times and caught by a test every time. */
        why.push(where + " has a part containing a NUL, which is the reserved ground");
      } else if (seen[s.parts[i]]) {
        why.push(where + " names " + s.parts[i] + " twice");
      }
      seen[s.parts[i]] = true;
    }
    if (!Array.isArray(s.links) || !s.links.length) {
      why.push(where + " has no links, so there is no structure to measure");
    } else {
      s.links.forEach(function (l, k) {
        var at = where + " link " + (k + 1);
        if (!Array.isArray(l) || l.length !== 3) { why.push(at + " is not [from, to, weight]"); return; }
        if (!seen[l[0]]) why.push(at + " starts at " + l[0] + ", which is not a part");
        if (!seen[l[1]]) why.push(at + " ends at " + l[1] + ", which is not a part");
        if (l[0] === l[1]) why.push(at + " joins " + l[0] + " to itself");
        if (typeof l[2] !== "number" || !(l[2] > 0) || !isFinite(l[2])) {
          why.push(at + " has a weight that is not a positive number");
        }
      });
    }
    if (!Array.isArray(s.sources) || !s.sources.length) {
      why.push(where + " has no sources, so there is nothing to remove");
    } else {
      s.sources.forEach(function (n) {
        if (!seen[n]) why.push(where + " lists a source, " + n + ", that is not a part");
      });
    }
    if (typeof s.conclusion !== "string" || !seen[s.conclusion]) {
      why.push(where + " has no conclusion among its parts");
    } else if (Array.isArray(s.sources) && s.sources.indexOf(s.conclusion) >= 0) {
      why.push(where + " makes " + s.conclusion + " support itself");
    }
    return why;
  }

  function validate(entry) {
    var why = [];
    if (!entry || typeof entry !== "object") return ["that is not an entry"];

    var extra = keysOutside(entry, ENTRY_KEYS);
    if (extra.length) why.push("an entry cannot carry " + extra.join(", "));

    if (typeof entry.id !== "string" || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(entry.id)) {
      why.push("id must be lowercase words joined by hyphens");
    }
    ["title", "problem"].forEach(function (k) {
      if (typeof entry[k] !== "string" || !entry[k].trim()) why.push(k + " is missing");
    });

    var p = entry.provenance;
    if (!p || typeof p !== "object") {
      why.push("provenance is missing: a structure from a real problem and one somebody imagined must not be stored the same way");
    } else {
      if (PROVENANCE_KINDS.indexOf(p.kind) < 0) {
        why.push("provenance.kind must be one of " + PROVENANCE_KINDS.join(", "));
      }
      if (typeof p.where !== "string" || !p.where.trim()) {
        why.push("provenance.where must say where the problem came from, checkably");
      }
      if (p.licence !== LICENCE) {
        why.push("a contributed structure is given under " + LICENCE + " or it cannot be redistributed");
      }
    }

    if (!entry.drawn) why.push("drawn is missing: an entry has to say how the thing is usually described");
    if (!entry.actual) why.push("actual is missing: an entry has to say what is really there");
    SLOTS.forEach(function (slot) {
      if (entry[slot]) why = why.concat(checkStructure(entry[slot], slot));
    });
    return why;
  }

  /* ------------------------------------------------------- measurement ---- */
  function measureStructure(s) {
    var b = ENG.bearings(s.parts, s.links);
    var f = ENG.sound(s.parts, s.links, s.sources, s.conclusion);
    return {
      parts: s.parts.length,
      pieces: b.pieces,
      totalBearing: b.total,
      expected: b.expected,
      conserved: b.conserved,
      links: b.links,
      singlePoints: ENG.singlePoints(s.parts, s.links),
      support: f.support,
      bySource: f.bySource,
      deepest: f.deepest,
      restsOnOneThread: f.restsOnOneThread,
    };
  }

  function measure(entry) {
    var why = validate(entry);
    if (why.length) return { id: entry && entry.id, ok: false, why: why };
    var out = { id: entry.id, title: entry.title, problem: entry.problem,
                provenance: entry.provenance, note: entry.note || null, ok: true, why: [] };
    SLOTS.forEach(function (slot) {
      out[slot] = entry[slot] ? measureStructure(entry[slot]) : null;
    });
    out.blindSpot = out.actual.deepest - out.drawn.deepest;
    out.relief = out.remedy ? out.actual.deepest - out.remedy.deepest : null;
    return out;
  }

  /* Two entries have the same SHAPE if there is a relabelling of one onto the
     other that carries links to links, sources to sources and conclusion to
     conclusion. Full graph isomorphism is expensive and unnecessary here: the
     library is small and structured, so the honest cheap test is to compare
     the multiset of measurements. If two entries return the same sorted
     dependences and the same sorted bearings, they measure the same, which is
     the only sense in which transfer is being claimed. */
  function signature(m) {
    return {
      deps: m.bySource.map(function (r) { return r.dependence; })
              .slice().sort(function (a, b) { return a - b; }),
      bearings: m.links.map(function (r) { return r.bearing; })
              .slice().sort(function (a, b) { return a - b; }),
      parts: m.parts, pieces: m.pieces,
    };
  }

  function sameShape(a, b, tol) {
    var t = tol === undefined ? 1e-12 : tol;
    if (a.parts !== b.parts || a.pieces !== b.pieces) return false;
    if (a.deps.length !== b.deps.length || a.bearings.length !== b.bearings.length) return false;
    var i;
    for (i = 0; i < a.deps.length; i++) if (Math.abs(a.deps[i] - b.deps[i]) > t) return false;
    for (i = 0; i < a.bearings.length; i++) if (Math.abs(a.bearings[i] - b.bearings[i]) > t) return false;
    return true;
  }

  /* Which library entries share a shape, across domains. This is the readout
     that says whether there is a commons here or just a list. */
  function families(entries, tol) {
    var ms = entries.map(measure).filter(function (m) { return m.ok; });
    var sigs = ms.map(function (m) { return { id: m.id, sig: signature(m.actual) }; });
    var groups = [], i, j, placed;
    for (i = 0; i < sigs.length; i++) {
      placed = false;
      for (j = 0; j < groups.length; j++) {
        if (sameShape(groups[j].sig, sigs[i].sig, tol)) {
          groups[j].ids.push(sigs[i].id); placed = true; break;
        }
      }
      if (!placed) groups.push({ sig: sigs[i].sig, ids: [sigs[i].id] });
    }
    return groups.map(function (g) { return { ids: g.ids, size: g.ids.length }; })
                 .sort(function (a, b) { return b.size - a.size; });
  }

  /* Does a shape in the library describe what somebody is looking at? Shared
     labels only, and it is a SUGGESTION -- the same rule engines.js already
     applies to suggested links. Nothing is measured on the strength of a word
     matching a word. */
  /* Labels are compared for EQUALITY after stripping a leading article, not by
     substring. Substring matching was written here first and found by running
     it: "package 3" matched "Package 30" through "Package 39", so a three-word
     query scored 0.406 against a forty-package entry instead of 0.071. A
     suggestion that flatters itself is worse than no suggestion, because the
     ordering is the only thing it is for. */
  function label(s) {
    return String(s).toLowerCase().trim().replace(/^(the|a|an)\s+/, "");
  }

  function match(entries, parts) {
    var mine = (parts || []).map(label);
    if (!mine.length) return [];
    return entries.map(function (e) {
      var theirs = (e.actual.parts || []).map(label);
      var hits = theirs.filter(function (t) { return mine.indexOf(t) >= 0; });
      return { id: e.id, title: e.title, shared: hits,
               score: hits.length / (theirs.length + mine.length - hits.length) };
    }).filter(function (r) { return r.score > 0; })
      .sort(function (a, b) { return b.score - a.score; });
  }

  /* The one number that would show the commons is real -- and it is not
     measurable in here. Stated as a function so that nothing can quietly
     substitute a measurement for it later. */
  function contributionRate(state) {
    var s = state || {};
    var buyers = s.buyers || 0, contributed = s.contributed || 0;
    if (!buyers) {
      return { measurable: false, rate: null,
               why: "nothing has shipped, so nobody has bought and nobody has contributed. " +
                    "No measurement in this file can stand in for this number." };
    }
    return { measurable: true, rate: contributed / buyers, buyers: buyers,
             contributed: contributed,
             passesGate: contributed / buyers >= 0.05 };
  }

  var API = { validate: validate, measure: measure, measureStructure: measureStructure,
              signature: signature, sameShape: sameShape, families: families,
              match: match, contributionRate: contributionRate,
              SLOTS: SLOTS, STRUCTURE_KEYS: STRUCTURE_KEYS, ENTRY_KEYS: ENTRY_KEYS,
              PROVENANCE_KINDS: PROVENANCE_KINDS, LICENCE: LICENCE };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.COMMONS = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
