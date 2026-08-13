/* Dump the JS engine's distances for the shared parity graphs, as JSON.
 * Consumed by smi/test_parity.py, which compares against the JAX engine. */
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const LMD = createRequire(import.meta.url)(join(here, "lmd.js"));
const cases = JSON.parse(readFileSync(join(here, "fixtures", "parity_graphs.json"), "utf8"));

process.stdout.write(JSON.stringify(cases.map(c => {
  const r = LMD.meshMetric(c.L);
  return {
    name: c.name,
    D: r.D.map(row => row.map(v => (Number.isFinite(v) ? v : null))),
    labels: r.labels, dead: r.dead,
  };
})));
