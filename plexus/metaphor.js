/* metaphor.js -- is this picture a lens or a covering? KERNEL: no interface.
 * ===========================================================================
 * THE TEST, AND IT IS NEWTON'S
 * He imagined light as tiny billiard balls. That picture predicted the angle
 * off a mirror, the bend into glass, and a perfectly sharp shadow with no
 * bending round an edge. Two of those came back FALSE. The corpuscle metaphor
 * was killed by its own predictions, and that is exactly what made it a lens
 * rather than a decoration: it had put something at risk.
 *
 * So a metaphor is audited on one question. What does this picture predict that
 * could come back false -- and WHO IS ABLE TO MAKE THAT PREDICTION COME TRUE?
 *
 * THREE CLASSES, AND THE MIDDLE ONE IS THE FINDING
 *
 *   notation        predicts nothing at all. "Cloud". "Folder". "For you".
 *                   Not a criticism: a legend on a map cannot be wrong and is
 *                   still worth having. It is simply not a model.
 *
 *   self-referring  predicts only things the presenter controls. "Widen the
 *                   pipe and bandwidth rises" is refutable -- widen it, watch
 *                   throughput -- but if it comes back false the people who
 *                   built the pipe can fix it by editing their own code. Not an
 *                   accusation of bad faith: every working demo is like this.
 *
 *   lens            predicts at least one thing the presenter does NOT control.
 *                   Nobody could rescue Newton's corpuscles by changing
 *                   anything except the theory.
 *
 * That last distinction is the whole reason a picture over infrastructure a
 * vendor operates cannot do the work this stack needs a picture to do.
 *
 * WHERE THE ARITHMETIC COMES FROM
 * A metaphor's predictions hang off the metaphor, exactly as a claim's handles
 * hang off its origin in press.js -- if the picture is wrong they all go
 * together. Same graph, same engine, and the same law falls out: with m
 * predictions, each settles 1/m^2.
 *
 * WHAT IS HAND-WRITTEN AND WHAT IS NOT
 * The list of predictions for each metaphor is written by a person. The
 * classification and the arithmetic over that list are not. Anyone who thinks a
 * prediction has been missed can add one, and the class will change -- which is
 * the only honest way to publish a judgement about somebody else's design.
 */
(function (root) {
  "use strict";

  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);

  var NOTATION = "notation";
  var SELF = "self-referring";
  var LENS = "lens";

  function problems(m) {
    var why = [];
    if (!m || typeof m !== "object") return ["that is not a metaphor"];
    if (typeof m.id !== "string" || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(m.id)) {
      why.push("id must be lowercase words joined by hyphens");
    }
    ["name", "says"].forEach(function (k) {
      if (typeof m[k] !== "string" || !m[k].trim()) why.push(k + " is missing");
    });
    if (!Array.isArray(m.predicts)) {
      /* An absent list and an empty list are different things. Empty is a
         finding -- this picture predicts nothing. Absent means nobody looked,
         and publishing a class for something nobody looked at is the failure
         this file exists to name. */
      why.push((m.id || "the metaphor") + " has no predicts list at all, so " +
               "nobody has asked what it puts at risk");
    } else {
      m.predicts.forEach(function (p, i) {
        var at = (m.id || "a metaphor") + " prediction " + (i + 1);
        if (!p || typeof p !== "object") { why.push(at + " is not a prediction"); return; }
        if (typeof p.says !== "string" || !p.says.trim()) {
          why.push(at + " does not say what could come back false");
        }
        if (typeof p.presenterControls !== "boolean") {
          why.push(at + " does not say whether the presenter could make it true " +
                   "by changing their own work, which is the whole question");
        }
      });
    }
    if (typeof m.where !== "string" || !m.where.trim()) {
      why.push((m.id || "the metaphor") + " does not say where this reading came from");
    }
    return why;
  }

  /* Same shape as press.js: predictions hang off the metaphor, the metaphor
     carries the picture. If the picture is wrong they all go at once. */
  function graph(m) {
    var origin = m.name;
    var claim = "The picture holds";
    var parts = [claim, origin], links = [[origin, claim, 1.0]], seen = {};
    var names = [];
    m.predicts.forEach(function (p, i) {
      var n = "prediction " + (i + 1), k = 2;
      while (seen[n]) { n = "prediction " + (i + 1) + " (" + k + ")"; k++; }
      seen[n] = true;
      parts.push(n);
      links.push([n, origin, 1.0]);
      names.push(n);
    });
    return { parts: parts, links: links, predictions: names,
             origin: origin, claim: claim };
  }

  function audit(m) {
    var why = problems(m);
    if (why.length) return { ok: false, id: m && m.id, why: why };

    var uncontrolled = m.predicts.filter(function (p) { return !p.presenterControls; });

    if (!m.predicts.length) {
      return {
        ok: true, why: [], id: m.id, name: m.name, says: m.says, where: m.where,
        refutable: false, klass: NOTATION,
        uncontrolled: 0, predictions: [],
        verdict: "This picture predicts nothing, so nothing could show it wrong. " +
                 "That is not a fault -- a legend on a map cannot be wrong either " +
                 "-- but it is a way of writing something down, not a model of it.",
        structure: null, killed: !!m.killed,
      };
    }

    var g = graph(m);
    var b = ENG.bearings(g.parts, g.links);
    var f = ENG.sound(g.parts, g.links, g.predictions, g.claim);
    var by = {};
    f.bySource.forEach(function (r) { by[r.source] = r.dependence; });

    var klass = uncontrolled.length ? LENS : SELF;

    return {
      ok: true, why: [], id: m.id, name: m.name, says: m.says, where: m.where,
      refutable: true, klass: klass,
      uncontrolled: uncontrolled.length,
      killed: !!m.killed,
      killedBy: m.killedBy || null,
      predictions: m.predicts.map(function (p, i) {
        return { says: p.says, presenterControls: p.presenterControls,
                 settles: by[g.predictions[i]] };
      }),
      verdict: klass === LENS
        ? "At least one of these could come back false in a way the people " +
          "showing you the picture could not fix by changing their own work. " +
          "That is what makes it worth looking through."
        : "Every one of these could be made true by the people who built it, " +
          "editing their own code. It is refutable about itself and silent " +
          "about the world. That is a demonstration, not an instrument.",
      structure: {
        parts: g.parts.length,
        bearings: b.links.map(function (r) { return r.bearing; }),
        totalBearing: b.total, expected: b.expected, conserved: b.conserved,
        pieces: b.pieces,
      },
    };
  }

  function tally(list) {
    var out = {};
    out[NOTATION] = 0; out[SELF] = 0; out[LENS] = 0;
    list.map(audit).forEach(function (r) { if (r.ok) out[r.klass] += 1; });
    return out;
  }

  var API = { audit: audit, problems: problems, graph: graph, tally: tally,
              NOTATION: NOTATION, SELF: SELF, LENS: LENS };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.METAPHOR = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
