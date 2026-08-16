/* Dump the Elastic Topology Interface's answers as JSON, for test_eti.py to
 * check against the Python engines. Same pattern as parity_dump.mjs: the view
 * is not trusted because it looks right, it is checked. */
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
const ETI = require(join(here, "eti.js"));

const VIEW = { w: 360, h: 320, pad: 30 };

const CASES = [
  ["triangle", ["a", "b", "c"], [["a", "b", 1], ["b", "c", 1], ["a", "c", 1]]],
  ["path", ["a", "b", "c", "d"], [["a", "b", 1], ["b", "c", 1], ["c", "d", 1]]],
  ["kite", ["a", "b", "c", "d"],
   [["a", "b", 1], ["b", "c", 1], ["a", "c", 1], ["c", "d", 1]]],
  ["two pieces", ["a", "b", "c", "d", "e"],
   [["a", "b", 1], ["b", "c", 2], ["d", "e", 5]]],
  ["hub", ["hub", "a", "b", "c"],
   [["hub", "a", 1], ["hub", "b", 1], ["hub", "c", 1]]],
  ["nothing left", ["a", "b", "c"], []],
];

/* One coupling turned up over three orders of magnitude, everything else held
   still. Rayleigh monotonicity says the distance must fall every time. */
const COLLAPSE = [0.25, 1, 4, 16, 64, 256].map((w) => {
  const links = [["a", "b", w], ["b", "c", 1], ["a", "c", 1], ["c", "d", 1]];
  const f = ETI.frame(["a", "b", "c", "d"], links, VIEW);
  const e = f.edges.find((x) => x.from === "a" && x.to === "b");
  return { w, distance: e.distance, bearing: e.bearing, integrity: f.integrity };
});

const KITE = [["a", "b", 1], ["b", "c", 1], ["a", "c", 1], ["c", "d", 1]];
const f1 = ETI.frame(["a", "b", "c", "d"], KITE, VIEW);
const f2 = ETI.frame(["a", "b", "c", "d"], KITE, VIEW);

process.stdout.write(JSON.stringify({
  cases: CASES.map(([name, parts, links]) => {
    const g = ETI.integrity(parts, links);
    const f = ETI.frame(parts, links, VIEW);
    return {
      name, parts: g.parts, pieces: g.pieces, total: g.total,
      integrity: g.integrity, stranded: f.stranded, nodes: f.nodes.length,
      soles: f.edges.filter((e) => e.sole).length,
      box: f.nodes.reduce((a, n) => ({
        x0: Math.min(a.x0, n.x), x1: Math.max(a.x1, n.x),
        y0: Math.min(a.y0, n.y), y1: Math.max(a.y1, n.y),
      }), { x0: Infinity, x1: -Infinity, y0: Infinity, y1: -Infinity }),
    };
  }),
  collapse: COLLAPSE,
  whole: ETI.integrity(["a", "b", "c", "d"],
    [["a", "b", 1], ["b", "c", 1], ["c", "d", 1]]),
  fractured: ETI.integrity(["a", "b", "c", "d"],
    [["a", "b", 1], ["c", "d", 1]]),
  deterministic: JSON.stringify(f1.nodes) === JSON.stringify(f2.nodes),
  view: VIEW,
}));
