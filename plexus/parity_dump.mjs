/* Dump the browser engines' answers for the shared parity set, as JSON.
 * Consumed by plexus/test_plexus.py, which compares against spar/ and fathom/. */
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
const P = require(join(here, "engines.js"));

const STRUCTURES = [
  ["triangle", ["a", "b", "c"], [["a", "b", 1], ["b", "c", 1], ["a", "c", 1]]],
  ["path", ["a", "b", "c", "d"], [["a", "b", 1], ["b", "c", 1], ["c", "d", 1]]],
  ["kite", ["a", "b", "c", "d"],
   [["a", "b", 1], ["b", "c", 1], ["a", "c", 1], ["c", "d", 1]]],
  ["weighted", ["w", "x", "y", "z"],
   [["w", "x", 3.7], ["x", "y", 0.4], ["y", "z", 9.1], ["w", "z", 2.2]]],
  ["wide weights", ["p", "q", "r", "s"],
   [["p", "q", 1e-3], ["q", "r", 1e3], ["p", "r", 1], ["r", "s", 5]]],
  ["two pieces", ["a", "b", "c", "d", "e"],
   [["a", "b", 1], ["b", "c", 2], ["d", "e", 5]]],
  ["hub", ["hub", "a", "b", "c"],
   [["hub", "a", 1], ["hub", "b", 1], ["hub", "c", 1]]],
  ["the energy bill", ["Meter reading", "Unit rate", "Standing charge", "Subtotal",
                       "VAT", "Late fee", "Amount due"],
   [["Meter reading", "Subtotal", 8], ["Unit rate", "Subtotal", 8],
    ["Standing charge", "Subtotal", 3], ["Subtotal", "VAT", 6],
    ["Subtotal", "Amount due", 6], ["VAT", "Amount due", 6],
    ["Late fee", "Amount due", 0.4]]],
];

const CLAIMS = [
  ["shared origin", "The claim", ["Origin"],
   [["The claim", "A", 1], ["The claim", "B", 1],
    ["A", "Origin", 1], ["B", "Origin", 1]]],
  ["separate sources", "The claim", ["S1", "S2"],
   [["The claim", "A", 1], ["The claim", "B", 1],
    ["A", "S1", 1], ["B", "S2", 1]]],
  ["lopsided", "The claim", ["Study", "Blog"],
   [["The claim", "Study", 9], ["The claim", "Blog", 0.2]]],
  ["long names that share a prefix", "The result",
   ["Source alpha", "Source alpha two"],
   [["The result", "Source alpha", 2], ["The result", "Source alpha two", 2]]],
];

process.stdout.write(JSON.stringify({
  bearings: STRUCTURES.map(([name, parts, links]) => {
    const b = P.bearings(parts, links);
    return { name, total: b.total, pieces: b.pieces, expected: b.expected,
             links: b.links.map(r => ({ from: r.from, to: r.to, bearing: r.bearing })) };
  }),
  singlePoints: STRUCTURES.map(([name, parts, links]) => ({
    name, parts: P.singlePoints(parts, links),
  })),
  soundings: CLAIMS.map(([name, conclusion, sources, links]) => {
    const parts = [];
    links.forEach(l => { [l[0], l[1]].forEach(n => { if (parts.indexOf(n) < 0) parts.push(n); }); });
    sources.forEach(s => { if (parts.indexOf(s) < 0) parts.push(s); });
    const s = P.sound(parts, links, sources, conclusion);
    return { name, deepest: s.deepest, restsOnOneThread: s.restsOnOneThread,
             bySource: s.bySource };
  }),
}));
