/* Dump the JS engine's distances for the shared parity graphs, as JSON.
 * Consumed by smi/test_parity.py, which compares against the JAX engine. */
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const LMD = createRequire(import.meta.url)(join(here, "lmd.js"));
const cases = JSON.parse(readFileSync(join(here, "fixtures", "parity_graphs.json"), "utf8"));

/* Two fixed frames, so the two engines' Procrustes alignment can be compared
 * on the same inputs rather than only their distances. */
const P = [[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 2]];
const Q = [[0, 0], [-1, 0], [-1, -1], [0, -1], [-0.5, -2]];

process.stdout.write(JSON.stringify({
  graphs: cases.map(c => {
    const r = LMD.meshMetric(c.L);
    return {
      name: c.name,
      D: r.D.map(row => row.map(v => (Number.isFinite(v) ? v : null))),
      labels: r.labels, dead: r.dead,
      /* the flat picture as well as the metric: a port that agrees about every
         distance and then draws a different picture is still a broken port */
      xy: (() => {
        const keep = r.labels.map((_, k) => k).filter(k => r.labels[k] === r.labels[0]);
        return keep.length >= 2 && !r.dead ? { keep, xy: LMD.layout2d(r.D, keep) } : null;
      })(),
    };
  }),
  aligned: LMD.procrustes2d(Q, P),
  fade_below: LMD.FADE_BELOW,
}));
