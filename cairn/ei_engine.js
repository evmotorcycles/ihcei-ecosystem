/* ei_engine.js -- faithful JS port of cairn/ei_llm.py's assay().
 *
 * This exists so the browser app runs the SAME logic as the audited Python
 * engine, with no server and no network. Parity is not assumed: it is tested by
 * cairn/test_parity.py, which runs both engines over a shared case list and
 * fails if any verdict, claim type, confidence or evidence count differs.
 *
 * Same limits as the Python engine, restated so nobody reads the port as an
 * upgrade: this does NOT understand language. Ambiguity detection is syntactic
 * pattern matching and the plausibility check reads a hand-written list of 15
 * landform nouns.
 */
(function (root) {
  "use strict";

  var EVIDENCE = [
    ["source", /\b(according to|source|cited|reference|study|report|dataset|https?:\/\/|\.gov|\.org|doi)\b/i,
      "A checkable source is named", "No source is named"],
    ["figures", /\d/, "Contains specific figures", "No specific figures given"],
    ["method", /\b(method|measured|sample|n\s*=|survey|trial|audit|tested|compared|control|logs?)\b/i,
      "Says how it was measured", "Does not say how it was measured"],
    ["time", /\b(19|20)\d{2}\b|\b(today|yesterday|last (year|month|quarter)|q[1-4])\b/i,
      "Anchored to a date or period", "No date or period given"],
    ["scope", /\b(in|across|among|between|per|for)\b[\s\S]{0,28}\b(uk|us|eu|africa|asia|region|country|sector|team|school|hospital|company|cities|clinics)\b/i,
      "States who or where it applies", "Scope is not stated"]
  ];

  var IMMOBILE = ["canyon", "grand canyon", "mountain", "mountains", "valley", "plateau",
    "cliff", "lake", "river", "desert", "glacier", "volcano", "island", "coastline", "forest"];
  var SELF_PROPELLED = ["flying", "walking", "running", "driving", "swimming",
    "travelling", "traveling", "climbing"];

  var ATTACH_RE = /^\s*(i|we|he|she|they|you)\s+(\w+)\s+(the|a|an|my|our|his|her|their)\s+([\w\s]{2,40}?)\s+(\w+ing)\b([\s\S]*)$/i;
  var CONCEPTUAL_RE = /(\bis (the|a|an) (study|branch|theory|field|concept|term|word|practice|process|state|quality)\b|\bis defined as\b|\bmeans\b|\brefers to\b|\bdefinition of\b|\bby definition\b|^\s*\w+\s*[:—-]\s*(the|a|an)\b)/i;
  var MATHY_RE = /^\s*[\d\s()+\-*/^=.]+\s*$/;
  var OPINION_RE = /\b(i think|i believe|in my opinion|i feel|should be|ought to|is better than|is the best|is amazing|is terrible|prefer)\b/i;
  var QUESTION_RE = /^\s*(what|who|when|where|why|how|is|are|do|does|did|can|could|should|would|will)\b[\s\S]*\?\s*$/i;
  var IMPERATIVE_RE = /^\s*(mix|add|combine|apply|take|use|heat|stir|install|run|pour|dissolve|blend)\b/i;

  var DOMAIN_RISK = [
    ["chemistry/formulation", /\b(acid|ph\b|emulsif|oil|solvent|dissolve|concentration|serum|formulation|mix(ing)?|bleach|ammonia)\b/i],
    ["medical/health", /\b(dose|dosage|mg\b|ml\b|supplement|treatment|symptom|diagnos|medication|serum|skin|ingest|therapy|clinical trial|metabolic|nutrition|placebo|patient|participants|infect\w*|outbreak|epidemic|pandemic|bacteri\w*|virus|viral|fungal|parasit\w*|contagio\w*|antibiotic|antimicrobial|pathogen\w*|contaminat\w*|quarantine|measles|cholera|influenza|bird flu|covid|death[s]?|died|dying|fatal\w*|mortality|lethal|survive|survival|kill(s|ed)?|life-threatening|amputat\w*|wound[s]?|illness|disease|disorder|syndrome|cancer|tumou?r|malignan\w*|biopsy|carcinom\w*|diabet\w*|blood pressure|cholesterol|kidney|cardiac|stroke|asthma|vaccin\w*|immunis\w*|immuniz\w*|booster|screening|hospital\w*|clinic\w*|doctor|nurse|prescription|fever|nausea)\b/i],
    ["legal/regulatory", /\b(contract|clause|liabilit\w*|complian\w*|regulat\w*|statute|gdpr|licen[cs]e|jurisdiction|appeal|waive[sd]?|legal|lawsuit|court|breach|terminat\w*|disclos\w*|entitle\w*|tribunal)\b/i],
    ["financial", /\b(revenue|profit|forecast|invest\w*|valuation|roi\b|interest rate|loan|credit|guaranteed returns?|returns? of|pension|tax|apr\b|mortgage|debt|refund|deposit|payment|withdraw\w*)\b/i],
    ["safety-critical", /\b(voltage|electrical|structural|load-bearing|pressure|gas|flammable|dosing|carbon monoxide|scaffold\w*|toxic|fumes|corrosive|explosi\w*|asbestos|brake[s]?|overheat\w*|wiring|flue|ventilat\w*|pesticide|solvent)\b/i]
  ];

  function classifyClaim(text) {
    var t = (text || "").trim();
    if (!t) return ["EMPTY", "Nothing to look at yet."];
    if (QUESTION_RE.test(t)) return ["QUESTION",
      "That's a question, not a claim. I audit statements — paste an answer you've been given and I'll tell you how far it can be trusted."];
    if (MATHY_RE.test(t)) return ["CONCEPTUAL",
      "That's arithmetic. It's true by definition, so there's nothing for me to verify against the world."];
    if (CONCEPTUAL_RE.test(t) && !/\d/.test(t)) return ["CONCEPTUAL",
      "That's a definition or a concept. Definitions are true by agreement, not by measurement — so there's no source, date or figure for me to check. This isn't a failure; it's simply outside what I audit."];
    if (OPINION_RE.test(t)) return ["OPINION",
      "That's a preference or a judgement. I can't audit what someone values — only claims about what is measurably the case."];
    if (IMPERATIVE_RE.test(t)) return ["INSTRUCTION",
      "That's a set of instructions. I can check whether it's specified precisely enough to follow — but NOT whether following it is safe or correct."];
    return ["EMPIRICAL", ""];
  }

  function domainFlags(text) {
    var out = [];
    for (var i = 0; i < DOMAIN_RISK.length; i++) {
      if (DOMAIN_RISK[i][1].test(text || "")) out.push(DOMAIN_RISK[i][0]);
    }
    return out;
  }

  function scoreEvidence(text) {
    return EVIDENCE.map(function (e) {
      var hit = e[1].test(text || "");
      return { signal: e[0], hit: hit, note: hit ? e[2] : e[3] };
    });
  }

  /* ------------------------------------------------------------- handles ---
   * A tick saying "contains specific figures" leaves the reader to find the
   * figures themselves. The handles are the SPANS that made each signal fire --
   * the exact words someone would paste into a search engine to go and check.
   * Strictly additional: same signals, same hits, plus the causing text. */
  var FIGURE_RX = /\d[\d,.]*(?:\s*(?:%|percent))?(?:\s+[a-z][a-z-]{2,20})?/gi;
  var YEAR_RX = /\b(?:19|20)\d{2}\b|\b(?:today|yesterday|last (?:year|month|quarter)|q[1-4])\b/gi;
  var METHOD_RX = /\b(?:[a-z-]+\s+)?(?:method|measured|sample|n\s*=|survey|trial|audit|tested|compared|control|logs?)\b/gi;
  var SCOPE_RX = /\b(?:in|across|among|between|per|for)\b.{0,28}?\b(?:uk|us|eu|africa|asia|region|country|sector|team|school|hospital|company|cities|clinics)\b/gi;
  var SOURCE_RX = /\b(?:according to|source|cited|reference|study|report|dataset|doi)\b|https?:\/\/\S+|\b\S+\.(?:gov|org)\b/gi;
  /* A source MARKER ("according to") is not a source NAME. The distinction only
   * becomes visible once the span is shown, which is the point of showing it. */
  var NAMED_RX = /https?:\/\/\S+|\bdoi\b|\b\S+\.(?:gov|org)\b|\b(?:the )?[A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*\s+(?:Journal|Review|Times|Post|University|Institute|Office|Agency|Association|Society)\b|\b(?:Nature|Science|Lancet|BMJ|JAMA|NEJM|WHO|CDC|NHS|ONS|OECD|NASA)\b/g;
  var STOP = ["a","an","the","of","in","on","at","by","to","and","or","was","were","is","are"];

  function spans(rx, text, limit) {
    var out = [], m;
    rx.lastIndex = 0;
    while ((m = rx.exec(text || "")) !== null) {
      var s = m[0].replace(/^[\s,.;:]+|[\s,.;:]+$/g, "");
      if (s && STOP.indexOf(s.toLowerCase()) === -1 && out.indexOf(s) === -1) out.push(s);
      if (out.length >= limit) break;
      if (m.index === rx.lastIndex) rx.lastIndex++;
    }
    return out;
  }

  function extractHandles(text) {
    text = text || "";
    var all = spans(FIGURE_RX, text, 6);
    var figures = all.filter(function (s) { return !/^(?:19|20)\d{2}$/.test(s.split(/\s+/)[0]); });
    if (!figures.length) figures = all;
    var method = [], mm;
    METHOD_RX.lastIndex = 0;
    while ((mm = METHOD_RX.exec(text)) !== null) {
      var s = mm[0].trim(), first = s.split(/\s+/)[0].toLowerCase();
      if (s.split(/\s+/).length > 1 && STOP.indexOf(first) !== -1) s = s.split(/\s+/).slice(1).join(" ");
      if (method.indexOf(s) === -1) method.push(s);
      if (mm.index === METHOD_RX.lastIndex) METHOD_RX.lastIndex++;
    }
    var src = spans(SOURCE_RX, text, 3);
    spans(NAMED_RX, text, 2).forEach(function (s) { if (src.indexOf(s) === -1) src.push(s); });
    return {
      source: src, figures: figures, method: method.slice(0, 3),
      time: spans(YEAR_RX, text, 3), scope: spans(SCOPE_RX, text, 3),
      // Reported, never scored.
      source_named: (NAMED_RX.lastIndex = 0, NAMED_RX.test(text))
    };
  }

  function searchLine(h) {
    var parts = [];
    ["time", "figures", "method", "scope"].forEach(function (k) {
      (h[k] || []).forEach(function (s) { if (parts.indexOf(s) === -1) parts.push(s); });
    });
    return parts.join(" ");
  }

  function nextSteps(checks, kind) {
    if (kind === "QUESTION") return ["Paste the answer you were given, and I'll audit that instead."];
    if (kind === "CONCEPTUAL" || kind === "OPINION") return [
      "Add a measurement, a date or a source and it becomes something I can check.",
      "For definitions, an ordinary assistant or a dictionary is the right tool."];
    var fix = {
      source: "Name where it came from — a study, a report, a link.",
      figures: "Add the actual numbers.",
      method: "Say how it was measured.",
      time: "Add when it was measured.",
      scope: "Say who or where it applies to."
    };
    var missing = checks.filter(function (c) { return !c.hit; }).slice(0, 3)
      .map(function (c) { return fix[c.signal]; });
    return missing.length ? missing : ["Nothing material is missing."];
  }

  function inImmobile(s) {
    if (IMMOBILE.indexOf(s) !== -1) return true;
    return s.split(/\s+/).some(function (w) { return IMMOBILE.indexOf(w) !== -1; });
  }

  function detectAmbiguity(text) {
    var t = (text || "").trim().replace(/\.+$/, "");
    var m = ATTACH_RE.exec(t);
    if (!m) return { ambiguous: false, readings: [], pattern: null };
    var subj = m[1], verb = m[2], obj = m[4].trim(), part = m[5], rest = m[6].trim();
    var objKey = obj.toLowerCase().trim();
    var objImmobile = inImmobile(objKey);
    var partMoves = SELF_PROPELLED.indexOf(part.toLowerCase()) !== -1;
    return {
      ambiguous: true, pattern: "participial attachment", object: obj, participle: part,
      object_in_immobile_lexicon: objImmobile,
      readings: [
        { id: "A", attaches_to: "subject",
          paraphrase: (subj + " was " + part + " " + rest + ", and " + subj + " " + verb + " the " + obj).trim(),
          plausible: true, why: "The subject is an agent, so it can perform the action." },
        { id: "B", attaches_to: "object",
          paraphrase: (subj + " " + verb + " the " + obj + ", and the " + obj + " was " + part + " " + rest).trim(),
          plausible: !(objImmobile && partMoves),
          why: (objImmobile && partMoves)
            ? "'" + obj + "' is in the declared immobile-landform lexicon and '" + part + "' is self-propelled motion, so this reading is physically implausible."
            : "Both the object and the action are ordinary, so this reading is perfectly possible." }
      ]
    };
  }

  function checkImpossible(text) {
    var t = (text || "").trim().replace(/\.+$/, "");
    var m = /^\s*(the\s+)?([\w\s]{2,40}?)\s+(was|is|were|are)\s+(\w+ing)\b/i.exec(t);
    if (!m) return null;
    var obj = m[2].trim().toLowerCase(), part = m[4].toLowerCase();
    if (inImmobile(obj) && SELF_PROPELLED.indexOf(part) !== -1) {
      return { implausible: true, subject: obj, action: part,
        basis: "declared immobile-landform lexicon (a hand-written list of " + IMMOBILE.length + " nouns), NOT comprehension" };
    }
    return null;
  }

  function assay(text, model) {
    model = model || "slate";
    text = (text || "").trim();
    var kr = classifyClaim(text), kind = kr[0], kindNote = kr[1];
    var checks = scoreEvidence(text);
    var hits = checks.filter(function (c) { return c.hit; }).length;
    var hnd = extractHandles(text);
    var words = text ? text.split(/\s+/).length : 0;
    var amb = detectAmbiguity(text);
    var impossible = checkImpossible(text);
    var domains = domainFlags(text);

    if (kind === "CONCEPTUAL" || kind === "OPINION" || kind === "QUESTION" || kind === "EMPTY") {
      return {
        input: text, model: model, verdict: "OUT_OF_SCOPE", claim_type: kind,
        committed_answer: null, confidence: null, band: "not applicable",
        evidence: [], evidence_hits: 0, evidence_total: EVIDENCE.length,
        handles: hnd, search_line: searchLine(hnd),
        ambiguity: amb, implausible: null, domain_flags: domains,
        explanation: kindNote, question: null, next_steps: nextSteps(checks, kind),
        abstained: false, engine: "cairn-ei/1.1 (js)",
        limits: "Out of scope is not a failure. I audit empirical claims; this text is not one."
      };
    }

    var conf = hits / EVIDENCE.length;
    if (words < 4) conf = 0.0;
    if (model === "granite" || model === "quartz") conf = Math.min(1.0, conf * 1.12);
    if (amb.ambiguous) conf = Math.min(conf, 0.35);

    var verdict, committed, question = null;
    if (amb.ambiguous) {
      verdict = "AMBIGUOUS"; committed = null;
      question = "Which did you mean: were you " + amb.participle + ", or was the " + amb.object + " " + amb.participle + "?";
    } else if (impossible) {
      verdict = "IMPLAUSIBLE"; committed = null;
      question = "Did you mean this literally, or is a word missing?";
    } else if (conf < 0.25) {
      verdict = "INSUFFICIENT_EVIDENCE"; committed = null;
      question = "Add a source, a figure, a date, a method or a scope and I can work with it.";
    } else {
      verdict = "SUPPORTED"; committed = text;
    }

    var band = conf >= 0.7 ? "high" : conf >= 0.45 ? "moderate" : conf >= 0.25 ? "low" : "insufficient";
    return {
      input: text, model: model, verdict: verdict, claim_type: kind,
      committed_answer: committed, confidence: Math.round(conf * 1000) / 1000, band: band,
      evidence: checks, evidence_hits: hits, evidence_total: EVIDENCE.length,
      handles: hnd, search_line: searchLine(hnd),
      ambiguity: amb, implausible: impossible, domain_flags: domains,
      explanation: kindNote, question: question, next_steps: nextSteps(checks, kind),
      abstained: committed === null, engine: "cairn-ei/1.1 (js)",
      limits: "This engine does not understand language. Ambiguity detection is pattern matching; plausibility reads a hand-written list of " + IMMOBILE.length + " landform nouns."
    };
  }

  var API = { assay: assay, classifyClaim: classifyClaim, domainFlags: domainFlags,
    scoreEvidence: scoreEvidence, extractHandles: extractHandles, searchLine: searchLine,
    IMMOBILE: IMMOBILE, EVIDENCE_N: EVIDENCE.length };

  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.EI = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
