/* node --test weir/weir.test.mjs
 *
 * The test that matters is the one asserting a refused request NEVER REACHED
 * UPSTREAM. Everything else in this project returns an opinion about an action.
 * This is the first component that stops one.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";

import { createWeir, decide, globMatch, guard, loadKey, manifest, Tape, tierOf } from "./weir.mjs";
import { createUpstream, received } from "./upstream_fixture.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const KEY = loadKey(join(here, "key.example.json"));

let up, weir, base;
test.before(async () => {
  up = createUpstream();
  await new Promise(r => up.listen(0, "127.0.0.1", r));
  weir = createWeir({ key: KEY, upstream: `http://127.0.0.1:${up.address().port}` });
  await new Promise(r => weir.listen(0, "127.0.0.1", r));
  base = `http://127.0.0.1:${weir.address().port}`;
});
test.after(() => { weir.close(); up.close(); });

const get = (p, opts) => fetch(`${base}/${p}`, opts);

/* ------------------------------------------------- the interposition test */
test("a refused request NEVER REACHES UPSTREAM", async () => {
  received.length = 0;
  for (const p of ["payroll/salaries.csv", ".ssh/id_rsa", "secret/.env", "nothing/here.txt"]) {
    const r = await get(p);
    assert.equal(r.status, 403, `${p} must be refused`);
  }
  assert.deepEqual(received, [],
    "upstream logged a request it should never have seen — this is advice, not a gate");
});

test("the refusal body never contains the protected content", async () => {
  const r = await get(".ssh/id_rsa");
  const body = await r.text();
  assert.ok(!body.includes("PRIVATE KEY MATERIAL"));
  assert.match(body, /refused/);
});

test("allowed requests do reach upstream and come back whole", async () => {
  received.length = 0;
  const r = await get("public/github.json");
  assert.equal(r.status, 200);
  const j = JSON.parse(await r.text());
  assert.equal(j.repos.length, 22, "the real frozen GitHub cohort should pass through intact");
  assert.deepEqual(received.map(x => x.path), ["public/github.json"]);
});

test("the Hugging Face cohort passes through intact", async () => {
  const r = await get("public/hf.json");
  const j = JSON.parse(await r.text());
  const rows = j[Object.keys(j).find(k => k !== "_provenance")];
  assert.ok(rows.length >= 20);
});

/* ------------------------------------------------------------ the rules -- */
test("default deny: anything not on the key is refused", () => {
  const d = decide(KEY, "GET", "somewhere/else.txt");
  assert.equal(d.allow, false);
  assert.match(d.why, /default deny/);
});

test("a refusal beats a permission written above it", () => {
  const key = { rules: [
    { path: "**", plain: "everything", allow: true, write: true },
    { path: "payroll/**", plain: "payroll", allow: false }] };
  assert.equal(decide(key, "GET", "payroll/x.csv").allow, false);
  assert.match(decide(key, "GET", "payroll/x.csv").why, /refusal always beats/);
});

test("read permission does not imply write permission", async () => {
  const d = decide(KEY, "PUT", "projects/report.md");
  assert.equal(d.allow, false);
  assert.match(d.why, /permits reading/);
  received.length = 0;
  const r = await get("projects/report.md", { method: "PUT", body: "overwrite" });
  assert.equal(r.status, 403);
  assert.deepEqual(received, [], "a write refusal must not reach upstream either");
});

test("a budget runs out and the key stops working", async () => {
  const fresh = createWeir({ key: KEY, upstream: `http://127.0.0.1:${up.address().port}` });
  await new Promise(r => fresh.listen(0, "127.0.0.1", r));
  const b = `http://127.0.0.1:${fresh.address().port}`;
  const codes = [];
  for (let i = 0; i < 7; i++) {
    const r = await fetch(`${b}/projects/drafts/new.md`, { method: "POST", body: "x" });
    codes.push(r.status);
  }
  assert.deepEqual(codes, [200, 200, 200, 200, 200, 403, 403],
    "the key permitted five changes; the sixth must be refused");
  fresh.close();
});

test("glob matching does not leak across directory boundaries", () => {
  assert.ok(globMatch("projects/**", "projects/a/b.md"));
  assert.ok(!globMatch("projects/*", "projects/a/b.md"));
  assert.ok(globMatch("**/.env", "secret/.env"));
});

