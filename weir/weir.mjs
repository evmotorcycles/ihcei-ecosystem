/* weir.mjs — the gate an agent has to cross.
 * ===========================================================================
 * A weir is a low barrier built across a stream. Water cannot go round it, and
 * because everything crosses at one place, a weir is also how you MEASURE the
 * flow. That is exactly the job: nothing passes unmeasured, and some things do
 * not pass at all.
 *
 * This is the piece the rest of the project did not have. Cairn, the valet key,
 * the dashcam and the meter all return an OPINION about an action. Weir
 * REFUSES. A denied request is answered 403 and is never forwarded upstream —
 * the upstream server does not see it, because the bytes are never sent.
 *
 *   node weir/weir.mjs --upstream http://127.0.0.1:8081 --port 8080
 *
 * *** WHAT THIS IS AND IS NOT ***
 * It is real interposition FOR TRAFFIC THAT ROUTES THROUGH IT. It is not
 * mandatory in the operating-system sense: nothing stops a program from opening
 * its own socket and ignoring the proxy. Making it unbypassable needs the
 * network namespace, the container, or the OS to force it — and that is not
 * something this file can do for you. Claiming otherwise would hand you a
 * guarantee the code does not provide.
 */
import http from "node:http";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(here);
const require = createRequire(import.meta.url);
const EI = require(join(ROOT, "cairn/ei_engine.js"));

/* ------------------------------------------------------------- the key --- */
export function loadKey(path) {
  const k = JSON.parse(readFileSync(path, "utf8"));
  if (!Array.isArray(k.rules)) throw new Error("a key needs a rules array");
  return k;
}

export function globMatch(glob, path) {
  const rx = "^" + glob.split("**").map(part =>
    part.split("*").map(p => p.replace(/[.+?^${}()|[\]\\]/g, "\\$&")).join("[^/]*")
  ).join(".*") + "$";
  return new RegExp(rx).test(path);
}

/* Verdicts the content guard understands, weakest first. A rule saying
 * `require: "SUPPORTED"` withholds anything that does not reach that bar. */
const LADDER = ["INSUFFICIENT_EVIDENCE", "AMBIGUOUS", "IMPLAUSIBLE", "OUT_OF_SCOPE", "SUPPORTED"];

/* Default deny, refusals beat permissions, most specific permission wins.
 * The same three rules the valet key screen shows a person — enforced here
 * rather than displayed. */
export function decide(key, method, path) {
  const write = !["GET", "HEAD", "OPTIONS"].includes(method.toUpperCase());
  const matches = key.rules.filter(r => globMatch(r.path, path));
  const denies = matches.filter(r => !r.allow);
  if (denies.length) {
    return { allow: false, rule: denies[0].path, plain: denies[0].plain,
             why: "a refusal always beats a permission" };
  }
  const allows = matches.sort((a, b) => b.path.length - a.path.length);
  const hit = allows[0];
  if (!hit) {
    return { allow: false, rule: "(nothing on your key)", plain: "not on the key",
             why: "default deny — you only had to say what WAS allowed" };
  }
  if (write && !hit.write) {
    return { allow: false, rule: hit.path, plain: hit.plain,
             why: `the key permits reading ${hit.path}, not writing to it` };
  }
  return { allow: true, rule: hit.path, plain: hit.plain,
           why: write ? "write permitted by this rule" : "read permitted by this rule",
           budget: hit.budget ?? null,
           require: hit.require ?? null,
           on_uncheckable: hit.on_uncheckable ?? "withhold" };
}

/* Three states, never two. The independence check elsewhere in this project
 * refuses to collapse "checked and failed" into "could not check", and a gate
 * must not either — otherwise an unreadable payload silently becomes a pass.
 *
 *   MET         the content reached the required bar        -> deliver
 *   NOT_MET     it was checked and fell short               -> withhold
 *   UNCHECKABLE nothing could be assayed (binary, empty)    -> the KEY decides
 *
 * The default for UNCHECKABLE is withhold, because this is a gate and a gate
 * fails closed. A key may say `on_uncheckable: "pass"`, and then the response
 * still carries x-weir-guard: UNCHECKABLE — the distinction is never lost, it
 * is only acted on differently. */
