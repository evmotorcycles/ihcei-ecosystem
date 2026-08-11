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

import { createWeir, decide, globMatch, loadKey, Tape } from "./weir.mjs";
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
