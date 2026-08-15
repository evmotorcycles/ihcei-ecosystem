/* node --test readers/readers.test.mjs
 *
 * These guard the thing that matters most about a reader: that it says what it
 * CANNOT do. A reader that overstates what it read is worse than no reader,
 * because everything downstream treats its output as evidence.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";

const here = dirname(fileURLToPath(import.meta.url));
const R = createRequire(import.meta.url)(join(here, "readers.js"));

test("every reader populates `cannot` — none may claim to do everything", () => {
  const results = [
    R.readTextDocument("a.txt", "Some text with 2023 and a number 42."),
    R.readCsv("d.csv", "a,b\n1,2\n3,4\n"),
    R.readImage("p.png", { width: 800, height: 600, bytes: 1234, type: "image/png" }),
    R.readTranscript("v.vtt", "WEBVTT\n00:00:01.000 --> 00:00:03.000\nHello there everyone."),
    R.auditCode("x.py", "def score(x):\n    return round(score, 3)\n"),
    R.planProject("Launch a small community newsletter", ""),
    R.readPdfLike("f.pdf", "%PDF-1.7")
  ];
  for (const r of results) {
    assert.ok(r.cannot.length > 0, `${r.kind} must declare what it cannot do`);
  }
});

// ------------------------------------------------------------------- csv --
test("csv: parses quoted fields containing commas", () => {
  const r = R.readCsv("t.csv", 'name,note\n"Smith, John",ok\n"He said ""hi""",fine\n');
  assert.equal(r.records.length, 2);
  assert.equal(r.records[0].name, "Smith, John");
  assert.equal(r.records[1].name, 'He said "hi"');
});

test("csv: ragged rows are dropped and REPORTED, not silently guessed at", () => {
  const r = R.readCsv("t.csv", "a,b,c\n1,2,3\n4,5\n6,7,8\n");
  assert.equal(r.records.length, 2);
  assert.equal(r.facts.ragged_rows_dropped, 1);
  assert.ok(r.limits.some(l => l.includes("not guessed at")));
});

test("csv: numeric detection and missing counts are structural, not inferred", () => {
  const r = R.readCsv("t.csv", "n,s,blank\n1,x,\n2,y,\n3,z,\n");
  const cols = Object.fromEntries(r.facts.column_summary.map(c => [c.name, c]));
  assert.equal(cols.n.numeric, true);
  assert.equal(cols.s.numeric, false);
  assert.equal(cols.blank.missing, 3);
  assert.equal(cols.n.min, 1);
  assert.equal(cols.n.max, 3);
});

test("csv: a file with only a header cannot be read as a dataset", () => {
  const r = R.readCsv("t.csv", "a,b,c\n");
  assert.equal(r.ok, false);
  assert.ok(r.cannot[0].includes("fewer than two rows"));
});

// ----------------------------------------------------------------- image --
test("image: refuses to claim it can see the picture", () => {
  const r = R.readImage("chart.png", { width: 1920, height: 1080, bytes: 900, type: "image/png" });
  assert.equal(r.facts.megapixels, 2.07);
  const cannot = r.cannot.join(" ");
  assert.ok(cannot.includes("see what is in the picture"));
  assert.ok(cannot.includes("no vision model"));
  assert.ok(cannot.includes("OCR"));
  assert.equal(r.text, "", "an image reader must not emit text it did not read");
});

// ------------------------------------------------------------------ pdf --
test("pdf: declines rather than emitting garbage text", () => {
  const r = R.readPdfLike("report.pdf", "%PDF-1.4");
  assert.equal(r.ok, false);
  assert.equal(r.text, "");
  assert.ok(r.cannot[0].includes("extract text from a PDF"));
  assert.ok(r.limits[0].includes("paste it in"), "it must offer the honest path that works");
});

// ------------------------------------------------------------ transcript --
test("transcript: strips caption timestamps and keeps the words", () => {
  const vtt = "WEBVTT\n\n1\n00:00:01.000 --> 00:00:04.000\nThe study found a 12% drop.\n\n" +
              "2\n00:00:04.000 --> 00:00:07.000\nAcross 240 participants.";
  const r = R.readTranscript("t.vtt", vtt);
  assert.ok(r.ok);
  assert.ok(r.text.includes("The study found a 12% drop."));
  assert.ok(!r.text.includes("-->"));
  assert.equal(r.facts.looks_like_captions, true);
});

test("transcript: states plainly that it cannot fetch a video", () => {
  const r = R.readTranscript("t.vtt", "hello there this is a talk");
  const cannot = r.cannot.join(" ");
  assert.ok(cannot.includes("fetch a video"));
  assert.ok(cannot.includes("no network by design"));
  assert.ok(cannot.includes("no honest way to pretend otherwise"));
  assert.ok(cannot.includes("shown on screen but not said aloud"));
});

// ------------------------------------------------------------------ code --
test("code audit: catches a bare score return", () => {
  const r = R.auditCode("m.py", "def rate(x):\n    score = x * 2\n    return round(score, 3)\n");
  assert.ok(r.facts.findings.some(f => f.id === "bare_return_of_score"));
});

test("code audit: catches reading the subject's own description", () => {
  const r = R.auditCode("m.py",
    'def check(p):\n    s = p["forks"] / p["stars"]\n    if "best" in p["description"].lower():\n        s += 0.5\n    return s\n');
  assert.ok(r.facts.findings.some(f => f.id === "reads_self_description"));
});

test("code audit: a scoring function WITH an abstain path is not flagged for it", () => {
  const withAbstain = 'def assess(x):\n    if not x: return abstain("nothing to assess")\n    return support(0.5, "ok")\n';
  const without = "def assess(x):\n    return 0.5\n";
  assert.ok(!R.auditCode("a.py", withAbstain).facts.findings.some(f => f.id === "no_abstain_path"));
  assert.ok(R.auditCode("b.py", without).facts.findings.some(f => f.id === "no_abstain_path"));
});

test("code audit: catches a silently swallowed error", () => {
  const r = R.auditCode("m.py", "try:\n    risky()\nexcept Exception:\n    pass\n");
  assert.ok(r.facts.findings.some(f => f.id === "silent_except"));
});

test("code audit: catches a shuffled split and a self-training fit", () => {
  const r = R.auditCode("m.py", "X_tr, X_te = train_test_split(X, y)\nmodel.fit(X, predictions)\n");
  const ids = r.facts.findings.map(f => f.id);
  assert.ok(ids.includes("seeded_shuffle_split"));
  assert.ok(ids.includes("self_training"));
});

test("code audit: recognises governance signals when they ARE present", () => {
  const good = 'def assess(r):\n    # blind the self-report, check vif, receipt it\n' +
    '    if thin: return abstain("insufficient")\n    h = hashlib.sha256(b"x").hexdigest()\n' +
    '    vif_ok = vif(a, b) < 5\n    return support(0.6, "ok", receipt=h)\n';
  const r = R.auditCode("g.py", good);
  assert.ok(r.facts.governance_signals_present.length >= 3);
});

test("code audit: a clean result is never reported as 'this code is fine'", () => {
  const r = R.auditCode("clean.py", "def add(a, b):\n    return a + b\n");
  const cannot = r.cannot.join(" ");
  assert.ok(cannot.includes("never 'this code is fine'"));
  assert.ok(cannot.includes("correct, secure"));
  assert.ok(cannot.includes("false positive"));
});

// ------------------------------------------------------------------ plan --
test("plan: every step declares evidence and a gate", () => {
  const r = R.planProject("Move our customer records to a new provider", "budget is fixed");
  assert.ok(r.ok);
  assert.equal(r.facts.steps.length, 7);
  for (const s of r.facts.steps) {
    assert.ok(s.phase && s.do_ && s.evidence && s.gate);
  }
});

test("plan: the gate comes before the work, not after", () => {
  const r = R.planProject("Launch a small community newsletter next month", "");
  const idxGate = r.facts.steps.findIndex(s => /before you start/i.test(s.phase));
  const idxDo = r.facts.steps.findIndex(s => /reversible step/i.test(s.phase));
  assert.ok(idxGate >= 0 && idxDo > idxGate, "writing the gate must precede doing the work");
});

test("plan: flags domains where structure is not safety", () => {
  const r = R.planProject("Change my father's medication schedule at home", "");
  assert.equal(r.facts.risk_flagged, true);
  assert.ok(r.cannot.some(c => c.includes("qualified professional")));
});

test("plan: refuses a goal too thin to decompose", () => {
  const r = R.planProject("do stuff", "");
  assert.equal(r.ok, false);
  assert.ok(r.cannot[0].includes("fewer than four words"));
});

// ------------------------------------------------------------ dispatcher --
test("dispatcher routes by extension", () => {
  assert.equal(R.readFile("a.csv", "a,b\n1,2\n").kind, "dataset");
  assert.equal(R.readFile("a.py", "x = 1").kind, "code");
  assert.equal(R.readFile("a.vtt", "hello there friends").kind, "transcript");
  assert.equal(R.readFile("a.pdf", "%PDF-").kind, "pdf");
  assert.equal(R.readFile("a.png", "", { width: 1, height: 1 }).kind, "image");
  assert.equal(R.readFile("a.md", "# hi there everyone").kind, "document");
});

test("the module states that no reader understands content", () => {
  const src = readFileSync(join(here, "readers.js"), "utf8");
  assert.ok(src.includes("None of them understand content"));
  assert.ok(src.includes("They parse structure"));
});
