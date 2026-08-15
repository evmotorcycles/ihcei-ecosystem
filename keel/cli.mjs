/* keel/cli.mjs — the command line for the governance kernel.
 *
 *   keel check "some claim"        what is this made of, and what would settle it
 *   keel run actions.json          put a list of actions through the kernel
 *   keel key [policy.json]         show what is currently allowed
 *   keel version
 *
 * Prints for people, not for machines. --json on any command gives the record.
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { boot, assay, VERSION } from "./kernel.mjs";

const here = dirname(fileURLToPath(import.meta.url));

/* The policy is resolved through one function so the bundled build can bake a
 * copy in without the build script having to edit any other line. A person who
 * downloads one file must not also need a config file. */
function loadPolicy(path) {
  if (path) return JSON.parse(readFileSync(path, "utf8"));
  if (typeof BAKED_POLICY !== "undefined") return BAKED_POLICY;   // set by the bundle
  return JSON.parse(readFileSync(join(here, "policy.example.json"), "utf8"));
}

const C = process.stdout.isTTY
  ? { dim: "\x1b[2m", b: "\x1b[1m", ok: "\x1b[32m", held: "\x1b[33m", stop: "\x1b[31m", off: "\x1b[0m" }
  : { dim: "", b: "", ok: "", held: "", stop: "", off: "" };

const PLAIN = { source: "says where it came from", figures: "gives real numbers",
                method: "says how it was measured", time: "says when",
                scope: "says who or where it applies to" };

export function run(argv, out = console.log) {
  const json = argv.includes("--json");
  const args = argv.filter(a => a !== "--json");
  const cmd = args[0];

  if (!cmd || cmd === "help" || cmd === "--help" || cmd === "-h") return usage(out);
  if (cmd === "version" || cmd === "--version" || cmd === "-v") { out(VERSION); return 0; }

  if (cmd === "check") {
    const text = args.slice(1).join(" ");
    if (!text) { out("keel check \"the claim you want to look at\""); return 2; }
    const a = assay(text);
    if (json) { out(JSON.stringify(a, null, 2)); return 0; }
    if (!a) { out("Nothing to look at yet."); return 0; }
    out(`\n${C.b}What this is made of${C.off}`);
    for (const [sig, label] of Object.entries(PLAIN)) {
      const hit = !a.missing.includes(sig);
      out(`  ${hit ? C.ok + "yes" : C.dim + " no"}${C.off}  ${label}`);
    }
    out(`\n  ${C.b}${a.found} of ${a.of}${C.off} checkable parts present`);
    out(`  ${C.dim}That does not make it true. It makes it checkable.${C.off}`);
    if (a.search_line) {
      out(`\n${C.b}Take this and go and check it${C.off}`);
      out(`  ${a.search_line}`);
      if (a.handles && !a.handles.source_named && a.handles.source.length) {
        out(`  ${C.held}The source line ticked on "${a.handles.source[0]}" — nobody is named.${C.off}`);
      }
    }
    if (a.domains.length) {
      out(`\n  ${C.held}Careful — this touches ${a.domains.join(", ").replace(/[a-z]+\//g, "")}.${C.off}`);
      out(`  ${C.dim}Well-written is not the same as safe. Ask someone qualified.${C.off}`);
    }
    if (a.question) out(`\n  ${C.dim}${a.question}${C.off}`);
    out("");
    return 0;
  }

  if (cmd === "run") {
    const file = args[1];
    if (!file) { out("keel run <actions.json>"); return 2; }
    const keel = boot({ policy: loadPolicy(args[2]) });
    const actions = JSON.parse(readFileSync(file, "utf8"));
    const results = (Array.isArray(actions) ? actions : [actions]).map(a => keel.admit(a));
    const m = keel.manifest();
    if (json) { out(JSON.stringify({ results, manifest: m }, null, 2)); return m.interruptions ? 1 : 0; }

    out(`\n${C.b}At the end of the run${C.off}`);
    out(`  ${C.b}${m.summary}${C.off}`);
    out(m.interruptions
      ? `  You were stopped ${C.stop}${m.interruptions}${C.off} ` +
        `time${m.interruptions === 1 ? "" : "s"} — each one reached past your key.`
      : `  You were interrupted ${C.b}no times${C.off}. Everything is on the sealed list.`);
    for (const s of m.stopped) out(`\n  ${C.stop}stopped${C.off}  ${s.verb} ${s.target}\n          ${C.dim}${s.why}${C.off}`);
    for (const s of m.held) {
      out(`\n  ${C.held}held${C.off}     ${s.verb} ${s.target}`);
      out(`          ${C.dim}missing ${s.missing.join(", ")}${C.off}`);
    }
    out(`\n  ${C.dim}${m.actions} actions, seals ${m.sealed.ok ? "intact" : "BROKEN"}${C.off}\n`);
    return m.interruptions ? 1 : 0;
  }

  if (cmd === "key") {
    const policy = loadPolicy(args[1]);
    if (json) { out(JSON.stringify(policy, null, 2)); return 0; }
    out(`\n${C.b}${policy.name || "Your key"}${C.off}`);
    for (const r of policy.rules) {
      const tag = r.allow ? `${C.ok}goes through${C.off}` : `${C.stop}stopped${C.off}`;
      const extra = [r.allow && r.write ? "can change it" : r.allow ? "reading only" : null,
                     r.budget ? `${r.budget} times` : null,
                     r.require ? "only if it carries its evidence" : null].filter(Boolean).join(" · ");
      out(`  ${tag.padEnd(24)} ${r.plain}${extra ? `\n${" ".repeat(15)}${C.dim}${extra}${C.off}` : ""}`);
    }
    out(`  ${C.stop}stopped${C.off}                  everything else — anything not listed above`);
    out(`\n  ${C.dim}You never have to predict the bad action. Only what is listed happens.${C.off}\n`);
    return 0;
  }

  out(`keel: no such command "${cmd}"`);
  usage(out);
  return 2;
}

function usage(out) {
  out(`
${C.b}keel${C.off} — the governance kernel  ${C.dim}(${VERSION})${C.off}

  A traditional system asks whether a program MAY do something.
  This asks whether there are GROUNDS to do it. Both matter.

${C.b}Commands${C.off}
  keel check "a claim"        what it is made of, and what would settle it
  keel run actions.json       put a list of actions through the kernel
  keel key [policy.json]      show what is currently allowed
  keel version

  Add --json to any command for the record instead of the reading.

${C.dim}Everything runs on this machine. No account, no network, no cost.
It governs the actions handed to it — it cannot stop a program that
never comes through it. A gate you can walk around is a gate you
should not rely on alone.${C.off}
`);
  return 0;
}

if (process.argv[1] && /keel|cli/.test(process.argv[1])) {
  process.exitCode = run(process.argv.slice(2));
}
