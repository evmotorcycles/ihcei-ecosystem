/* keel/kernel.mjs — the governance kernel.
 * ===========================================================================
 * KEEL is the part of a boat you never see. It does not power the boat, steer
 * it, or choose where it goes. It removes ONE degree of freedom: the sideways
 * one. Without a keel you go where the wind pushes you. With one you go where
 * you are pointed. "On an even keel" is already ordinary speech for this.
 *
 * That is the whole relationship to Windows, macOS, Android, HarmonyOS and
 * Linux. They are the hull, the engine and the cargo hold, and they are good at
 * it. Keel is added underneath. It competes with none of them because it
 * answers a different question:
 *
 *     A traditional kernel asks:  MAY this program do this?
 *     Keel asks:                  are there GROUNDS to do this?
 *
 * Those are orthogonal, which is why holding both matters. A hallucinated
 * instruction with valid permissions executes perfectly on every operating
 * system in the world. The permission was never the thing that was wrong.
 *
 * The inversion, stated once:
 *
 *     Traditional default:  DO IT unless something objects.
 *     Keel default:         DO NOT unless there are grounds.
 *
 * ---------------------------------------------------------------------------
 * THE ONE ENTRY POINT
 * Every action goes through admit(). There is no second path, no fast path and
 * no privileged caller. Six stages run in a fixed order and EVERY STAGE CAN
 * ONLY REFUSE — not one of them can grant. Passing simply means nothing
 * stopped you.
 *
 *   1 NAME    an action must say what it is        (nothing anonymous moves)
 *   2 KEY     default deny                          (you list what IS allowed)
 *   3 BUDGET  a permission may be finite            (five changes, then ask)
 *   4 ASSAY   measure the evidence behind it        (three states, never two)
 *   5 BAR     policy may demand a standard          (below it, withhold)
 *   6 SEAL    write it to a chain that cannot be quietly edited
 *
 * ---------------------------------------------------------------------------
 * WHAT THIS IS NOT
 * This is not a kernel in the operating-system sense and calling it one without
 * this paragraph would be a lie. It does not schedule, allocate memory, drive
 * hardware or isolate processes, and NOTHING FORCES A PROGRAM TO COME THROUGH
 * IT. It governs the actions handed to it. Making it unavoidable is a job for
 * the layer underneath — a container, a network namespace with no other exit, a
 * platform that will only call out through this — and that is not in this
 * repository. A gate you can walk around is a gate you should not rely on
 * alone. Every screen this project ships says so, and a test fails if the
 * sentence is removed.
 */
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(here);
const require = createRequire(import.meta.url);
const EI = require(join(ROOT, "cairn/ei_engine.js"));

export const VERSION = "keel/1.0";

/* Verdicts the bar understands, weakest first. */
const LADDER = ["INSUFFICIENT_EVIDENCE", "AMBIGUOUS", "IMPLAUSIBLE", "OUT_OF_SCOPE", "SUPPORTED"];

/* Domains where being well-formed is not the same as being safe. A held action
 * touching any of these is promoted out of the end-of-run batch. */
export const HIGH_STAKES = ["medical/health", "safety-critical", "financial", "legal/regulatory"];

const READ_VERBS = ["read", "open", "list", "get", "head"];
const SIGNAL_PLAIN = { source: "a source", figures: "a figure", method: "how it was measured",
                       time: "a date", scope: "who it applies to" };

/* ------------------------------------------------------------- stage 2 --- */
export function globMatch(glob, path) {
  const rx = "^" + glob.split("**").map(part =>
    part.split("*").map(p => p.replace(/[.+?^${}()|[\]\\]/g, "\\$&")).join("[^/]*")
  ).join(".*") + "$";
  return new RegExp(rx).test(path);
}

/* Default deny; a refusal beats a permission written above it; the most
 * specific permission wins; reading never implies writing. */
