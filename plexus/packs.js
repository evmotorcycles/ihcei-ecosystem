/* packs.js -- the structure arrives already built. KERNEL: no interface.
 * ===========================================================================
 * THE BLANK CANVAS IS THE DEFECT
 * Asking a person holding a bill to name six parts and draw five links before
 * the software says anything is homework. The mask asks for one tap. A tired
 * person at the end of a long day takes the one tap, every time, and they are
 * right to.
 *
 * A pack is a shape somebody already worked out with the numbers left empty.
 * You type what is on your paper. Nothing else.
 *
 * TWO ANSWERS, AND THEY ARE NEVER FUSED
 *
 *   arithmetic  does the printed total follow from the numbers you typed?
 *               Recomputed from scratch. Either it matches or the difference is
 *               named. No model, no judgement, no score.
 *
 *   structure   what does it rest on, and is there a second way to any of it?
 *               The same Foster arithmetic as everywhere else in this stack.
 *
 * One green light fusing the two would be the most saleable thing a pack could
 * produce and the least honest. A bill can be arithmetically perfect and rest
 * entirely on one meter reading nobody checked; a bill can come out exactly
 * right on a tariff nobody agreed to. `difference == 0` means the printed total
 * follows from what you typed, and it means nothing else at all.
 *
 * WHY THE STRUCTURE READOUT HERE IS SINGLE POINTS AND NOT REDUNDANCY
 * Every input to an arithmetic identity is required: units needs BOTH meter
 * readings, the total needs the rate AND the fee. That is a conjunction, and
 * FATHOM's sources are disjunctive -- more sources always means less rests on
 * each. It is the same limit the Shapes library records as atomic-install-list,
 * where a twelve-way conjunction drawn as a star understates by 0.917. Run over
 * a bill it would report each meter reading at 0.0625, which is not unhelpful,
 * it is backwards. So packs run SPAR and deliberately do not run the
 * source-dropping readout, and the page says why rather than this file alone.
 *
 * A MISSING NUMBER IS MISSING
 * Anything derived from an input the person did not give is ABSENT from the
 * result. Not zero. Software that turns a blank field into a 0 has invented a
 * number, which is the exact thing a mask does, committed by the tool built to
 * name it. A test asserts the row disappears rather than reading nought.
 */
