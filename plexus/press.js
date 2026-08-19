/* press.js -- the Lens algorithm. KERNEL: no interface, no network, ever.
 * ===========================================================================
 * THE LOGIC, WITHOUT THE TERMINOLOGY
 * A pomegranate is peel, bitter pith and seeds around the part you want. You do
 * not argue with the peel. You press it, and what runs out is what you can use.
 * Whatever does not run out was never going to nourish anybody, however good the
 * fruit looked from outside.
 *
 * Truthfulness is not truth. Truthfulness is manner -- fluent, confident,
 * sincere-sounding. Truth is what survives the pressing. That is the whole
 * distinction this stack is arranged around, and this file is it as arithmetic.
 *
 * WHAT IS MEASURED
 * How fast reality could contradict this, IF reality disagrees. Not whether it
 * is true. Not how likely. Not how good.
 *
 * THE CONSEQUENCE, SAID BEFORE ANYBODY MEETS IT AS A BUG
 * A completely fabricated claim carrying a named body, a year, a percentage and
 * a stated method reads MAXIMUM here. A careful, honest, vague statement reads
 * NOTHING.
 *
 * That is correct. The fabrication has staked something and can be destroyed
 * with one phone call. The vague statement cannot be destroyed at all, which is
 * why fog survives and specifics die. Pressing a well-formed lie traps the liar
 * inside their own structure. Pressing fog produces nothing, and this file says
 * so rather than producing a number.
 *
 * WHY THE MARKS HANG OFF THE ORIGIN AND NOT OFF THE CLAIM
 * A figure attributed to a report is worth nothing if the report does not exist.
 * So marks attach to the ORIGIN they are attributed to, and the origin attaches
 * to the claim. That one modelling decision produces the finding:
 *
 *     with m marks on one origin, each mark reads 1/m^2
 *
 * Five handles do not give you five ways to check. They give you one way to
 * check, dressed as five, and each reads 0.040 precisely because the graph is
 * saying they are not independent. The reassuring number is the warning. It is
 * the fifth time this shape has turned up while this repository was being built.
 *
 * WHY CONTRACTION IS THE RIGHT MOVE HERE AND THE WRONG ONE IN A BILL
 * FATHOM's sources are disjunctive. In a bill every input is required, so packs
 * refuse this readout. Here any SINGLE check coming back negative can kill the
 * claim, so disjunction is exactly the relation that holds.
 */
