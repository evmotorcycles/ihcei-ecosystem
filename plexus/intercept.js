/* intercept.js -- the AI interceptor kernel. No interface, no network, ever.
 * ===========================================================================
 * WHAT THIS DOES AND WHAT IT MUST NEVER BE SAID TO DO
 * You paste what an assistant told you. It reports what in that text could be
 * checked, which check to do first, and which of the ten things a workable plan
 * has to settle were never mentioned.
 *
 * It does NOT make anybody safe. It cannot read the text, it knows no chemistry,
 * no medicine, no law and no finance, and it certifies nothing. What it does is
 * refuse to let an unverifiable step be treated as settled. A person still has
 * to go and check, and for anything that can hurt them, ask somebody qualified.
 * Every one of those sentences is printed on the page and asserted by a test:
 * an interceptor that implies safety is a mask worn by the tool built to name
 * masks.
 *
 * THE TEN, WITH THE VOCABULARY LEFT OUT
 * The governance reading this stack draws on lists ten things any working order
 * has to settle. They transfer to a plan with no terminology attached at all,
 * and a plan missing most of them is not a plan, it is a paragraph:
 *
 *    1 terms          what each word means here, exactly
 *    2 roles          who does which part
 *    3 dues           what is owed, by whom, and when
 *    4 boundaries     what may be touched and what may not
 *    5 rules          the constraints that must hold
 *    6 standards      what counts as done properly
 *    7 steps          the order things happen in
 *    8 consequences   what happens when a step fails
 *    9 where          the scope it applies to
 *   10 exceptions     the cases that do not follow the rest
 *
 * Detection is lexical and is a SUGGESTION, exactly as the five marks are. It
 * matches words; it does not read. A person adds or strikes any of them.
 *
 * WHAT IS MEASURED AND WHAT IS COUNTED
 * The measuring is press.js: same graph, same engine, same 1/m^2. The ten are
 * COUNTED, not measured, and the two are reported apart. A count of ten
 * keywords is not a measurement and calling it one would be the whole failure.
 */
(function (root) {
  "use strict";

  var PRESS = root.PRESS || (typeof require === "function" ? require("./press.js") : null);
  var EI = root.EI || (typeof require === "function" ? require("../cairn/ei_engine.js") : null);

  var TEN = [
    ["terms", /\b(means|defined as|refers to|that is,|i\.e\.|by ["']?[a-z ]+["']? we mean)\b/i,
     "what each word means here"],
    ["roles", /\b(you|your|the (user|client|customer|supplier|landlord|employer|doctor|pharmacist)|who (is|will)|responsible|assigned)\b/i,
     "who does which part"],
    ["dues", /\b(owe|owed|pay|cost|price|fee|charge|due|invoice|refund|deposit)\b/i,
     "what is owed, by whom"],
    ["boundaries", /\b(do not|don't|never|only|must not|avoid|limit|no more than|at most|permission|allowed)\b/i,
     "what may be touched and what may not"],
    /* `%` sits OUTSIDE the \b(...)\b group. Inside it, it never fires: a percent
       sign is a non-word character, so "30% glycolic" has no word boundary after
       the % and the alternation silently fails. Found by running it on a
       concentration, which is exactly the case the flag exists for. */
    ["rules", /\b(must|required|shall|has to|ratio|per cent|percent|ph|maximum|minimum|no less than)\b|%/i,
     "the constraints that must hold"],
    ["standards", /\b(quality|standard|specification|grade|tolerance|acceptable|correct|verified|tested)\b/i,
     "what counts as done properly"],
    ["steps", /\b(first|then|next|after|finally|step \d|\d\.\s|stage)\b/i,
     "the order things happen in"],
    ["consequences", /\b(if .{0,40}(fails?|goes wrong|does not|doesn't)|otherwise|else|risk|danger|harm|burn|damage|penalty)\b/i,
     "what happens when a step fails"],
    ["where", /\b(in |across |within |for |applies to |jurisdiction|country|region|state|only in)\b/i,
     "the scope it applies to"],
    ["exceptions", /\b(except|unless|apart from|other than|does not apply|edge case|but if)\b/i,
     "the cases that do not follow the rest"],
  ];

  /* Domains where being wrong hurts. Deliberately blunt and deliberately
     over-inclusive: a false alarm costs somebody a sentence of reading, and a
     miss costs something that cannot be undone. */
  var RISK = [
    ["health", /\b(dose|dosage|mg\b|ml\b|medicine|drug|tablet|treat|symptom|diagnos|skin|serum|acid|peel|allerg|pregnan|infant|wound|infection)\b/i,
     "a pharmacist, doctor or nurse"],
    ["chemicals", /\b(mix|dilute|concentration|ph\b|acid|alkali|bleach|ammonia|solvent|reagent|ratio|formulat)\b/i,
     "somebody who handles these materials for a living"],
    ["money", /\b(invest|loan|interest|tax|refund|deposit|mortgage|pension|crypto|shares|returns?)\b/i,
     "a qualified financial or tax adviser"],
    ["law", /\b(contract|clause|liable|liability|sue|court|legal|rights|notice period|tenancy|eviction|visa)\b/i,
     "somebody qualified in the law where you live"],
    ["safety", /\b(electric|wiring|gas\b|voltage|ladder|structural|load-bearing|brake|scaffold)\b/i,
     "a qualified tradesperson or engineer"],
  ];

  function marksIn(text) {
    var hits = EI.scoreEvidence(text).filter(function (c) { return c.hit; });
    var h = EI.extractHandles(text);
    return { kinds: hits.map(function (c) { return c.signal; }), handles: h,
             origin: (h.source && h.source.length) ? h.source[0] : null };
  }

  function ten(text) {
    var t = String(text || "");
    return TEN.map(function (row) {
      return { key: row[0], present: row[1].test(t), asks: row[2] };
    });
  }

  function risks(text) {
    var t = String(text || ""), out = [];
    RISK.forEach(function (r) {
      if (r[1].test(t)) out.push({ domain: r[0], ask: r[2] });
    });
    return out;
  }

  function intercept(text, struck) {
    var t = String(text || "").trim();
    struck = struck || {};
    if (!t) return { empty: true };

    var f = marksIn(t);
    var kinds = f.kinds.filter(function (k) { return !struck[k]; });
    var pressed = PRESS.press(kinds.map(function (k) {
      return { kind: k, origin: f.origin };
    }));

    var rows = ten(t);
    var settled = rows.filter(function (r) { return r.present; });
    var missing = rows.filter(function (r) { return !r.present; });
    var flags = risks(t);

    return {
      empty: false,
      handles: { of: 5, found: kinds.length, kinds: kinds, spans: f.handles },
      pressed: pressed,
      ten: { rows: rows, settled: settled.length, missing: missing },
      flags: flags,
      /* Never fused. The handles are measured; the ten are counted; the flags
         are pattern matches. Three different kinds of thing and no arithmetic
         combines them honestly. */
      limits: [
        "This does not understand what you pasted.",
        "This does not certify that anything is safe.",
        "A claim that is completely made up reads exactly like a true one here.",
      ],
    };
  }

  var API = { intercept: intercept, ten: ten, risks: risks, marksIn: marksIn,
              TEN: TEN, RISK: RISK };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.INTERCEPT = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
