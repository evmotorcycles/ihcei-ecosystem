import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
const P = require(join(here, "press.js"));

const f = JSON.parse(readFileSync(
  join(here, "..", "hf-cohort", "data", "hf_cohort_frozen.json"), "utf8"));
const M = f.models, n = M.length;

const evalNoPaper = M.filter(m => m.eval_results && !m.arxiv);
const withArxiv = M.filter(m => m.arxiv);
const noBase = M.filter(m => !m.base_model);
const flagged = M.filter(m => (m.flags || []).length);

// Each model is a mark on the origin it declares. A model declaring no base
// model hangs off the same unnamed node -- which is the point: nothing named
// means nothing to open.
const marks = M.map(m => ({
  kind: "source", name: m.id, text: m.id,
  origin: m.base_model || null,
}));
const r = P.press(marks);

const byOrigin = {};
r.checks.forEach(c => {
  byOrigin[c.origin] = byOrigin[c.origin] || { n: 0, settles: c.settles };
  byOrigin[c.origin].n += 1;
});

process.stdout.write(JSON.stringify({
  provenance: f._provenance,
  n,
  evalNoPaper: { n: evalNoPaper.length, share: evalNoPaper.length / n },
  withArxiv: { n: withArxiv.length, share: withArxiv.length / n },
  noBase: { n: noBase.length, share: noBase.length / n },
  flagged: { n: flagged.length, ids: flagged.map(m => m.id) },
  origins: r.origins.length,
  originList: r.origins,
  byOrigin,
  cutOrigins: r.cutOrigins,
  naive: 1 / n,
  maxSettles: Math.max(...r.checks.map(c => c.settles)),
  structure: r.structure,
  licences: [...new Set(M.map(m => m.license))].length,
}, null, 1));