(function (root) {
  "use strict";

  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);

  var CLAIM = "The claim stands";
  var UNNAMED = "an origin nobody named";

  /* What a person actually does, per kind of mark. These are instructions, not
     judgements: each one can come back negative, which is the only property
     that makes a mark a check at all. */
  var INSTRUCTION = {
    source: "Open it. Confirm the thing named actually exists and says this.",
    figures: "Find the figure in the original, not in the summary of it.",
    method: "Ask how it was measured, and on how many.",
    time: "Check the date, and ask what has changed since.",
    scope: "Ask who and where it covers, and whether that includes you.",
  };

  var LABEL = {
    source: "something named you can open",
    figures: "a specific figure",
    method: "a stated way of measuring",
    time: "a date or period",
    scope: "who or where it applies",
  };

  /* ------------------------------------------------------- the check graph -- */
  /* marks: [{ kind, text, origin }]. `origin` is what the mark is attributed to.
     Marks with no stated origin all hang off one unnamed node -- which is not a
     technicality, it is the finding: an origin nobody named cannot be opened,
     and everything hanging off it goes when it goes. */
  function graph(marks) {
    var parts = [CLAIM], links = [], seenOrigin = {}, seenMark = {};
    marks.forEach(function (m, i) {
      var origin = (m.origin && String(m.origin).trim()) || UNNAMED;
      if (!seenOrigin[origin]) {
        seenOrigin[origin] = true;
        parts.push(origin);
        links.push([origin, CLAIM, 1.0]);
      }
      /* names must be unique in the graph, and two marks of the same kind on the
         same origin are two different checks */
      var name = m.name || (LABEL[m.kind] || m.kind);
      var n = name, k = 2;
      while (seenMark[n]) { n = name + " (" + k + ")"; k++; }
      seenMark[n] = true;
      parts.push(n);
      links.push([n, origin, 1.0]);
      m._node = n;
      m._origin = origin;
      void i;
    });
    return { parts: parts, links: links,
             marks: marks.map(function (m) { return m._node; }),
             origins: Object.keys(seenOrigin) };
  }

  /* ------------------------------------------------------------- the press -- */
  function press(marks) {
    marks = (marks || []).filter(function (m) { return m && m.kind; });

    if (!marks.length) {
      /* No number. Assigning a value to fog is the mask failure, committed by
         the tool built to name it. */
      return {
        checkable: false,
        says: "Nothing runs out. There is no source to open, no figure to look " +
              "up and no date to compare, so there is nothing here that could " +
              "come back negative.",
        meaning: "That is not the same as false. It means this cannot be shown " +
                 "false, which is why wording like this survives and specific " +
                 "claims die.",
        firstCheck: null, checks: [], origins: [], sharedOrigin: false,
        structure: null, marks: 0,
      };
    }

    var g = graph(marks);
    var b = ENG.bearings(g.parts, g.links);
    var sp = ENG.singlePoints(g.parts, g.links).map(function (r) { return r.part; });
    var f = ENG.sound(g.parts, g.links, g.marks, CLAIM);

    var byNode = {};
    f.bySource.forEach(function (r) { byNode[r.source] = r.dependence; });

    var checks = marks.map(function (m) {
      return {
        kind: m.kind,
        node: m._node,
        origin: m._origin,
        namedOrigin: m._origin !== UNNAMED,
        text: m.text || null,
        instruction: INSTRUCTION[m.kind] || "Go and confirm this.",
        settles: byNode[m._node],
      };
    });

    /* The first thing to do is whatever, if removed, leaves the rest of the
       claim in pieces. That is an origin -- computed by removal, never by a
       rank somebody assigned.
       THE CLAIM ITSELF IS EXCLUDED. With two or more origins the claim node is
       also a cut vertex, which is true and useless: it would have the tool
       telling somebody to go and open "The claim stands". Found by running it,
       and it also falsified a prediction made before the run -- the count of
       single points with two origins is three, not two. */
    var origins = g.origins;
    var cuts = sp.filter(function (n) { return n !== CLAIM; });
    var first = cuts.length ? cuts[0] : null;
    var shared = origins.length === 1 && marks.length > 1;

    return {
      checkable: true,
      marks: marks.length,
      origins: origins,
      unnamedOrigin: origins.indexOf(UNNAMED) >= 0,
      firstCheck: first ? {
        origin: first,
        instruction: first === UNNAMED
          ? "Ask where this came from. Until something is named there is nothing to open."
          : "Open " + first + " and confirm it exists and says this.",
        breaks: cuts.length,
      } : null,
      checks: checks.sort(function (a, b2) { return b2.settles - a.settles; }),
      singlePoints: sp,
      cutOrigins: cuts,
      sharedOrigin: shared,
      eachSettles: shared ? checks[0].settles : null,
      says: shared
        ? marks.length + " things to check, and every one of them hangs off " +
          (origins[0] === UNNAMED ? "an origin nobody named" : origins[0]) +
          ". They are not " + marks.length + " ways in; they are one way in, " +
          "counted " + marks.length + " times."
        : "There are " + marks.length + " things here you can go and do.",
      meaning: "A claim that is completely made up reads exactly like a true one " +
               "here. This says how quickly you could find out, not which way it " +
               "will go.",
      structure: {
        parts: g.parts.length,
        bearings: b.links.map(function (r) { return r.bearing; }),
        totalBearing: b.total, expected: b.expected, conserved: b.conserved,
        pieces: b.pieces,
      },
    };
  }

  /* Marks straight from a list of kinds, all on one origin. Used by the page and
     by the suite; keeps the 1/m^2 law testable without any text at all. */
  function fromKinds(kinds, origin) {
    return (kinds || []).map(function (k) {
      return { kind: k, origin: origin || null };
    });
  }

  var API = { press: press, graph: graph, fromKinds: fromKinds,
              INSTRUCTION: INSTRUCTION, LABEL: LABEL,
              CLAIM: CLAIM, UNNAMED: UNNAMED };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.PRESS = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
