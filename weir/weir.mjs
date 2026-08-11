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
           budget: hit.budget ?? null };
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

/* ----------------------------------------------------------- the gate ---- */
export function createWeir({ key, upstream, tape = new Tape(), screen = true }) {
  const spent = new Map();          // rule -> writes used, for budgeted rules
  const stats = { seen: 0, passed: 0, refused: 0, screened: 0, flagged: 0 };

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
                               rule: verdict.rule, why: verdict.why });
      res.writeHead(403, { "content-type": "application/json",
                           "x-weir": "refused", "x-weir-seal": entry.seal.slice(0, 16) });
      // The request is answered here. It is NEVER forwarded: upstream does not
      // see it, because the bytes are never sent.
      res.end(JSON.stringify({ refused: true, path, rule: verdict.rule,
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

    stats.passed++;
    let checked = null;
    if (screen && /text|json|html/.test(body.type || "")) {
      const a = EI.assay(body.text.slice(0, 4000), "slate");
      stats.screened++;
      const risky = a.domain_flags.length > 0;
      const thin = a.verdict === "INSUFFICIENT_EVIDENCE";
      if (risky || thin) stats.flagged++;
      checked = { verdict: a.verdict, evidence: `${a.evidence_hits}/${a.evidence_total}`,
                  domains: a.domain_flags, thin, risky };
    }

    const entry = tape.add({ what: "PASSED", method: req.method, path,
                             rule: verdict.rule, bytes: body.text.length, checked });
    res.writeHead(body.status || 200, {
      "content-type": body.type || "text/plain",
      "x-weir": "passed",
      "x-weir-rule": verdict.rule,
      "x-weir-seal": entry.seal.slice(0, 16),
      ...(checked ? { "x-weir-check": checked.verdict,
                      "x-weir-evidence": checked.evidence,
                      ...(checked.domains.length
                          ? { "x-weir-careful": checked.domains.join(",") } : {}) } : {}),
    });
    res.end(body.text);
  });

  server.stats = stats;
  server.tape = tape;
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
