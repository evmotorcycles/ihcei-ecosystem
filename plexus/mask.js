/* mask.js -- label-blind masking. KERNEL: no interface, no network, ever.
 * ===========================================================================
 * THE BEST IDEA IN THE PROTOCOL, AND THE ONLY PART THAT CAN BE BUILT WITHOUT
 * DATA NOBODY HAS YET.
 *
 * Strip every name off a contract until only the dependencies remain, so a
 * coder classifying it cannot be reading the label. It is the same move the
 * Shapes commons already rests on -- the arithmetic never reads a word -- and it
 * is the reason a shape measured in one field transfers to another.
 *
 * THE PROPERTY THAT MATTERS, AND IT IS A TEST NOT A PROMISE
 * Masking must change NO NUMBER. If scrubbing the labels moves a measurement,
 * the measurement was reading the labels, and every result downstream of it was
 * about vocabulary. test_mask.py asserts the bearings and the dependences are
 * bit-identical before and after.
 *
 * AND THE MASK MUST NOT LEAK
 * A masked artefact that still contains a stripped word somewhere -- in an id,
 * a note, a source field -- is not masked, it is decorated. leaks() reads the
 * whole serialised output and refuses if any stripped term survives anywhere in
 * it, in any case.
 *
 * WHAT THIS DOES NOT DO
 * It does not classify anything. Deciding whether a return is coupled or fixed,
 * whether a substrate is present, whether a hardship branch exists -- those are
 * judgements made by people looking at masked topology, and this file exists so
 * that what they look at carries no clue about which answer is wanted.
 */
(function (root) {
  "use strict";

  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);

  /* Terms are supplied per run, not hardcoded. A hardcoded list is a claim
     about which words carry a label, and that claim belongs to whoever is
     running the study, in a file they signed. */
  function normalise(terms) {
    return (terms || []).map(function (t) { return String(t).trim(); })
      .filter(function (t) { return t.length > 1; })
      .sort(function (a, b) { return b.length - a.length; });  // longest first
  }

  function problems(spec) {
    var why = [];
    if (!spec || typeof spec !== "object") return ["that is not a contract spec"];
    if (typeof spec.id !== "string" || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(spec.id)) {
      why.push("id must be lowercase words joined by hyphens");
    }
    if (!Array.isArray(spec.parts) || spec.parts.length < 2) {
      why.push("a contract needs at least two parts");
    }
    if (!Array.isArray(spec.links) || !spec.links.length) {
      why.push("a contract with no links has no structure to classify");
    }
    if (!spec.provenance || typeof spec.provenance.where !== "string"
        || !spec.provenance.where.trim()) {
      why.push("provenance.where must say where this contract text came from");
    }
    if (spec.provenance && spec.provenance.kind !== "real"
        && spec.provenance.kind !== "synthetic") {
      why.push("provenance.kind must be 'real' or 'synthetic' -- a made-up " +
               "contract and a real one must never be stored the same way");
    }
    /* A classification supplied WITH the spec would be the coder reading the
       answer off the file. It is filled in after masking, by somebody else. */
    if (spec.classification) {
      why.push("a spec must not arrive carrying its own classification");
    }
    return why;
  }

  function mask(spec, terms) {
    var why = problems(spec);
    if (why.length) return { ok: false, why: why };

    var strip = normalise(terms);
    var map = {}, back = {}, n = 0;

    function token(name) {
      if (!(name in map)) {
        n += 1;
        map[name] = "part " + n;
        back["part " + n] = name;
      }
      return map[name];
    }

    var parts = spec.parts.map(token);
    var links = spec.links.map(function (l) {
      return [token(l[0]), token(l[1]), l[2]];
    });
    var sources = (spec.sources || []).map(function (s) { return map[s] || token(s); });
    var conclusion = spec.conclusion ? (map[spec.conclusion] || token(spec.conclusion)) : null;

    return {
      ok: true, why: [],
      /* the id goes too: "murabaha-07" is a label */
      id: "contract " + (spec.serial === undefined ? "?" : spec.serial),
      parts: parts, links: links, sources: sources, conclusion: conclusion,
      stripped: strip.length,
      /* the key stays with whoever runs the study, NOT with the coder */
      key: back,
    };
  }

  /* Does any stripped term survive anywhere in the masked artefact? Reads the
     whole thing serialised, because a leak in a note or an id is still a leak. */
  function leaks(masked, terms) {
    var strip = normalise(terms);
    var blob = JSON.stringify({
      id: masked.id, parts: masked.parts, links: masked.links,
      sources: masked.sources, conclusion: masked.conclusion,
    }).toLowerCase();
    return strip.filter(function (t) { return blob.indexOf(t.toLowerCase()) >= 0; });
  }

  /* The numbers, before and after.
     NOT bit-identical, and finding that out was worth the run. The engine sorts
     node names internally, so renaming changes the ORDER of the floating-point
     operations in the eigendecomposition and the answers differ in the last
     couple of places -- measured at 5e-16 on the worked spec. The labels do
     enter the computation, not as information but as sort keys.
     So the property to assert is agreement to tolerance, not equality. A study
     that validated its masker with exact equality would fail spuriously and
     might then "fix" it by weakening the mask. */
  function measure(parts, links, sources, conclusion) {
    var b = ENG.bearings(parts, links);
    var out = {
      total: b.total, expected: b.expected, pieces: b.pieces,
      conserved: b.conserved,
      bearings: b.links.map(function (r) { return r.bearing; }).slice().sort(),
      singlePoints: ENG.singlePoints(parts, links).length,
      deepest: null,
    };
    if (sources && sources.length && conclusion) {
      out.deepest = ENG.sound(parts, links, sources, conclusion).deepest;
    }
    return out;
  }

  function unchanged(spec, terms) {
    var m = mask(spec, terms);
    if (!m.ok) return { ok: false, why: m.why };
    var before = measure(spec.parts, spec.links, spec.sources, spec.conclusion);
    var after = measure(m.parts, m.links, m.sources, m.conclusion);
    var worst = 0;
    function gap(a, b) { worst = Math.max(worst, Math.abs(a - b)); }
    gap(before.total, after.total);
    if (before.deepest !== null && after.deepest !== null) {
      gap(before.deepest, after.deepest);
    }
    before.bearings.forEach(function (x, i) { gap(x, after.bearings[i]); });

    return {
      ok: true, before: before, after: after,
      bitIdentical: JSON.stringify(before) === JSON.stringify(after),
      worstDifference: worst,
      sameToTolerance: worst < 1e-12,
      structureUnchanged: before.pieces === after.pieces
        && before.expected === after.expected
        && before.singlePoints === after.singlePoints,
      leaked: leaks(m, terms),
    };
  }

  var API = { mask: mask, leaks: leaks, measure: measure, unchanged: unchanged,
              problems: problems, normalise: normalise };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.MASK = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
