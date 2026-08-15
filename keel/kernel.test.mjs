/* node --test keel/kernel.test.mjs
 *
 * The claims this file has to defend:
 *   1. there is ONE way in, and it cannot be gone around inside the kernel
 *   2. every stage can only REFUSE — none of them can grant
 *   3. permission and grounds are different things, and both are checked
 *   4. "could not check" never becomes "checked and passed"
 *   5. ordinary work interrupts nobody, and a breach interrupts immediately
 *   6. the file states plainly what it is not
 */
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { boot, consultKey, globMatch, Ledger, meetsBar, assay, tierOf } from "./kernel.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const POLICY = JSON.parse(readFileSync(join(here, "policy.example.json"), "utf8"));

const GROUNDED = "According to the 2024 ONS survey of 1,180 households across the UK, " +
                 "energy use fell 8% compared with the year before.";
const HOLLOW = "The new process is much better and everyone should switch to it.";

const k = () => boot({ policy: POLICY });

/* ------------------------------------------------------ one way in ------- */
test("the kernel refuses to start without a policy — there is no implicit default", () => {
  assert.throws(() => boot({}), /no implicit default/);
  assert.throws(() => boot({ policy: {} }), /rules array/);
});

test("an action that does not say what it is gets no further than the first stage", () => {
  const d = k().admit({ content: "please just do it" });
  assert.equal(d.admitted, false);
  assert.equal(d.stage, "NAME");
  assert.match(d.why, /say what it is/);
});

test("every outcome is sealed, admitted ones included", () => {
  const keel = k();
  keel.admit({ verb: "read", target: "projects/a.md" });
  keel.admit({ verb: "read", target: "payroll/x.csv" });
  keel.admit({ verb: "write", target: "projects/a.md" });
  assert.equal(keel.ledger.entries.length, 3, "a decision nobody recorded is not a decision");
  assert.equal(keel.ledger.verify().ok, true);
});

/* --------------------------------------- permission is not grounds ------- */
test("permission and grounds are checked separately, and both can stop it", () => {
  const keel = k();
  // permission fails, grounds never consulted
  const a = keel.admit({ verb: "read", target: "payroll/salaries.csv", content: GROUNDED });
  assert.equal(a.stage, "KEY");
  assert.equal(a.outcome, "REFUSED");

  // permission passes, grounds fail
  const b = keel.admit({ verb: "write", target: "posts/claim.md", content: HOLLOW });
  assert.equal(b.stage, "BAR");
  assert.equal(b.outcome, "HELD");

  // both pass
  const c = keel.admit({ verb: "write", target: "posts/claim.md", content: GROUNDED });
  assert.equal(c.admitted, true);
});

test("a hallucination with valid permission is exactly what this catches", () => {
  const keel = k();
  const d = keel.admit({ verb: "write", target: "posts/finding.md", content: HOLLOW });
  assert.equal(d.admitted, false,
    "every traditional operating system would have written this file");
  assert.match(d.why, /INSUFFICIENT_EVIDENCE/);
  assert.ok(d.next, "a refusal that does not say what would fix it is a dead end");
});

test("reading is not writing, and the key says so in words", () => {
  const d = k().admit({ verb: "write", target: "projects/notes.md" });
  assert.equal(d.admitted, false);
  assert.match(d.why, /permits reading .*, not changing it/);
});

test("default deny: anything unlisted does not happen", () => {
  const d = k().admit({ verb: "read", target: "somewhere/else.txt" });
  assert.match(d.why, /default deny/);
  assert.equal(d.rule, "(nothing on the key)");
});

test("a refusal beats a permission written above it", () => {
  const policy = { rules: [
    { path: "**", plain: "everything", allow: true, write: true },
    { path: "payroll/**", plain: "payroll", allow: false }] };
  const r = consultKey(policy, "read", "payroll/x.csv");
  assert.equal(r.ok, false);
  assert.match(r.why, /refusal always beats/);
});

test("a budget runs out and the permission stops working", () => {
  const keel = k();
  const codes = [];
  for (let i = 0; i < 7; i++) {
    codes.push(keel.admit({ verb: "write", target: "projects/drafts/n.md" }).admitted);
  }
  assert.deepEqual(codes, [true, true, true, true, true, false, false]);
});

test("a read never spends the write budget", () => {
  const keel = k();
  for (let i = 0; i < 20; i++) keel.admit({ verb: "read", target: "projects/drafts/n.md" });
  assert.equal(keel.admit({ verb: "write", target: "projects/drafts/n.md" }).admitted, true);
});