export function guard(require, onUncheckable, checked) {
  if (!require) return { withhold: false, state: "NOT_REQUIRED" };
  if (!checked) {
    const pass = onUncheckable === "pass";
    return { withhold: !pass, state: "UNCHECKABLE", got: null,
             why: pass ? "nothing could be assayed; this key says pass anyway"
                       : "nothing could be assayed, and a gate fails closed — " +
                         "this is 'could not check', not 'checked and failed'" };
  }
  const need = LADDER.indexOf(require), got = LADDER.indexOf(checked.verdict);
  if (need === -1) throw new Error(`a key asked for an unknown bar: ${require}`);
  if (got >= need) return { withhold: false, state: "MET", got: checked.verdict };
  return { withhold: true, state: "NOT_MET", got: checked.verdict,
           why: `this rule delivers only ${require} content; what came back was ` +
                `${checked.verdict} (${checked.evidence} kinds of support found)` };
}

/* ------------------------------------------------------------ the tape --- */
export class Tape {
  constructor() { this.entries = []; }
  get head() { return this.entries.length ? this.entries.at(-1).seal : "0".repeat(64); }
  add(body) {
    const e = { ...body, at: new Date().toISOString(), prev: this.head };
    e.seal = createHash("sha256").update(JSON.stringify(e)).digest("hex");
    this.entries.push(e);
    return e;
  }
  verify() {
    let prev = "0".repeat(64);
    for (let i = 0; i < this.entries.length; i++) {
      const e = this.entries[i];
      const { seal, ...body } = e;
      if (e.prev !== prev) return { ok: false, broken: i, why: "does not follow its predecessor" };
      if (createHash("sha256").update(JSON.stringify(body)).digest("hex") !== seal) {
        return { ok: false, broken: i, why: "modified after it was written" };
      }
      prev = seal;
    }
    return { ok: true, entries: this.entries.length };
  }
}

/* --------------------------------------------------------- escalation ---- *
 * An agent doing ordinary work crosses this gate hundreds of times a minute.
 * A slip for every crossing is not protection — it is notification fatigue, and
 * a person who has dismissed forty slips will dismiss the forty-first without
 * reading it. That is how "Allow" became a reflex on every other system.
 *
 * So a crossing lands in one of three tiers, and only one of them interrupts:
 *
 *   LEDGER  it passed. Sealed to the tape, nothing shown. The tape is always
 *           there to inspect; the person's attention is not spent.
 *   BATCH   held for want of evidence. Collected, and reported ONCE at the end
 *           of the run: "47 done · 3 held for missing sources."
 *   STOP    a boundary was crossed, or the content is high-stakes. Shown
 *           immediately, on its own.
 *
 * The dividing line is deliberate: BATCH is "your input was thin", which can
 * always wait. STOP is "something tried to leave the boundary you drew, or what
 * came back could hurt you", which cannot. */
export const TIERS = ["LEDGER", "BATCH", "STOP"];
const HIGH_STAKES = ["medical/health", "safety-critical", "financial", "legal/regulatory"];

export function tierOf({ what, domains = [] }) {
  // A refusal is always a boundary breach: the request was for something that
  // was never on the key. That is the one thing a person must see at once.
  if (what === "REFUSED") return "STOP";
  if (what === "WITHHELD") {
    return domains.some(d => HIGH_STAKES.includes(d)) ? "STOP" : "BATCH";
  }
  return "LEDGER";
}

const SIGNAL_PLAIN = { source: "a source", figures: "a figure", method: "how it was measured",
                       time: "a date", scope: "who it applies to" };

/* The end-of-run receipt. Everything that passed is a number; everything that
 * was held or stopped is named. */
export function manifest(tape) {
  const es = tape.entries;
  const by = t => es.filter(e => (e.tier || tierOf(e)) === t);
  const ledger = by("LEDGER"), batch = by("BATCH"), stops = by("STOP");
  const slip = e => ({
    path: e.path, why: e.why,
    missing: (e.missing || []).map(s => SIGNAL_PLAIN[s] || s),
    search_line: e.search_line || null,
    seal: e.seal.slice(0, 12),
  });
  // The most common missing thing across the batch — what a person would fix once.
  const tally = {};
  for (const e of batch) for (const m of e.missing || []) tally[m] = (tally[m] || 0) + 1;
  const commonest = Object.entries(tally).sort((a, b) => b[1] - a[1])[0];
  return {
    summary: `${ledger.length} done` +
      (batch.length ? ` · ${batch.length} held` +
        (commonest ? ` for missing ${SIGNAL_PLAIN[commonest[0]] || commonest[0]}` : "") : "") +
      (stops.length ? ` · ${stops.length} stopped` : ""),
    done: ledger.length,
    held: batch.map(slip),
    stopped: stops.map(slip),
    interruptions: stops.length,      // how many times the person was actually interrupted
    crossings: es.length,
    sealed: tape.verify(),
  };
}