/* ------------------------------------------------------------- the tape -- */
test("every crossing is sealed, refusals included", async () => {
  const t = new Tape();
  const w = createWeir({ key: KEY, upstream: `http://127.0.0.1:${up.address().port}`, tape: t });
  await new Promise(r => w.listen(0, "127.0.0.1", r));
  const b = `http://127.0.0.1:${w.address().port}`;
  await fetch(`${b}/projects/report.md`);
  await fetch(`${b}/payroll/salaries.csv`);
  assert.equal(t.entries.length, 2);
  assert.equal(t.entries[0].what, "PASSED");
  assert.equal(t.entries[1].what, "REFUSED");
  assert.equal(t.verify().ok, true);
  t.entries[0].path = "something/else";
  assert.equal(t.verify().ok, false, "editing a past crossing must break the chain");
  w.close();
});

/* --------------------------------------------------------- the screening - */
test("content crossing the gate is screened, and warnings ride on the response", async () => {
  const r = await get("projects/health.md");
  assert.equal(r.status, 200);
  assert.equal(r.headers.get("x-weir"), "passed");
  assert.match(r.headers.get("x-weir-careful") || "", /medical\/health/,
    "an outbreak report must carry a warning through the gate");
});

test("thin content is marked thin rather than passed off as checked", async () => {
  const r = await get("projects/thin.md");
  assert.equal(r.headers.get("x-weir-check"), "INSUFFICIENT_EVIDENCE");
});

/* -------------------------------------------------------------- the guard */
/* Everywhere else Cairn returns a verdict and something downstream may or may
 * not act on it. Here the verdict IS the refusal. */
test("content that does not reach the required bar is withheld, not delivered", async () => {
  const r = await get("briefings/bare.md");
  assert.equal(r.status, 403);
  assert.equal(r.headers.get("x-weir"), "withheld");
  assert.equal(r.headers.get("x-weir-guard"), "NOT_MET");
  const j = JSON.parse(await r.text());
  assert.equal(j.required, "SUPPORTED");
  assert.equal(j.got, "INSUFFICIENT_EVIDENCE");
  assert.ok(!j.body && !JSON.stringify(j).includes("everyone should switch"),
    "the content that failed the bar must not ride out inside the refusal");
  assert.ok(j.next_step, "a withheld response must say what would fix it");
});

test("withholding is honest that upstream DID see the request", async () => {
  received.length = 0;
  const r = await get("briefings/bare.md");
  assert.equal(r.status, 403);
  assert.deepEqual(received.map(x => x.path), ["briefings/bare.md"],
    "content guarding happens after the fetch — that is a weaker claim than refusal");
  const j = JSON.parse(await r.text());
  assert.equal(j.fetched_but_not_delivered, true,
    "the response must not let a reader confuse this with a request that never left");
});

test("content that does reach the bar is delivered whole", async () => {
  const r = await get("briefings/sourced.md");
  assert.equal(r.status, 200);
  assert.equal(r.headers.get("x-weir-guard"), "MET");
  assert.match(await r.text(), /readmission fell 8%/);
});

test("could-not-check is a third state and fails closed by default", async () => {
  const r = await get("briefings/binary.bin");
  assert.equal(r.status, 403);
  assert.equal(r.headers.get("x-weir-guard"), "UNCHECKABLE",
    "an unreadable payload must not be reported as a failed check");
  assert.match(JSON.parse(await r.text()).why, /could not check.*not.*checked and failed/);
});

test("a key may allow uncheckable through, and the stamp still says so", () => {
  assert.equal(guard("SUPPORTED", "withhold", null).withhold, true);
  const passed = guard("SUPPORTED", "pass", null);
  assert.equal(passed.withhold, false);
  assert.equal(passed.state, "UNCHECKABLE", "passing it must not relabel it as MET");
});

test("a withheld parcel comes back with a slip saying what to check", async () => {
  const r = await get("briefings/bare.md");
  const j = JSON.parse(await r.text());
  assert.ok("handles" in j && "search_line" in j,
    "handing back nothing to check is the empty tray this design rejects");
});

/* The case that motivated the handles. A fabrication written in the shape of a
 * finding is HIGHLY checkable, so it passes the guard — and that is correct.
 * What the gate can do is hand over the exact spans that kill it. */
test("a well-dressed fabrication passes the guard, carrying the handles that kill it", async () => {
  const r = await get("briefings/greentea.md");
  assert.equal(r.status, 200, "5/5 checkable text is delivered — checkable is not true");
  assert.equal(r.headers.get("x-weir-guard"), "MET");
  assert.equal(r.headers.get("x-weir-evidence"), "5/5");
  assert.match(r.headers.get("x-weir-careful") || "", /medical\/health/,
    "a health claim must still carry its warning through");
});

test("a rule with no bar set guards nothing", () => {
  assert.deepEqual(guard(null, "withhold", null), { withhold: false, state: "NOT_REQUIRED" });
});

