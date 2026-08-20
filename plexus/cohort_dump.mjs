import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
const P = require(join(here, "press.js"));

const frozen = JSON.parse(readFileSync(
  join(here, "..", "ei-dashboards", "data", "qwen_deepseek_frozen.json"), "utf8"));

// Each repository is a mark; the organisation that publishes it is the origin.
const marks = frozen.repos.map(r => ({
  kind: "source", origin: r.org, name: r.full_name, text: r.full_name,
}));

const r = P.press(marks);
const byOrg = {};
frozen.repos.forEach(x => { byOrg[x.org] = (byOrg[x.org] || 0) + 1; });

const settles = {};
r.checks.forEach(c => {
  settles[c.origin] = settles[c.origin] || [];
  settles[c.origin].push(c.settles);
});

process.stdout.write(JSON.stringify({
  provenance: frozen._provenance,
  repos: frozen.repos.length,
  orgs: byOrg,
  origins: r.origins,
  singlePoints: r.singlePoints,
  cutOrigins: r.cutOrigins,
  sharedOrigin: r.sharedOrigin,
  says: r.says,
  settlesByOrg: Object.fromEntries(Object.entries(settles).map(
    ([k, v]) => [k, { n: v.length, each: v[0], allSame: v.every(x => Math.abs(x - v[0]) < 1e-12) }])),
  naive: 1 / frozen.repos.length,
  structure: r.structure,
}, null, 1));