/* ----------------------------------------------------------- the gate ---- */
export function createWeir({ key, upstream, tape = new Tape(), screen = true }) {
  const spent = new Map();          // rule -> writes used, for budgeted rules
  const stats = { seen: 0, passed: 0, refused: 0, withheld: 0, screened: 0, flagged: 0 };

  const server = http.createServer(async (req, res) => {
    stats.seen++;
    const path = (req.url || "/").replace(/^\/+/, "");
    const verdict = decide(key, req.method || "GET", path);

    // budget: a rule may permit N writes before it must be granted again
    if (verdict.allow && verdict.budget != null &&
        !["GET", "HEAD", "OPTIONS"].includes((req.method || "GET").toUpperCase())) {
      const used = spent.get(verdict.rule) || 0;
      if (used >= verdict.budget) {
        verdict.allow = false;
        verdict.why = `the key allowed ${verdict.budget} changes here and they are used up`;
      } else {
        spent.set(verdict.rule, used + 1);
      }
    }

    if (!verdict.allow) {
      stats.refused++;
      const entry = tape.add({ what: "REFUSED", method: req.method, path,
                               rule: verdict.rule, why: verdict.why, tier: "STOP" });
      res.writeHead(403, { "content-type": "application/json",
                           "x-weir": "refused", "x-weir-tier": "STOP",
                           "x-weir-seal": entry.seal.slice(0, 16) });
      // The request is answered here. It is NEVER forwarded: upstream does not
      // see it, because the bytes are never sent.
      res.end(JSON.stringify({ refused: true, path, rule: verdict.rule, tier: "STOP",
                               why: verdict.why, seal: entry.seal }));
      return;
    }

    let body;
    try {
      body = await fetchUpstream(upstream, req);
    } catch (err) {
      const entry = tape.add({ what: "UPSTREAM_FAILED", method: req.method, path,
                               error: String(err.message || err) });
      res.writeHead(502, { "content-type": "application/json", "x-weir-seal": entry.seal.slice(0, 16) });
      res.end(JSON.stringify({ error: "upstream unreachable", seal: entry.seal }));
      return;
    }

    let checked = null;
    if (screen && /text|json|html/.test(body.type || "")) {
      const a = EI.assay(body.text.slice(0, 4000), "slate");
      stats.screened++;
      const risky = a.domain_flags.length > 0;
      const thin = a.verdict === "INSUFFICIENT_EVIDENCE";
      if (risky || thin) stats.flagged++;
      checked = { verdict: a.verdict, evidence: `${a.evidence_hits}/${a.evidence_total}`,
                  domains: a.domain_flags, thin, risky,
                  question: a.question, next_steps: a.next_steps,
                  // the spans that made each signal fire — what a person carries
                  // to a search engine when the gate hands the parcel back
                  handles: a.handles, search_line: a.search_line,
                  missing: a.evidence.filter(c => !c.hit).map(c => c.signal),
                  words: (body.text.trim() ? body.text.trim().split(/\s+/).length : 0) };
    }

    /* ------- the guard: Cairn stops being a label and becomes a refusal ----
     * Everywhere else in this project Cairn RETURNS A VERDICT and something
     * downstream decides what to do with it — which is to say, nothing has to.
     * Here the verdict is the predicate of a refusal. `require` on a rule
     * means: if the content coming back does not reach this bar, it is not
     * handed over.
     *
     * The guarantee is NARROWER than the one above and must not be blurred
     * with it. A refused REQUEST never reaches upstream. Withheld CONTENT was
     * already fetched — upstream saw the request. What is guaranteed is only
     * that the bytes did not reach the client. */
    const gr = guard(verdict.require, verdict.on_uncheckable, checked);
    if (gr.withhold) {
      stats.withheld++;
      const tier = tierOf({ what: "WITHHELD", domains: checked?.domains || [] });
      const entry = tape.add({ what: "WITHHELD", method: req.method, path,
                               rule: verdict.rule, required: verdict.require,
                               got: gr.got, why: gr.why, tier,
                               domains: checked?.domains || [],
                               missing: checked ? checked.missing : null,
                               search_line: checked?.search_line || null });
      res.writeHead(403, { "content-type": "application/json", "x-weir": "withheld",
                           "x-weir-rule": verdict.rule, "x-weir-guard": gr.state,
                           "x-weir-tier": tier,
                           "x-weir-seal": entry.seal.slice(0, 16) });
      res.end(JSON.stringify({ withheld: true, path, rule: verdict.rule, tier,
                               required: verdict.require, got: gr.got, why: gr.why,
                               fetched_but_not_delivered: true,
                               next_step: checked?.question || null,
                               // A returned parcel with a slip on it: the content
                               // is not handed over, but what to go and check is.
                               handles: checked?.handles || null,
                               search_line: checked?.search_line || null,
                               seal: entry.seal }));
      return;
    }

    stats.passed++;
    const entry = tape.add({ what: "PASSED", method: req.method, path,
                             rule: verdict.rule, bytes: body.text.length, checked,
                             tier: "LEDGER",
                             guard: verdict.require ? gr.state : undefined });
    res.writeHead(body.status || 200, {
      "content-type": body.type || "text/plain",
      "x-weir": "passed",
      "x-weir-tier": "LEDGER",
      "x-weir-rule": verdict.rule,
      "x-weir-seal": entry.seal.slice(0, 16),
      ...(verdict.require ? { "x-weir-guard": gr.state } : {}),
      ...(checked ? { "x-weir-check": checked.verdict,
                      "x-weir-evidence": checked.evidence,
                      ...(checked.domains.length
                          ? { "x-weir-careful": checked.domains.join(",") } : {}) } : {}),
    });
    res.end(body.text);
  });

  server.stats = stats;
  server.tape = tape;
  /* One receipt for a whole run, instead of a slip per crossing. The count
   * never travels alone: `held` names which paths were held and what each was
   * missing, so "3 held" is something a person can act on rather than a number
   * they have to take on trust. (Same obligation as `handles` in Plumb.) */
  server.manifest = () => manifest(tape);
  return server;
}

