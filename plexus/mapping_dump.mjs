import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
const ENG = globalThis.PLEXUS;

const SIGNALS = ["source", "figures", "method", "time", "scope"];
const TEN = ["terminology", "roles", "dues", "authorities", "rules",
             "policies", "procedures", "results", "domains", "exceptions"];

// My assignment, exactly as written in the pre-registration.
const MINE = [
  ["method", "procedures", "strong"],
  ["scope", "domains", "strong"],
  ["figures", "rules", "medium"],
  ["figures", "results", "medium"],
  ["source", "authorities", "weak"],
];

// The assignment implied by the exchange: scope->domains, figures->results.
const THEIRS = [
  ["scope", "domains", "weak"],
  ["figures", "results", "weak"],
];

// A third reasonable reading, to test M5. Someone could argue a named source
// bears on terminology (it fixes what a word means here) and that "when"
// bears on exceptions (a claim true only in a period is an exception elsewhere).
const THIRD = [
  ["method", "procedures", "strong"],
  ["scope", "domains", "strong"],
  ["source", "terminology", "weak"],
  ["source", "authorities", "weak"],
  ["figures", "rules", "medium"],
  ["time", "exceptions", "weak"],
];

function measure(name, links) {
  const parts = SIGNALS.concat(TEN);
  const edges = links.map(l => [l[0], l[1], 1.0]);
  const covered = [...new Set(links.map(l => l[1]))].sort();
  const uncovered = TEN.filter(e => covered.indexOf(e) < 0).sort();

  // pieces, over the whole bipartite graph including isolated elements
  const b = ENG.bearings(parts, edges);
  return {
    name,
    links: links.length,
    covered, coveredN: covered.length,
    uncovered, uncoveredN: uncovered.length,
    pieces: b.pieces,
    parts: parts.length,
    totalBearing: b.total, expected: b.expected, conserved: b.conserved,
  };
}

const rows = [measure("mine", MINE), measure("theirs", THEIRS), measure("third", THIRD)];

// M5: is the covered set stable across readings? is the uncovered set?
const coveredSets = rows.map(r => new Set(r.covered));
const uncoveredSets = rows.map(r => new Set(r.uncovered));
function inter(sets) { return [...sets[0]].filter(x => sets.every(s => s.has(x))).sort(); }
function union(sets) { const u = new Set(); sets.forEach(s => s.forEach(x => u.add(x))); return [...u].sort(); }

process.stdout.write(JSON.stringify({
  signals: SIGNALS, ten: TEN,
  rows,
  coveredAgreedByAll: inter(coveredSets),
  coveredClaimedByAny: union(coveredSets),
  uncoveredAgreedByAll: inter(uncoveredSets),
  countsDiffer: [...new Set(rows.map(r => r.coveredN))].length > 1,
}, null, 1));
