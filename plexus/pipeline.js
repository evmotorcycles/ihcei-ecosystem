/* pipeline.js -- Press to Evidence, as six stages that can each refuse.
 * ===========================================================================
 * The process this stack keeps describing, made into something that can fail.
 *
 *   1 press       the physical thing this is like -- a picture, not a summary
 *   2 schema      the mental model the picture organises. STAMPED: proves nothing
 *   3 guidelines  what the schema tells you to go and check
 *   4 topology    what the claim rests on. MEASURED, never written down by hand
 *   5 solutions   what to build, each with what would show it wrong
 *   6 evidence    what was actually measured, or an honest word for why not
 *
 * THE STAGE THAT DOES THE WORK IS SIX, AND IT IS THE ONE EVERYBODY SKIPS
 * `evidence.status` must be one of three words and each has a cost:
 *
 *   measured        requires a pre-registration hash. A project claiming a
 *                   measured result with no locked prediction is refused, full
 *                   stop. That is the discipline of this whole repository turned
 *                   into a field that cannot be left blank.
 *   untestable-here requires naming the missing artefact. "We could not test it"
 *                   without saying what was missing is a shrug with a label on.
 *   not-yet         requires a date or a trigger. An intention with no when is
 *                   not a plan, and it will still be "not yet" in a year.
 *
 * WHY THE SCHEMA CARRIES A STAMP
 * A mental model organises thinking. It certifies nothing, and the moment a
 * project treats its schema as a finding, everything downstream inherits a
 * conclusion nobody measured. `provesNothing` must be literally true in the
 * data or the stage is refused.
 *
 * WHAT THIS DOES NOT DO
 * It does not decide whether a press is a good picture, whether a guideline is
 * worth following, or whether a solution is sensible. Those are judgements. It
 * checks that each stage was filled in at all, that stage six was not skipped,
 * and it measures stage four with the same engine as everything else.
 */
(function (root) {
  "use strict";

  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);
  var META = root.METAPHOR || (typeof require === "function" ? require("./metaphor.js") : null);

  var STATUSES = ["measured", "untestable-here", "not-yet"];

  function problems(p) {
    var why = [];
    if (!p || typeof p !== "object") return ["that is not a project"];
    if (typeof p.id !== "string" || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(p.id)) {
      why.push("id must be lowercase words joined by hyphens");
    }
    if (typeof p.claim !== "string" || !p.claim.trim()) {
      why.push("a project has to state the claim it is about, in one sentence");
    }

    /* 1 press -- audited by metaphor.js, the same instrument used on everybody
       else's pictures. A press that risks nothing is notation. */
    if (!p.press) why.push("stage 1: no press. What physical thing is this like?");
    else why = why.concat((META.problems(p.press) || []).map(function (w) {
      return "stage 1: " + w;
    }));

    /* 2 schema */
    if (!p.schema || typeof p.schema.says !== "string" || !p.schema.says.trim()) {
      why.push("stage 2: no schema. What does the picture organise?");
    } else if (p.schema.provesNothing !== true) {
      why.push("stage 2: the schema must carry provesNothing: true. A mental " +
               "model organises thinking and certifies nothing, and a project " +
               "that treats its schema as a finding hands a conclusion nobody " +
               "measured to everything downstream");
    }

    /* 3 guidelines -- each must be a thing a person DOES */
    if (!Array.isArray(p.guidelines) || !p.guidelines.length) {
      why.push("stage 3: no guidelines. What does the schema send you to check?");
    } else {
      p.guidelines.forEach(function (g, i) {
        if (typeof g !== "string" || !g.trim()) {
          why.push("stage 3: guideline " + (i + 1) + " is empty");
        }
      });
    }

    /* 4 topology -- parts and links only. The numbers are measured from them. */
    var t = p.topology;
    if (!t || !Array.isArray(t.parts) || t.parts.length < 2
        || !Array.isArray(t.links) || !t.links.length) {
      why.push("stage 4: no topology. What are the parts and what depends on what?");
    }

    /* 5 solutions -- each carries its own falsifier */
    if (!Array.isArray(p.solutions) || !p.solutions.length) {
      why.push("stage 5: no solutions. What would you build?");
    } else {
      p.solutions.forEach(function (s, i) {
        var at = "stage 5: solution " + (i + 1);
        if (!s || typeof s.build !== "string" || !s.build.trim()) {
          why.push(at + " does not say what to build");
        }
        if (typeof s.wrongIf !== "string" || !s.wrongIf.trim()) {
          why.push(at + " does not say what would show it was the wrong thing " +
                   "to build, so it cannot be abandoned");
        }
      });
    }

    /* 6 evidence -- the stage everybody skips */
    var e = p.evidence;
    if (!e || STATUSES.indexOf(e.status) < 0) {
      why.push("stage 6: evidence.status must be one of " + STATUSES.join(", "));
    } else if (e.status === "measured") {
      if (typeof e.preregSha256 !== "string" || !/^[0-9a-f]{64}$/.test(e.preregSha256)) {
        why.push("stage 6: a measured result needs the sha256 of the " +
                 "pre-registration that was locked before it ran");
      }
      if (typeof e.result !== "string" || !e.result.trim()) {
        why.push("stage 6: a measured result has to say what the result was");
      }
    } else if (e.status === "untestable-here") {
      if (typeof e.missing !== "string" || !e.missing.trim()) {
        why.push("stage 6: untestable-here must name the missing artefact. " +
                 "Without it this is a shrug with a label on");
      }
    } else if (e.status === "not-yet") {
      if (typeof e.when !== "string" || !e.when.trim()) {
        why.push("stage 6: not-yet must carry a date or a trigger, or it will " +
                 "still be not-yet in a year");
      }
    }
    return why;
  }

  function run(p) {
    var why = problems(p);
    if (why.length) return { ok: false, id: p && p.id, why: why };

    var t = p.topology;
    var b = ENG.bearings(t.parts, t.links);
    var sp = ENG.singlePoints(t.parts, t.links).map(function (r) { return r.part; });
    var rests = null;
    if (Array.isArray(t.sources) && t.sources.length && t.conclusion) {
      var f = ENG.sound(t.parts, t.links, t.sources, t.conclusion);
      rests = {
        deepest: f.deepest,
        bySource: f.bySource.map(function (r) {
          return { source: r.source, dependence: r.dependence };
        }),
        restsOnOneThread: f.restsOnOneThread,
      };
    }

    return {
      ok: true, why: [], id: p.id, claim: p.claim,
      press: META.audit(p.press),
      schema: p.schema,
      guidelines: p.guidelines.slice(),
      topology: {
        parts: t.parts.length,
        soleRoutes: b.links.filter(function (r) { return r.soleRoute; }).length,
        links: b.links.length,
        totalBearing: b.total, expected: b.expected, conserved: b.conserved,
        pieces: b.pieces,
        singlePoints: sp,
        restsOn: rests,
      },
      solutions: p.solutions.slice(),
      evidence: p.evidence,
      /* the one line worth reading first */
      standing: p.evidence.status === "measured"
        ? "Something here was measured against a prediction locked beforehand."
        : p.evidence.status === "untestable-here"
          ? "Nothing here has been measured, and the missing piece is named."
          : "Nothing here has been measured yet, and there is a date on when.",
    };
  }

  var API = { run: run, problems: problems, STATUSES: STATUSES };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.PIPELINE = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