function fetchUpstream(upstream, req) {
  return new Promise((resolve, reject) => {
    const url = new URL(req.url, upstream);
    const r = http.request(url, { method: req.method, headers: { host: url.host } }, up => {
      let d = "";
      up.on("data", c => { d += c; });
      up.on("end", () => resolve({ text: d, status: up.statusCode,
                                   type: up.headers["content-type"] || "text/plain" }));
    });
    r.on("error", reject);
    req.pipe(r);
    if (!req.readable) r.end();
  });
}

/* ------------------------------------------------------------- the cli --- */
if (process.argv[1] && process.argv[1].endsWith("weir.mjs")) {
  const arg = n => { const i = process.argv.indexOf(n); return i > -1 ? process.argv[i + 1] : null; };
  const keyPath = arg("--key") || join(here, "key.example.json");
  const upstream = arg("--upstream") || "http://127.0.0.1:8081";
  const port = Number(arg("--port") || 8080);
  const key = loadKey(keyPath);
  const server = createWeir({ key, upstream });
  server.listen(port, "127.0.0.1", () => {
    console.log(`weir listening on http://127.0.0.1:${port}`);
    console.log(`  key      ${keyPath}   (${key.rules.length} rules, everything else refused)`);
    console.log(`  upstream ${upstream}`);
    console.log(`  refusals are answered here and never forwarded.`);
    console.log(`  NOT unbypassable: a program that opens its own socket ignores this.`);
  });
  process.on("SIGINT", () => {
    const v = server.tape.verify();
    console.log(`\ntape: ${v.ok ? `${v.entries} entries, all seals intact` : `BROKEN at ${v.broken}`}`);
    console.log(`seen ${server.stats.seen}  passed ${server.stats.passed}  refused ${server.stats.refused}`);
    process.exit(0);
  });
}