export function consultKey(policy, verb, target) {
  const writing = !READ_VERBS.includes(String(verb).toLowerCase());
  const matches = (policy.rules || []).filter(r => globMatch(r.path, target));
  const denied = matches.find(r => !r.allow);
  if (denied) {
    return { ok: false, rule: denied.path, plain: denied.plain,
             why: "a refusal always beats a permission" };
  }
  const hit = matches.sort((a, b) => b.path.length - a.path.length)[0];
  if (!hit) {
    return { ok: false, rule: "(nothing on the key)", plain: "not on the key",
             why: "default deny — only what is listed can happen" };
  }
  if (writing && !hit.write) {
    return { ok: false, rule: hit.path, plain: hit.plain,
             why: `the key permits reading ${hit.path}, not changing it` };
  }
  return { ok: true, rule: hit.path, plain: hit.plain, writing,
           budget: hit.budget ?? null, bar: hit.require ?? null,
           on_uncheckable: hit.on_uncheckable ?? "withhold" };
}

/* ------------------------------------------------------------- stage 4 --- */
/* Three states, never two. Collapsing "could not check" into "checked and
 * failed" turns an unreadable payload into a silent pass, and collapsing it the
 * other way turns an honest gap into a fabricated verdict. */
export function assay(content) {
  if (content == null || String(content).trim() === "") return null;   // UNCHECKABLE
  const a = EI.assay(String(content).slice(0, 4000), "slate");
  return {
    verdict: a.verdict,
    found: a.evidence_hits, of: a.evidence_total,
    missing: a.evidence.filter(c => !c.hit).map(c => c.signal),
    domains: a.domain_flags,
    handles: a.handles,
    search_line: a.search_line,
    question: a.question,
  };
}

/* ------------------------------------------------------------- stage 5 --- */
export function meetsBar(bar, onUncheckable, checked) {
  if (!bar) return { ok: true, state: "NOT_REQUIRED" };
  if (!checked) {
    const pass = onUncheckable === "pass";
    return { ok: pass, state: "UNCHECKABLE",
             why: pass ? "nothing could be measured; this policy proceeds anyway"
                       : "nothing could be measured, and the default is not to — " +
                         "this is 'could not check', not 'checked and failed'" };
  }
  const need = LADDER.indexOf(bar);
  if (need === -1) throw new Error(`policy asked for an unknown bar: ${bar}`);
  if (LADDER.indexOf(checked.verdict) >= need) {
    return { ok: true, state: "MET", got: checked.verdict };
  }
  return { ok: false, state: "NOT_MET", got: checked.verdict,
           why: `this rule acts only on ${bar} material; what arrived was ` +
                `${checked.verdict} (${checked.found} of ${checked.of} kinds of support)` };
}

/* ------------------------------------------------------------- stage 6 --- */
export class Ledger {
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
      const { seal, ...body } = this.entries[i];
      if (this.entries[i].prev !== prev) {
        return { ok: false, broken: i, why: "does not follow the entry before it" };
      }
      if (createHash("sha256").update(JSON.stringify(body)).digest("hex") !== seal) {
        return { ok: false, broken: i, why: "changed after it was written" };
      }
      prev = seal;
    }
    return { ok: true, entries: this.entries.length };
  }
}

/* --------------------------------------------------------- escalation ---- */
/* A slip for every action is not protection. Someone who has dismissed forty
 * slips dismisses the forty-first without reading it — which is exactly how
 * "Allow" became a reflex on every other system. */
export function tierOf(outcome, domains = []) {
  if (outcome === "REFUSED") return "STOP";                 // a boundary was crossed
  if (outcome === "HELD") {
    return domains.some(d => HIGH_STAKES.includes(d)) ? "STOP" : "BATCH";
  }
  return "LEDGER";
}