/* ------------------------------------------- three states, never two ----- */
test("could not check never becomes checked and passed", () => {
  assert.equal(assay(""), null, "empty content is unmeasurable, not weak");
  const closed = meetsBar("SUPPORTED", "withhold", null);
  assert.equal(closed.ok, false);
  assert.equal(closed.state, "UNCHECKABLE");
  const open = meetsBar("SUPPORTED", "pass", null);
  assert.equal(open.ok, true);
  assert.equal(open.state, "UNCHECKABLE", "letting it through must not relabel it MET");
});

test("a rule with no bar does not invent one", () => {
  assert.deepEqual(meetsBar(null, "withhold", null), { ok: true, state: "NOT_REQUIRED" });
  assert.equal(k().admit({ verb: "read", target: "projects/a.md" }).admitted, true);
});

test("an unknown bar is a policy error, not a silent pass", () => {
  assert.throws(() => meetsBar("EXCELLENT", "withhold", { verdict: "SUPPORTED" }), /unknown bar/);
});

/* ------------------------------------------------- checkable is not true - */
test("a well-dressed fabrication is admitted, and hands over what kills it", () => {
  const keel = k();
  const fake = "According to a 2023 randomised trial of 240 participants in the UK, " +
               "green tea reduced self-reported stress by 12%.";
  const d = keel.admit({ verb: "write", target: "posts/tea.md", content: fake });
  assert.equal(d.admitted, true,
    "the bar measures whether a claim can be checked, never whether it is true");
  assert.equal(d.search_line, "2023 240 participants 12% randomised trial in the UK",
    "what it hands over is what settles it in five seconds");
});

/* ------------------------------------------------------- interruptions --- */
test("ordinary work interrupts nobody and is still all on the ledger", () => {
  const keel = k();
  for (let i = 0; i < 30; i++) keel.admit({ verb: "read", target: `projects/n${i}.md` });
  const m = keel.manifest();
  assert.equal(m.done, 30);
  assert.equal(m.interruptions, 0);
  assert.equal(m.actions, 30);
  assert.equal(m.sealed.ok, true);
});

test("thin material waits for the end of the run; a breach does not", () => {
  const keel = k();
  for (let i = 0; i < 9; i++) keel.admit({ verb: "read", target: `projects/n${i}.md` });
  keel.admit({ verb: "write", target: "posts/a.md", content: HOLLOW });
  const quiet = keel.manifest();
  assert.equal(quiet.interruptions, 0, "'your input was thin' can always wait");
  assert.match(quiet.summary, /^9 done · 1 held for missing /);
  assert.ok(quiet.held[0].missing.length, "a batch count must name what each was missing");

  keel.admit({ verb: "read", target: ".ssh/id_rsa" });
  assert.equal(keel.manifest().interruptions, 1,
    "reaching for the login keys is not something to mention later");
});

test("high-stakes material is promoted out of the batch", () => {
  assert.equal(tierOf("HELD", []), "BATCH");
  assert.equal(tierOf("HELD", ["medical/health"]), "STOP");
  assert.equal(tierOf("REFUSED", []), "STOP");
  assert.equal(tierOf("ADMITTED", ["medical/health"]), "LEDGER",
    "material that was ADMITTED is not an interruption");
});

test("editing a past decision breaks every seal after it", () => {
  const l = new Ledger();
  l.add({ outcome: "ADMITTED", target: "a" });
  l.add({ outcome: "REFUSED", target: "b" });
  assert.equal(l.verify().ok, true);
  l.entries[0].target = "something else";
  assert.equal(l.verify().ok, false);
});

test("glob matching does not leak across directory boundaries", () => {
  assert.ok(globMatch("projects/**", "projects/a/b.md"));
  assert.ok(!globMatch("projects/*", "projects/a/b.md"));
  assert.ok(globMatch("**/.env", "secret/.env"));
});

/* --------------------------------------------------------- the honesty --- */
test("the kernel states plainly that it is not an operating-system kernel", () => {
  const src = readFileSync(join(here, "kernel.mjs"), "utf8").replace(/\s*\n\s*\*?\s*/g, " ");
  assert.match(src, /not a kernel in the operating-system sense/);
  assert.match(src, /NOTHING FORCES A PROGRAM TO COME THROUGH IT/);
  assert.match(src, /A gate you can walk around is a gate you should not rely on alone/);
});

test("the paradigm shift is stated as a difference in default, not a claim of superiority", () => {
  const src = readFileSync(join(here, "kernel.mjs"), "utf8");
  assert.match(src, /MAY this program do this\?/);
  assert.match(src, /are there GROUNDS to do this\?/);
  assert.match(src, /competes with none of them/);
});