(function (root) {
  "use strict";

  var ENG = root.PLEXUS || (typeof require === "function" ? require("./engines.js") : null);

  var OPS = { "+": true, "-": true, "*": true, "/": true };

  /* ---------------------------------------------------------- validation --- */
  function checkPack(p) {
    var why = [], keys = {}, i;
    if (!p || typeof p !== "object") return ["that is not a pack"];
    if (typeof p.id !== "string" || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(p.id)) {
      why.push("id must be lowercase words joined by hyphens");
    }
    ["title", "about"].forEach(function (k) {
      if (typeof p[k] !== "string" || !p[k].trim()) why.push(k + " is missing");
    });

    /* A pack that hides what it takes for granted is a mask with a form on it.
       The flat-rate assumption is the whole reason a stepped tariff will not
       match, and a person who is not told that will read the difference as an
       accusation. */
    if (!Array.isArray(p.assumes) || !p.assumes.length) {
      why.push((p.id || "the pack") + " declares no assumptions, so nobody can " +
               "tell when it does not apply to them");
    }
    if (!Array.isArray(p.goCheck) || !p.goCheck.length) {
      why.push((p.id || "the pack") + " gives the reader nowhere to go afterwards");
    }

    if (!Array.isArray(p.asks) || !p.asks.length) {
      why.push("a pack has to ask for something");
    } else {
      p.asks.forEach(function (a) {
        if (!a || typeof a.key !== "string" || !a.key) { why.push("an ask has no key"); return; }
        if (keys[a.key]) why.push("two things are called " + a.key);
        keys[a.key] = "ask";
        if (typeof a.label !== "string" || !a.label.trim()) {
          why.push(a.key + " has no label, so nobody knows what to type in it");
        }
      });
    }

    if (!Array.isArray(p.derive) || !p.derive.length) {
      why.push("a pack that derives nothing has nothing to tell anyone");
    } else {
      p.derive.forEach(function (d) {
        if (!d || typeof d.key !== "string" || !d.key) { why.push("a derivation has no key"); return; }
        if (keys[d.key]) why.push("two things are called " + d.key);
        keys[d.key] = "derived";
        if (typeof d.label !== "string" || !d.label.trim()) {
          why.push(d.key + " has no label");
        }
        why = why.concat(checkExpr(d.expr, keys, d.key, p));
      });
    }

    if (p.check) {
      if (!keys[p.check.computed]) why.push("check names an unknown computed value");
      if (!keys[p.check.printed]) why.push("check names an unknown printed value");
    }

    var s = p.structure;
    if (!s || !Array.isArray(s.parts) || !Array.isArray(s.links)) {
      why.push("a pack must carry the structure it fills in");
    }
    return why;
  }

  /* An expression is a prefix array: ["+", a, b, ...] or ["-", a, b].
     + and * take two or more, - and / take exactly two. Everything else is a
     key or a literal number. There is no eval and no parser: a pack is data,
     and data that can run is not data. */
  function checkExpr(e, keys, owner, pack) {
    var why = [];
    if (typeof e === "number") return isFinite(e) ? [] : [owner + " uses a number that is not finite"];
    if (typeof e === "string") {
      if (e === owner) return [owner + " is derived from itself"];
      if (!keys[e]) return [owner + " uses " + e + ", which is not a value in this pack"];
      return [];
    }
    if (!Array.isArray(e) || e.length < 3) {
      return [owner + " has an expression that is not [operator, a, b, ...]"];
    }
    var op = e[0];
    if (!OPS[op]) return [owner + " uses an operator that does not exist: " + op];
    if ((op === "-" || op === "/") && e.length !== 3) {
      why.push(owner + " gives " + op + " more than two things, and it takes two");
    }
    for (var i = 1; i < e.length; i++) why = why.concat(checkExpr(e[i], keys, owner, pack));
    return why;
  }

  /* --------------------------------------------------------- evaluation --- */
  /* Returns { value } or { missing: [keys] } or { refused: "reason" }.
     Never a number it made up. */
  function evaluate(e, values) {
    if (typeof e === "number") return { value: e };
    if (typeof e === "string") {
      if (!(e in values) || values[e] === null || values[e] === undefined) {
        return { missing: [e] };
      }
      return { value: values[e] };
    }
    var op = e[0], parts = [], missing = [], i, r;
    for (i = 1; i < e.length; i++) {
      r = evaluate(e[i], values);
      if (r.refused) return r;
      if (r.missing) { missing = missing.concat(r.missing); continue; }
      parts.push(r.value);
    }
    if (missing.length) return { missing: missing };

    var v;
    if (op === "+") { v = 0; parts.forEach(function (x) { v += x; }); }
    else if (op === "*") { v = 1; parts.forEach(function (x) { v *= x; }); }
    else if (op === "-") { v = parts[0] - parts[1]; }
    else if (op === "/") {
      if (parts[1] === 0) {
        return { refused: "that would divide by zero, and there is no answer to give" };
      }
      v = parts[0] / parts[1];
    }
    if (!isFinite(v)) return { refused: "that does not come out to a number" };
    return { value: v };
  }

  /* ------------------------------------------------------------ the fill --- */
  function fill(pack, given) {
    var why = checkPack(pack);
    if (why.length) return { ok: false, why: why };

    var values = {}, rows = [], missing = [], refused = [];
    (pack.asks || []).forEach(function (a) {
      var v = given ? given[a.key] : undefined;
      if (v === undefined || v === null || v === "") {
        if (!a.optional) missing.push(a.label);
        return;                       /* left OUT of values, never set to 0 */
      }
      var n = typeof v === "number" ? v : parseFloat(String(v).replace(/[\s,]/g, ""));
      if (!isFinite(n)) { refused.push(a.label + " is not a number"); return; }
      values[a.key] = n;
    });

    (pack.derive || []).forEach(function (d) {
      var r = evaluate(d.expr, values);
      if (r.refused) { refused.push(d.label + ": " + r.refused); return; }
      if (r.missing) return;          /* the row simply does not appear */
      values[d.key] = r.value;
      rows.push({ key: d.key, label: d.label, value: r.value, note: d.note || null });
    });

    /* the headline: does the printed figure follow from what was typed */
    var verdict = null;
    if (pack.check && pack.check.computed in values && pack.check.printed in values) {
      var diff = values[pack.check.printed] - values[pack.check.computed];
      var near = Math.abs(diff) < 0.005;   /* half a hundredth: below any real currency unit */
      verdict = {
        computed: values[pack.check.computed],
        printed: values[pack.check.printed],
        difference: diff,
        matches: near,
        /* Deliberately not "they overcharged you". The arithmetic knows only
           that two numbers differ; who is right about the tariff, the reading
           or the law is not in here and cannot be. */
        says: near
          ? "The figure they printed follows from the numbers you typed."
          : (diff > 0
             ? "The figure they printed is " + fmt(Math.abs(diff)) + " more than these parts come to."
             : "The figure they printed is " + fmt(Math.abs(diff)) + " less than these parts come to."),
      };
    }

    return {
      ok: true, why: [], id: pack.id, title: pack.title,
      values: values, rows: rows,
      missing: missing, refused: refused,
      verdict: verdict,
      assumes: pack.assumes.slice(),
      goCheck: pack.goCheck.slice(),
    };
  }

  function fmt(x) {
    var r = Math.round(x * 100) / 100;
    return (Math.abs(r - Math.round(r)) < 1e-9 ? String(Math.round(r)) : String(r));
  }

  /* ---------------------------------------------------------- structure --- */
  /* SPAR only, for the reason set out at the top of this file. */
  function structure(pack) {
    var s = pack.structure;
    var b = ENG.bearings(s.parts, s.links);
    return {
      parts: s.parts.length,
      links: b.links.map(function (r) {
        return { from: r.from, to: r.to, bearing: r.bearing, soleRoute: r.soleRoute };
      }),
      totalBearing: b.total, expected: b.expected, conserved: b.conserved,
      pieces: b.pieces,
      soleRoutes: b.links.filter(function (r) { return r.soleRoute; }).length,
      singlePoints: ENG.singlePoints(s.parts, s.links).map(function (r) { return r.part; }),
      /* stated as data so the page cannot quietly stop saying it */
      whyNoRedundancyReading:
        "Every number here is needed. A bill is a conjunction, and the " +
        "rest-on reading assumes sources that stand in for one another, so it " +
        "would understate what the readings carry rather than overstate it.",
    };
  }

  /* --------------------------------------------------------- the friction -- */
  /* The claim "a pack is less work than the blank canvas", as arithmetic
     instead of as a promise. Numbers typed against parts and links placed. */
  function effort(pack) {
    var asks = (pack.asks || []).length;
    var byHand = (pack.structure.parts || []).length + (pack.structure.links || []).length;
    return {
      id: pack.id, asks: asks, byHand: byHand,
      saved: byHand - asks,
      lessWork: asks < byHand,
    };
  }

  var API = { checkPack: checkPack, checkExpr: checkExpr, evaluate: evaluate,
              fill: fill, structure: structure, effort: effort, fmt: fmt };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.PACKS = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