/* ============================== THE KERNEL ============================== */
export function boot({ policy, ledger = new Ledger() } = {}) {
  if (!policy || !Array.isArray(policy.rules)) {
    throw new Error("keel needs a policy with a rules array — there is no implicit default");
  }
  const spent = new Map();
  const stats = { seen: 0, admitted: 0, refused: 0, held: 0 };

  /* The governance syscall. Returns a decision; never throws for a refusal,
   * because a refusal is a normal result, not an exception. */
  function admit(action = {}) {
    stats.seen++;
    const { verb, target, content = null, why: intent = null } = action;

    const decide = (outcome, stage, why, extra = {}) => {
      const checked = extra.checked ?? null;
      const tier = tierOf(outcome, checked?.domains || []);
      const entry = ledger.add({
        outcome, stage, verb: verb ?? null, target: target ?? null, tier, why,
        rule: extra.rule ?? null, intent,
        found: checked ? `${checked.found}/${checked.of}` : null,
        missing: checked?.missing ?? null,
        domains: checked?.domains ?? [],
      });
      if (outcome === "ADMITTED") stats.admitted++;
      else if (outcome === "HELD") stats.held++;
      else stats.refused++;
      return {
        admitted: outcome === "ADMITTED", outcome, stage, tier, why,
        rule: extra.rule ?? null,
        checked,
        // What to do about it, pointed at the action rather than at the system.
        next: outcome === "ADMITTED" ? null
              : (checked?.question ?? "Name the action and put it on the key."),
        handles: checked?.handles ?? null,
        search_line: checked?.search_line ?? null,
        seal: entry.seal, at: entry.at,
      };
    };

    // 1 NAME — nothing anonymous moves.
    if (!verb || !target) {
      return decide("REFUSED", "NAME",
        "an action has to say what it is and what it touches before anything else can look at it");
    }

    // 2 KEY — default deny.
    const key = consultKey(policy, verb, target);
    if (!key.ok) return decide("REFUSED", "KEY", key.why, { rule: key.rule });

    // 3 BUDGET — a permission may be finite.
    if (key.writing && key.budget != null) {
      const used = spent.get(key.rule) || 0;
      if (used >= key.budget) {
        return decide("REFUSED", "BUDGET",
          `the key allowed ${key.budget} changes here and they are used up`, { rule: key.rule });
      }
      spent.set(key.rule, used + 1);
    }

    // 4 ASSAY + 5 BAR — grounds, not permission.
    const checked = assay(content);
    const bar = meetsBar(key.bar, key.on_uncheckable, checked);
    if (!bar.ok) return decide("HELD", "BAR", bar.why, { rule: key.rule, checked });

    // 6 SEAL happens inside decide() for every outcome, admitted included.
    return decide("ADMITTED", "SEAL",
      key.writing ? "on the key, within budget, and the material meets the bar"
                  : "on the key, and the material meets the bar",
      { rule: key.rule, checked });
  }

  /* One receipt for a whole run, instead of a slip per action. The count never
   * travels alone: what was held is named, with what each one was missing. */
  function manifest() {
    const es = ledger.entries;
    const at = t => es.filter(e => e.tier === t);
    const done = at("LEDGER"), held = at("BATCH"), stopped = at("STOP");
    const slip = e => ({
      verb: e.verb, target: e.target, why: e.why,
      missing: (e.missing || []).map(s => SIGNAL_PLAIN[s] || s),
      seal: e.seal.slice(0, 12),
    });
    const tally = {};
    for (const e of held) for (const m of e.missing || []) tally[m] = (tally[m] || 0) + 1;
    const commonest = Object.entries(tally).sort((a, b) => b[1] - a[1])[0];
    return {
      summary: `${done.length} done` +
        (held.length ? ` · ${held.length} held` +
          (commonest ? ` for missing ${SIGNAL_PLAIN[commonest[0]] || commonest[0]}` : "") : "") +
        (stopped.length ? ` · ${stopped.length} stopped` : ""),
      done: done.length,
      held: held.map(slip),
      stopped: stopped.map(slip),
      interruptions: stopped.length,
      actions: es.length,
      sealed: ledger.verify(),
    };
  }

  return { admit, manifest, ledger, stats, policy, version: VERSION };
}
