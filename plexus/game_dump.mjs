import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
const Q = require(join(here, "game.js"));

const even = { fight: 4, greed: 4, flee: 4 };
const evenSmall = { fight: 0.4, greed: 0.4, flee: 0.4 };
process.stdout.write(JSON.stringify({
  idle: Q.state({ fight: 0.05, greed: 0.05, flee: 0.05 }),
  allFight: Q.state({ fight: 12, greed: 0.05, flee: 0.05 }),
  allFlee: Q.state({ fight: 0.05, greed: 0.05, flee: 12 }),
  allGreed: Q.state({ fight: 0.05, greed: 12, flee: 0.05 }),
  even: Q.state(even),
  evenSmall: Q.state(evenSmall),
  overspend: Q.state({ fight: 100, greed: 100, flee: 100 }),
  /* TRUE global scaling: every link, dungeon ties included. This is the one
     that must be exactly invariant. */
  globalScale: [1, 9].map((k) => {
    const st = Q.state({ fight: 3, greed: 2, flee: 4 });
    const idx = {}; Q.CAST.forEach((n, i) => { idx[n] = i; });
    const scaled = st.links.map((l) => [idx[l[0]], idx[l[1]], l[2] * k]);
    const r = globalThis.LMD.meshMetric(
      globalThis.LMD.laplacianFromEdges(Q.CAST.length, scaled));
    return { k,
      toBoss: r.D[idx[Q.PLAYER]][idx[Q.BOSS]],
      toPortal: r.D[idx[Q.PLAYER]][idx[Q.PORTAL]],
      toLoot: r.D[idx[Q.PLAYER]][idx[Q.LOOT]] };
  }),
  /* greed alone should drag the portal along, because loot and portal are tied */
  greedPulls: [0.05, 1, 4, 12].map((g) => {
    const s = Q.state({ fight: 0.05, greed: g, flee: 0.05 });
    return { greed: g, toLoot: s.toLoot, toPortal: s.toPortal, escaped: s.escaped };
  }),
}));