/* -------------------------------------------------- interrupting a person */
/* A slip per crossing is not protection. Someone who has dismissed forty slips
 * dismisses the forty-first without reading it. */
test("passing traffic never interrupts, and is still all on the tape", async () => {
  const t = new Tape();
  const w = createWeir({ key: KEY, upstream: `http://127.0.0.1:${up.address().port}`, tape: t });
  await new Promise(r => w.listen(0, "127.0.0.1", r));
  const b = `http://127.0.0.1:${w.address().port}`;
  for (let i = 0; i < 20; i++) await fetch(`${b}/projects/report.md`);
  const m = w.manifest();
  assert.equal(m.done, 20);
  assert.equal(m.interruptions, 0, "twenty ordinary reads must interrupt nobody");
  assert.equal(m.crossings, 20, "and every one of them is still sealed to the tape");
  assert.equal(m.sealed.ok, true);
  w.close();
});

test("thin content is held quietly and reported once at the end", async () => {
  const t = new Tape();
  const w = createWeir({ key: KEY, upstream: `http://127.0.0.1:${up.address().port}`, tape: t });
  await new Promise(r => w.listen(0, "127.0.0.1", r));
  const b = `http://127.0.0.1:${w.address().port}`;
  for (let i = 0; i < 7; i++) await fetch(`${b}/projects/report.md`);
  const r = await fetch(`${b}/briefings/bare.md`);
  assert.equal(r.headers.get("x-weir-tier"), "BATCH",
    "a thin briefing is 'your input was weak' — that can wait for the end of the run");
  const m = w.manifest();
  assert.equal(m.interruptions, 0);
  assert.match(m.summary, /^7 done · 1 held for missing /);
  assert.equal(m.held.length, 1);
  assert.ok(m.held[0].missing.length, "a batch count must name what each one was missing");
  w.close();
});

test("a boundary breach interrupts immediately, on its own", async () => {
  const t = new Tape();
  const w = createWeir({ key: KEY, upstream: `http://127.0.0.1:${up.address().port}`, tape: t });
  await new Promise(r => w.listen(0, "127.0.0.1", r));
  const b = `http://127.0.0.1:${w.address().port}`;
  for (let i = 0; i < 5; i++) await fetch(`${b}/projects/report.md`);
  const r = await fetch(`${b}/.ssh/id_rsa`);
  assert.equal(r.headers.get("x-weir-tier"), "STOP");
  const m = w.manifest();
  assert.equal(m.interruptions, 1, "reaching for the login keys is not something to mention later");
  assert.equal(m.stopped[0].path, ".ssh/id_rsa");
  w.close();
});

test("high-stakes content is promoted out of the batch", () => {
  assert.equal(tierOf({ what: "WITHHELD", domains: [] }), "BATCH");
  assert.equal(tierOf({ what: "WITHHELD", domains: ["medical/health"] }), "STOP",
    "a health claim held back is not something to mention at the end of the run");
  assert.equal(tierOf({ what: "REFUSED", domains: [] }), "STOP");
  assert.equal(tierOf({ what: "PASSED", domains: ["medical/health"] }), "LEDGER",
    "content that PASSED is not an interruption — the warning rides on the response");
});

test("the manifest names what was held, never only how many", () => {
  const t = new Tape();
  t.add({ what: "PASSED", path: "a", tier: "LEDGER" });
  t.add({ what: "WITHHELD", path: "b", tier: "BATCH", missing: ["source", "time"], why: "thin" });
  const m = manifest(t);
  assert.equal(m.done, 1);
  assert.deepEqual(m.held[0].missing, ["a source", "a date"],
    "signal names must be turned into words a person uses");
  assert.match(m.summary, /1 done · 1 held for missing/);
});

/* ------------------------------------------------------------ the limits - */
test("the file states plainly that it is not unbypassable", () => {
  // the disclaimer wraps across comment lines, so compare the flattened text
  const src = readFileSync(join(here, "weir.mjs"), "utf8").replace(/\s*\n\s*\*?\s*/g, " ");
  assert.match(src, /not mandatory in the operating-system sense/);
  assert.match(src, /opening its own socket/);
  assert.match(src, /guarantee the code does not provide/);
});

test("screening raw JSON produces noisy flags, and that is not hidden", async () => {
  // github.json contains the word "license", which trips the legal pattern.
  // A machine-readable payload is not prose and the screen was built for prose.
  const r = await get("public/github.json");
  const careful = r.headers.get("x-weir-careful");
  assert.ok(careful, "the flag does fire here");
  const readme = readFileSync(join(here, "README.md"), "utf8");
  assert.match(readme, /noisy on machine-readable payloads/,
    "the README must disclose that screening JSON produces false flags");
});
