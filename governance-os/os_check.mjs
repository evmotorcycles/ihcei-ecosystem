/* os_check.mjs -- is this an operating system, or a set of libraries?
 * ===========================================================================
 *   node governance-os/os_check.mjs
 *
 * Runs what governance-os/PREREG.md specifies, locked before this ran.
 * Several of these are expected to fail. Failing them is the point: a library
 * called an OS transfers a guarantee to the user that the code does not provide.
 */
import { createRequire } from "node:module";
import { readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(here);
const require = createRequire(import.meta.url);

const EI = require(join(ROOT, "cairn/ei_engine.js"));
require(join(ROOT, "novora-suite/engine.bundle.js"));
const NOVORA = globalThis.NOVORA;
const READERS = require(join(ROOT, "readers/readers.js"));

/* ---------------------------------------------------------------- helpers */
function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (["node_modules", ".git", "__pycache__", ".pytest_cache"].includes(name)) continue;
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) walk(p, out);
    else if (/\.(js|mjs|py|ts|json)$/.test(name) && st.size < 2_000_000) out.push(p);
  }
  return out;
}
const FILES = walk(ROOT);
// Exclusions matter more than the patterns. A first pass "found" interposition
// in THIS FILE (it contains the search patterns as string literals) and in prose
// fixtures that merely mention seccomp. A detector that matches its own source
// is measuring itself.
const SELF = relative(ROOT, fileURLToPath(import.meta.url));
function isEvidence(rel) {
  if (rel === SELF) return false;                       // no self-matching
  if (/(^|\/)fixtures?\//.test(rel)) return false;       // prose fixtures
  if (/\.test\.|_test\.|test_/.test(rel)) return false;  // tests discuss, not implement
  if (/_prose\.json$|README|\.md$/.test(rel)) return false;
  return true;
}
function grepFiles(re) {
  const hits = [];
  for (const f of FILES) {
    const rel = relative(ROOT, f);
    if (!isEvidence(rel)) continue;
    let s;
    try { s = readFileSync(f, "utf8"); } catch { continue; }
    if (re.test(s)) hits.push(rel);
  }
  return hits;
}

/* ------------------------------------------------- O1 interposition ------ */
// Something that can BLOCK looks like: a call that raises/throws/exits on a
// denial, or a hook that wraps a resource access. An opinion looks like: a
// function that returns a decision object nobody is obliged to read.
const blockingCalls = grepFiles(
  /\b(process\.exit|os\.abort|SIGKILL)\b[\s\S]{0,120}\b(deny|denied|blocked|forbidden)\b/i);
const raisesOnDeny = grepFiles(
  /\b(raise|throw)\b[^\n]{0,100}\b(PermissionDenied|NotPermitted|Forbidden|AccessDenied)\b/);
const O1_blocks = [...new Set([...blockingCalls, ...raisesOnDeny])];

// Pattern matching is the weak form of this question and it produced a FALSE
// NEGATIVE: the gate blocks by refusing to forward, which no grep for `throw`
// or `process.exit` can see. So the real check is BEHAVIOURAL — stand the gate
// up, ask it for something denied, and look at whether the far side ever heard
// about it. That cannot be gamed by wording.
async function behaviouralInterpositionCheck() {
  try {
    const W = await import(join(ROOT, "weir/weir.mjs"));
    const F = await import(join(ROOT, "weir/upstream_fixture.mjs"));
    const up = F.createUpstream();
    await new Promise(r => up.listen(0, "127.0.0.1", r));
    const key = W.loadKey(join(ROOT, "weir/key.example.json"));
    const gate = W.createWeir({ key, upstream: `http://127.0.0.1:${up.address().port}` });
    await new Promise(r => gate.listen(0, "127.0.0.1", r));
    const base = `http://127.0.0.1:${gate.address().port}`;
    F.received.length = 0;
    const denied = await fetch(`${base}/payroll/salaries.csv`);
    const deniedReachedUpstream = F.received.length > 0;
    F.received.length = 0;
    const allowed = await fetch(`${base}/projects/report.md`);
    const allowedReachedUpstream = F.received.length > 0;
    gate.close(); up.close();
    return {
      ran: true,
      denied_status: denied.status,
      denied_reached_upstream: deniedReachedUpstream,
      allowed_status: allowed.status,
      allowed_reached_upstream: allowedReachedUpstream,
      blocks: denied.status === 403 && !deniedReachedUpstream && allowedReachedUpstream,
    };
  } catch (e) {
    return { ran: false, error: String(e.message || e) };
  }
}
const behaviour = await behaviouralInterpositionCheck();

/* ------------------------------------------------- O2 mandatory ---------- */
const hookPatterns = [
  [/\bLD_PRELOAD\b/, "linker preload"],
  [/\bptrace\b|\bseccomp\b|\bLandlock\b/, "syscall interception"],
  [/\bFUSE\b|fuse\.Operations|\bfsevents\b/, "filesystem driver"],
  // an extension only interposes with a BLOCKING request API. activeTab and
  // scripting make it an observer you have to click, not a gate.
  [/chrome\.webRequest|chrome\.declarativeNetRequest|"webRequestBlocking"/, "blocking browser extension"],
  [/\bAppArmor\b|\bSELinux\b/, "mandatory access control"],
  [/os\.setuid|capabilities\.set|CAP_SYS/, "privilege boundary"],
];
const O2_hooks = hookPatterns
  .map(([re, label]) => ({ label, files: grepFiles(re) }))
  .filter(x => x.files.length);

// An extension that exists but cannot block is worth reporting precisely,
// because "we ship a browser extension" reads like interposition and is not.
let observerExtension = null;
try {
  const mf = JSON.parse(readFileSync(join(ROOT, "novora-helm/extension/manifest.json"), "utf8"));
  const perms = [...(mf.permissions || []), ...(mf.host_permissions || [])];
  const canBlock = perms.some(p => /webRequest|declarativeNetRequest|<all_urls>|^\*:/.test(p));
  observerExtension = { name: mf.name, permissions: perms, can_block: canBlock,
    reading: canBlock ? "can intercept requests"
      : "READS the active tab when clicked. It cannot intercept or block " +
        "anything, so it observes; it does not interpose." };
} catch { /* no extension present */ }

/* ------------------------------------------------- O3 composition -------- */
// Chain them for real: permission -> record -> claim check.
function globMatch(glob, path) {
  const rx = "^" + glob.split("**").map(part =>
    part.split("*").map(p => p.replace(/[.+?^${}()|[\]\\]/g, "\\$&")).join("[^/]*")
  ).join(".*") + "$";
  return new RegExp(rx).test(path);
}
const RULES = [
  { glob: "projects/**", allow: true }, { glob: "payroll/**", allow: false },
];
function decide(path) {
  const m = RULES.filter(r => globMatch(r.glob, path));
  const deny = m.find(r => !r.allow);
  const hit = deny || m[0] || null;
  return { path, decision: hit ? (hit.allow ? "allow" : "deny") : "deny",
           rule: hit ? hit.glob : "(default)" };
}
function seal(entry, prev) {
  return createHash("sha256").update(JSON.stringify({ ...entry, prev })).digest("hex");
}

const chain = [];
const step1 = decide("projects/report.md");
let prev = "0".repeat(64);
const rec1 = { what: `access ${step1.path}`, decision: step1.decision, prev };
rec1.seal = seal({ what: rec1.what, decision: rec1.decision }, prev);
chain.push(rec1);

const generated = "According to a 2023 trial of 240 participants in the UK, the rate fell 12%.";
const audit = EI.assay(generated, "slate");
const rec2 = { what: "checked generated text", verdict: audit.verdict, prev: rec1.seal };
rec2.seal = seal({ what: rec2.what, verdict: rec2.verdict }, rec1.seal);
chain.push(rec2);

const chained = step1.decision === "allow" && audit.verdict && chain.length === 2 &&
  chain[1].prev === chain[0].seal;

// do the components share a record type?
const shapes = {
  page_code: Object.keys(step1).sort(),
  helm_entry: Object.keys(rec1).sort(),
  cairn_verdict: Object.keys(audit).sort(),
  novora_screen: Object.keys(NOVORA.screen("pages", generated)).sort(),
  reader: Object.keys(READERS.readTextDocument("a.txt", generated)).sort(),
};
const allKeys = Object.values(shapes).map(k => new Set(k));
const shared = [...allKeys[0]].filter(k => allKeys.every(s => s.has(k)));

/* ------------------------------------------------- O4 safe degradation --- */
const EMPTY_INPUTS = ["", "   ", "hi", "ok thanks"];
const degrade = [];
for (const t of EMPTY_INPUTS) {
  const c = EI.assay(t, "slate");
  degrade.push({ component: "cairn", input: t,
    declined: c.verdict === "OUT_OF_SCOPE" || c.confidence === null || c.confidence < 0.25 });
  for (const id of NOVORA.PRODUCT_IDS) {
    const r = NOVORA.screen(id, t);
    degrade.push({ component: `novora/${id}`, input: t,
      declined: r.insufficient_evidence === true && r.display_score === false });
  }
  const rd = READERS.readTextDocument("x.txt", t);
  degrade.push({ component: "reader", input: t, declined: !rd.ok || rd.facts.words < 4 });
  const pl = READERS.planProject(t, "");
  degrade.push({ component: "planner", input: t, declined: !pl.ok });
}
const notDeclined = degrade.filter(d => !d.declined);

/* ------------------------------------------------- verdicts -------------- */
const O1 = { gate: "some component can BLOCK an action, not merely report on one",
  blocking_call_sites: O1_blocks,
  behavioural_check: behaviour,
  method: "behavioural — a denied request is sent and the far side is inspected",
  result: behaviour.blocks ? "PASSES" : "FAILS",
  evidence: behaviour.blocks
    ? `a denied request was answered ${behaviour.denied_status} and the upstream ` +
      "log stayed EMPTY, while an allowed request did reach it. The bytes were " +
      "never sent."
    : "no component stopped a request from reaching its destination" };
const O2 = { gate: "an integration point exists that a program cannot bypass",
  hooks_found: O2_hooks,
  observer_extension_found: observerExtension,
  result: O2_hooks.length ? "PASSES" : "FAILS" };
const O3 = { gate: "components chain without human translation; record types compared",
  chained_end_to_end: chained,
  keys_shared_by_all_five_components: shared,
  shapes,
  result: chained ? (shared.length ? "HOLDS" : "PARTIALLY HOLDS") : "FAILS",
  note: shared.length ? "" :
    "they chain, but share NO common field. Every join is hand-written glue, " +
    "which is what a library looks like, not a kernel." };
const O4 = { gate: "every component declines on evidence-free input",
  checks: degrade.length, failures: notDeclined,
  result: notDeclined.length ? "FAILS" : "HOLDS" };

const isOS = O1.result === "PASSES" && O2.result === "PASSES";
const gateOnly = O1.result === "PASSES" && O2.result === "FAILS";
const O5 = { gate: "the artefact is named for what it is",
  interposition: O1.result, mandatory: O2.result,
  honest_label: isOS ? "operating system"
    : gateOnly ? "a gate that works only where it is the only route"
    : "a library, not an operating system",
  result: "HOLDS",
  why: gateOnly
    ? "It can stop things — that is real and it is new. But nothing forces a " +
      "program to come through it, so the guarantee is conditional on the layer " +
      "underneath (a container, a network with no other exit, a firewall rule). " +
      "Neither 'library' nor 'operating system' is accurate; this is the label " +
      "that is."
    : "" };

const out = {
  prereg_sha256: createHash("sha256")
    .update(readFileSync(join(here, "PREREG.md"))).digest("hex"),
  files_scanned: FILES.length,
  O1_interposition: O1, O2_mandatory: O2, O3_composition: O3,
  O4_safe_degradation: O4, O5_honest_label: O5,
  THE_FINDING: isOS
    ? "interposition and mandatory enforcement both present"
    : gateOnly
    ? "There is now a component that genuinely BLOCKS: a denied request is " +
      "refused at the gate and the far side never receives it, proven by an " +
      "empty upstream log. That is interposition, and the rest of the stack " +
      "still does not have it. What is still missing is MANDATORY routing: " +
      "nothing stops a program from going around the gate. So the honest label " +
      "is neither library nor operating system — it is a gate that works only " +
      "where it is the only route, and putting it there is a job for the " +
      "container or the network, not for this code."
    : "This is NOT an operating system. Nothing here can block an action, and " +
      "there is no hook a program cannot bypass. Every component returns an " +
      "OPINION about an action that something else has already taken or will " +
      "take regardless. What it is: a set of libraries that compose, decline " +
      "safely, and keep a tamper-evident record — which is genuinely useful and " +
      "is not the same guarantee.",
  why_the_distinction_matters:
    "An operating system's value is that a program CANNOT go around it. If a " +
    "permission table only advises, an agent that ignores it is unaffected, and " +
    "the person relying on it is worse off than with no table at all, because " +
    "they believe they are protected.",
  what_would_close_the_gap: [
    "a browser extension that intercepts requests before they are made",
    "an OS-level filesystem hook, or a sandbox the agent runs inside",
    "an MCP or tool-call proxy that the agent must route through",
    "none of these exist in this repository today",
  ],
};

const bar = "=".repeat(78);
console.log(bar);
console.log(" IS THIS AN OPERATING SYSTEM? — pre-registered structural test");
console.log(bar);
console.log(`  files scanned                 ${FILES.length}`);
console.log(`  O1 interposition              ${O1.result}   (can anything BLOCK?)`);
console.log(`  O2 mandatory enforcement      ${O2.result}   (any unbypassable hook?)`);
if (observerExtension) {
  console.log(`     an extension DOES exist: "${observerExtension.name}"`);
  console.log(`     permissions [${observerExtension.permissions.join(", ")}] -> ${observerExtension.reading}`);
}
console.log(`  O3 composition                ${O3.result}`);
console.log(`     chained end to end: ${chained}`);
console.log(`     fields shared by all five components: ${shared.length ? shared.join(", ") : "NONE"}`);
console.log(`  O4 safe degradation           ${O4.result}   (${degrade.length} checks, ${notDeclined.length} failures)`);
console.log(`  O5 honest label               ${O5.honest_label.toUpperCase()}`);
console.log();
console.log("  THE FINDING:");
for (const line of out.THE_FINDING.match(/.{1,72}(\s|$)/g)) console.log("   ", line.trim());
console.log();
console.log("  WHAT WOULD CLOSE THE GAP:");
for (const w of out.what_would_close_the_gap) console.log("    -", w);
writeFileSync(join(here, "results_os.json"), JSON.stringify(out, null, 2));
console.log("\n  wrote results_os.json");
console.log(bar);
