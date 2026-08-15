/* readers.js — turn real-world inputs into things the audited engines can check.
 * ============================================================================
 * Every reader here answers one question honestly: WHAT CAN I ACTUALLY EXTRACT?
 * A reader that overstates what it read is worse than no reader, because the
 * engines downstream will treat its output as evidence.
 *
 * Each reader returns { ok, kind, text, records, facts, limits, cannot }.
 *   text     plain text the claim-checker can audit, or ""
 *   records  array of objects a governed learner could take, or []
 *   facts    what was structurally established, never inferred
 *   cannot   what this reader is NOT able to determine. Always populated.
 *
 * *** WHAT NONE OF THESE DO ***
 * None of them understand content. They parse structure. A CSV reader knows a
 * column is numeric; it does not know what the number means. An image reader
 * knows the pixel dimensions; it cannot see what is in the picture. Saying
 * otherwise would be the overclaim this project exists to refuse.
 */
(function (root) {
  "use strict";

  function base(kind) {
    return { ok: false, kind: kind, text: "", records: [], facts: {}, limits: [], cannot: [] };
  }

  // ------------------------------------------------------------ text doc --
  function readTextDocument(name, content) {
    var out = base("document");
    var t = String(content || "");
    if (!t.trim()) {
      out.cannot.push("the file is empty — there is nothing to read");
      return out;
    }
    var words = t.trim().split(/\s+/).filter(Boolean);
    var paras = t.split(/\n\s*\n/).filter(function (p) { return p.trim(); });
    out.ok = true;
    out.text = t;
    out.facts = {
      filename: name, characters: t.length, words: words.length,
      paragraphs: paras.length,
      has_numbers: /\d/.test(t),
      has_links: /https?:\/\//.test(t),
      has_dates: /\b(19|20)\d{2}\b/.test(t)
    };
    out.limits.push("plain text only — formatting, tables and footnotes are lost");
    out.cannot.push("tell whether anything in the document is true");
    out.cannot.push("tell whether the document is complete or has been edited");
    return out;
  }

  // ------------------------------------------------------------------ pdf --
  function readPdfLike(name, bytesHead) {
    var out = base("pdf");
    out.cannot.push(
      "extract text from a PDF. A PDF stores glyph positions, often compressed, " +
      "sometimes as scanned images with no text layer at all. Extracting it " +
      "properly needs a parser this offline page does not carry.");
    out.limits.push("open the PDF, select the text, and paste it in — that path is honest and works");
    out.facts = { filename: name, looks_like_pdf: /^%PDF-/.test(bytesHead || "") };
    return out;
  }

  // ------------------------------------------------------------------ csv --
  function parseCsv(content) {
    // RFC4180-ish: handles quoted fields containing commas and doubled quotes.
    var rows = [], row = [], field = "", inQ = false, i = 0, c;
    var s = String(content || "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
    for (; i < s.length; i++) {
      c = s[i];
      if (inQ) {
        if (c === '"') { if (s[i + 1] === '"') { field += '"'; i++; } else inQ = false; }
        else field += c;
      } else if (c === '"') inQ = true;
      else if (c === ",") { row.push(field); field = ""; }
      else if (c === "\n") { row.push(field); rows.push(row); row = []; field = ""; }
      else field += c;
    }
    if (field.length || row.length) { row.push(field); rows.push(row); }
    return rows.filter(function (r) { return r.length > 1 || (r[0] || "").trim(); });
  }

  function readCsv(name, content) {
    var out = base("dataset");
    var rows = parseCsv(content);
    if (rows.length < 2) {
      out.cannot.push("read this as a dataset — fewer than two rows, so there is no header plus data");
      return out;
    }
    var header = rows[0].map(function (h) { return h.trim(); });
    var body = rows.slice(1).filter(function (r) { return r.length === header.length; });
    var ragged = rows.length - 1 - body.length;

    var records = body.map(function (r) {
      var o = {};
      header.forEach(function (h, j) { o[h] = r[j]; });
      return o;
    });

    var cols = header.map(function (h) {
      var vals = records.map(function (r) { return (r[h] || "").trim(); });
      var nonEmpty = vals.filter(function (v) { return v !== ""; });
      var nums = nonEmpty.filter(function (v) { return v !== "" && isFinite(Number(v)); });
      var numeric = nonEmpty.length > 0 && nums.length === nonEmpty.length;
      var uniq = {};
      nonEmpty.forEach(function (v) { uniq[v] = 1; });
      var c = { name: h, numeric: numeric, missing: vals.length - nonEmpty.length,
                distinct: Object.keys(uniq).length };
      if (numeric && nums.length) {
        var xs = nums.map(Number).sort(function (a, b) { return a - b; });
        c.min = xs[0]; c.max = xs[xs.length - 1];
        c.mean = +(xs.reduce(function (a, b) { return a + b; }, 0) / xs.length).toFixed(4);
        c.median = xs[Math.floor(xs.length / 2)];
      }
      return c;
    });

    out.ok = true;
    out.records = records;
    out.facts = {
      filename: name, rows: records.length, columns: header.length,
      ragged_rows_dropped: ragged, column_summary: cols,
      constant_columns: cols.filter(function (c) { return c.distinct <= 1; }).map(function (c) { return c.name; }),
      columns_with_missing: cols.filter(function (c) { return c.missing > 0; })
        .map(function (c) { return c.name + " (" + c.missing + ")"; })
    };
    out.limits.push("column types are inferred from the values present, not from a schema");
    if (ragged) out.limits.push(ragged + " row(s) had the wrong number of fields and were dropped, not guessed at");
    out.cannot.push("tell whether the numbers are correct, or how they were collected");
    out.cannot.push("tell whether rows are missing entirely — only that fields are blank");
    return out;
  }

  // ----------------------------------------------------------------- image --
  function readImage(name, meta) {
    var out = base("image");
    out.ok = true;
    out.facts = { filename: name, width: meta.width, height: meta.height,
                  bytes: meta.bytes, type: meta.type,
                  megapixels: +((meta.width * meta.height) / 1e6).toFixed(2) };
    out.limits.push("structure and dimensions only");
    out.cannot.push(
      "see what is in the picture. There is no vision model here, and there is " +
      "no offline way to add one. A chart, a contract photo and a cat are the " +
      "same thing to this reader.");
    out.cannot.push("read text in the image — that needs OCR, which is not present");
    out.cannot.push("tell whether the image has been edited or generated");
    return out;
  }

  // ------------------------------------------------------------ transcript --
  // The honest answer to "read a video": you bring the transcript.
  function readTranscript(name, content) {
    var out = base("transcript");
    var t = String(content || "");
    if (!t.trim()) {
      out.cannot.push("nothing was pasted");
      return out;
    }
    // strip common caption timestamps: 00:01:02.500 --> 00:01:05.000, [00:12], 1:23
    var stamps = (t.match(/\d{1,2}:\d{2}(:\d{2})?([.,]\d{1,3})?/g) || []).length;
    var clean = t
      .replace(/^WEBVTT.*$/gm, "")
      .replace(/\d{1,2}:\d{2}(:\d{2})?([.,]\d{1,3})?\s*-->\s*\d{1,2}:\d{2}(:\d{2})?([.,]\d{1,3})?.*$/gm, "")
      .replace(/^\s*\[?\d{1,2}:\d{2}(:\d{2})?\]?\s*/gm, "")
      .replace(/^\s*\d+\s*$/gm, "")
      .replace(/\n{2,}/g, "\n").trim();
    out.ok = clean.length > 0;
    out.text = clean;
    out.facts = { filename: name, timestamps_removed: stamps,
                  words: clean.split(/\s+/).filter(Boolean).length,
                  looks_like_captions: stamps > 3 };
    out.limits.push("auto-generated captions contain transcription errors; those errors are read as if spoken");
    out.cannot.push(
      "fetch a video. This page has no network by design, so it cannot open a " +
      "YouTube link, and there is no honest way to pretend otherwise. Open the " +
      "video, copy the transcript, paste it here.");
    out.cannot.push("see anything shown on screen but not said aloud — slides, charts, captions burned into the picture");
    out.cannot.push("tell who is speaking, or whether the transcript is complete");
    return out;
  }

  // ----------------------------------------------------------------- code --
  // A governance audit of source code: does this code obey the obligations?
  var CODE_CHECKS = [
    { id: "bare_return_of_score",
      re: /return\s+(?:round\s*\(\s*)?[\w.]*(?:score|confidence|rating|risk|prob\w*)\b[^;\n]*$/gim,
      title: "returns a bare score",
      why: "A number returned with no confidence, no reasons and no receipt travels " +
           "downstream looking like a measurement. Nothing carries how it was reached.",
      fix: "Return a verdict object carrying the value, its confidence, the reasons, and a receipt." },
    { id: "reads_self_description",
      re: /["'\[]?\b(?:description|self_?report\w*|self_?desc\w*|bio|blurb|about|summary|claims?)\b["'\]]?\s*[\].)]/gi,
      title: "may consult the subject's own account of itself",
      why: "If an evaluator reads what the thing being judged says about itself, the " +
           "verdict is partly self-assessment. This is the failure the 0.8-vs-0.300 " +
           "example demonstrates.",
      fix: "Delete the field from the record before evaluation, and commit the deletion to the receipt." },
    { id: "no_abstain_path",
      re: /\b(?:def|function)\s+\w*(?:score|assess|evaluate|rate|judge|predict|classif)\w*/gi,
      title: "scoring function — check it can decline",
      why: "A scoring function with no abstain path must answer even when the input " +
           "determines nothing. It will guess, and the guess looks like the answer.",
      fix: "Add an explicit abstain return with reasons, and make it a normal result rather than an exception.",
      needsAbsence: /\b(?:abstain|insufficient|unknown|decline|not_?enough|INCONCLUSIVE)\b/i },
    { id: "silent_except",
      re: /except\s*(?:\w+\s*)?:\s*(?:\n\s*(?:pass|continue)\b)|catch\s*\([^)]*\)\s*\{\s*\}/gi,
      title: "swallows an error silently",
      why: "A swallowed error becomes a missing check nobody can see. The code carries " +
           "on with a value it never validated.",
      fix: "Log it, or convert it into an abstention that says what failed." },
    { id: "magic_threshold",
      re: /(?:[<>]=?)\s*0\.\d{2,}/g,
      title: "hard-coded threshold",
      why: "A threshold in the middle of the code is a decision nobody registered. If it " +
           "was chosen after seeing results, that is invisible here.",
      fix: "Lift it to a named, declared constant, and hash-lock it before the run." },
    { id: "seeded_shuffle_split",
      re: /\b(?:shuffle|train_test_split|sample)\s*\(/gi,
      title: "shuffled data split",
      why: "A shuffle with a changeable seed can be re-rolled until the numbers flatter " +
           "the result, and nobody downstream can tell that it was.",
      fix: "Split deterministically on a hash of the row id, so anyone can recompute which side a row landed on." },
    { id: "self_training",
      re: /\bfit\s*\([^)]*\b(?:pred\w*|self\.\w*out\w*|generated)\b/gi,
      title: "may fit on its own outputs",
      why: "A model trained on its own predictions measures its own consistency, not the world.",
      fix: "Require human or independently-measured labels; refuse model-generated ones." }
  ];

  function auditCode(name, source) {
    var out = base("code");
    var src = String(source || "");
    if (!src.trim()) {
      out.cannot.push("nothing was pasted");
      return out;
    }
    var lines = src.split("\n");
    var findings = [];
    CODE_CHECKS.forEach(function (c) {
      c.re.lastIndex = 0;
      var m, seen = {};
      while ((m = c.re.exec(src)) !== null) {
        if (c.needsAbsence && c.needsAbsence.test(src)) break;
        var line = src.slice(0, m.index).split("\n").length;
        if (seen[line]) continue;
        seen[line] = 1;
        findings.push({ id: c.id, title: c.title, why: c.why, fix: c.fix,
                        line: line, snippet: (lines[line - 1] || "").trim().slice(0, 110) });
        if (findings.filter(function (f) { return f.id === c.id; }).length >= 4) break;
        if (m.index === c.re.lastIndex) c.re.lastIndex++;
      }
    });
    var good = [];
    if (/\b(?:abstain|INCONCLUSIVE|insufficient)\b/i.test(src)) good.push("has an abstain path");
    if (/\b(?:receipt|sha256|hashlib|digest)\b/i.test(src)) good.push("computes a receipt or digest");
    if (/\bblind\b/i.test(src)) good.push("declares blinding");
    if (/\bvif\b/i.test(src)) good.push("checks independence");
    if (/\bprereg|locked|\.lock\b/i.test(src)) good.push("references a pre-registration lock");

    out.ok = true;
    out.facts = { filename: name, lines: lines.length, findings: findings,
                  governance_signals_present: good,
                  checks_run: CODE_CHECKS.length };
    out.limits.push("pattern matching over source text — it does not parse or execute the code");
    out.cannot.push("tell whether the code is correct, secure, or does what it claims");
    out.cannot.push("find a problem it has no pattern for; a clean result means 'none of these " +
                    CODE_CHECKS.length + " patterns matched', never 'this code is fine'");
    out.cannot.push("distinguish a real finding from a false positive — every line is for a human to judge");
    return out;
  }

  // -------------------------------------------------------------- planner --
  // A project plan, structured so each step declares what would show it worked.
  function planProject(goal, constraints) {
    var out = base("plan");
    var g = String(goal || "").trim();
    if (g.split(/\s+/).filter(Boolean).length < 4) {
      out.cannot.push("plan from fewer than four words — there is no goal here to decompose");
      return out;
    }
    var risky = /\b(health|medic\w*|clinical|legal|financial|money|safety|child|dose|contract|tax|immigration)\b/i.test(g);
    var steps = [
      { phase: "State it as a claim",
        do_: "Write the goal as something that could be false: \"" + g + "\" succeeds if …",
        evidence: "A single sentence a stranger could check without asking you what you meant.",
        gate: "If you cannot finish that sentence, the project is not yet defined." },
      { phase: "Write the gate before you start",
        do_: "Decide now what result would mean this did NOT work.",
        evidence: "A number or an observable event, fixed in advance and written down.",
        gate: "A project with no failure condition cannot be evaluated, only narrated." },
      { phase: "Name your two independent checks",
        do_: "Find two sources of evidence that do not come from the same place.",
        evidence: "Two checks whose failure modes differ.",
        gate: "If both come from the same source you have one check and twice the confidence." },
      { phase: "Decide what you will not look at",
        do_: "List what must be excluded to keep the judgement honest — a vendor's own claims, your own earlier estimate.",
        evidence: "A written exclusion list.",
        gate: "Applied before you gather evidence, not after." },
      { phase: "Smallest reversible step",
        do_: "Do the smallest version that could still fail informatively.",
        evidence: "A result you could show someone.",
        gate: "If the first step is irreversible, the plan is a bet, not a project." },
      { phase: "Check against the gate you set",
        do_: "Compare the result to the failure condition written in step 2.",
        evidence: "The comparison, recorded with its date.",
        gate: "Moving the gate now invalidates everything before it." },
      { phase: "Record what happened",
        do_: "Log the outcome including what did not work.",
        evidence: "An append-only note with the date.",
        gate: "A record only of successes is a record of nothing." }
    ];
    out.ok = true;
    out.facts = { goal: g, constraints: String(constraints || "").trim(), steps: steps,
                  risk_flagged: risky };
    out.limits.push("a structure, not domain advice — it does not know your field");
    out.cannot.push("tell you whether the goal is worth pursuing, achievable, or wise");
    out.cannot.push("estimate cost or duration; nothing here knows your situation");
    if (risky) out.cannot.push(
      "substitute for a qualified professional. This goal touches an area where a " +
      "well-structured plan and a safe plan are different things.");
    return out;
  }

  // ----------------------------------------------------------- dispatcher --
  function readFile(name, content, meta) {
    var n = String(name || "").toLowerCase();
    if (/\.csv$|\.tsv$/.test(n)) return readCsv(name, content);
    if (/\.pdf$/.test(n)) return readPdfLike(name, String(content || "").slice(0, 8));
    if (/\.(png|jpe?g|gif|webp|bmp|svg)$/.test(n)) return readImage(name, meta || {});
    if (/\.(vtt|srt)$/.test(n)) return readTranscript(name, content);
    if (/\.(js|mjs|ts|py|java|go|rb|rs|c|cpp|cs|php|sh)$/.test(n)) return auditCode(name, content);
    return readTextDocument(name, content);
  }

  var API = { readTextDocument: readTextDocument, readPdfLike: readPdfLike,
              readCsv: readCsv, parseCsv: parseCsv, readImage: readImage,
              readTranscript: readTranscript, auditCode: auditCode,
              planProject: planProject, readFile: readFile,
              CODE_CHECKS: CODE_CHECKS };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  else root.READERS = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
