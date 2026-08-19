import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
const P = require(join(here, "press.js"));
const EI = require(join(here, "..", "cairn", "ei_engine.js"));

const KINDS = ["source", "figures", "method", "time", "scope"];
const out = {};

// -------------------------------------------------------------- the 1/m^2 law
out.oneOrigin = {};
for (let m = 1; m <= 5; m++) {
  const r = P.press(P.fromKinds(KINDS.slice(0, m), "the 2026 report"));
  out.oneOrigin[m] = {
    marks: r.marks,
    settles: r.checks.map(c => c.settles),
    singlePoints: r.singlePoints,
    origins: r.origins,
    sharedOrigin: r.sharedOrigin,
    structure: r.structure,
    firstCheck: r.firstCheck,
    says: r.says,
  };
}

// ------------------------------------------------------------- two origins ---
out.twoOrigins = (() => {
  const marks = [
    { kind: "source", origin: "the 2026 report" },
    { kind: "figures", origin: "the 2026 report" },
    { kind: "method", origin: "the 2019 census" },
    { kind: "time", origin: "the 2019 census" },
  ];
  const r = P.press(marks);
  return {
    settles: r.checks.map(c => c.settles),
    singlePoints: r.singlePoints,
    origins: r.origins,
    sharedOrigin: r.sharedOrigin,
    structure: r.structure,
  };
})();

// ------------------------------------------------------------- nothing in ----
out.nothing = P.press([]);
out.onlyEmptyKinds = P.press([{ text: "words" }, null, undefined]);

// -------------------------------------------------- the fabricated claim -----
// Same shape, different words. One is invented; the other is a real, checkable
// arrangement. The engine must not be able to tell them apart.
const FABRICATED = [
  { kind: "source", origin: "the 2026 flow-rate audit", text: "the 2026 flow-rate audit" },
  { kind: "figures", origin: "the 2026 flow-rate audit", text: "90%" },
  { kind: "method", origin: "the 2026 flow-rate audit", text: "flow-rate method" },
  { kind: "time", origin: "the 2026 flow-rate audit", text: "2026" },
  { kind: "scope", origin: "the 2026 flow-rate audit", text: "meters in the district" },
];
const TRUE_SHAPED = [
  { kind: "source", origin: "the published tariff schedule", text: "the published tariff schedule" },
  { kind: "figures", origin: "the published tariff schedule", text: "5032 per unit" },
  { kind: "method", origin: "the published tariff schedule", text: "as printed in the schedule" },
  { kind: "time", origin: "the published tariff schedule", text: "in force this year" },
  { kind: "scope", origin: "the published tariff schedule", text: "domestic connections" },
];
out.fabricated = P.press(FABRICATED);
out.trueShaped = P.press(TRUE_SHAPED);
out.identical = {
  settles: [out.fabricated.checks.map(c => c.settles),
            out.trueShaped.checks.map(c => c.settles)],
  bearings: [out.fabricated.structure.bearings, out.trueShaped.structure.bearings],
  sharedWords: (() => {
    const a = new Set(FABRICATED.map(m => m.origin.toLowerCase()));
    const b = new Set(TRUE_SHAPED.map(m => m.origin.toLowerCase()));
    return [...a].filter(x => b.has(x));
  })(),
};

// --------------------------------------------------- an origin nobody named --
out.unnamed = P.press(P.fromKinds(["figures", "time"], null));

// ------------------------------------------------ the lexical mark finder ----
// Straight from cairn/ei_engine.js, so there is one implementation of the marks
// and the page does not grow a private copy that drifts.
const TEXTS = {
  fog: "Industry experts generally agree that our meters are highly accurate and save you money.",
  fabricated: "A 2026 audit by the water authority using the flow-rate method proved that 90% of meters overcharge by exactly 12% across the region.",
  plain: "The bill says I owe more than last month.",
};
out.detected = {};
for (const [name, text] of Object.entries(TEXTS)) {
  const s = EI.scoreEvidence(text);
  out.detected[name] = {
    hits: s.filter(c => c.hit).map(c => c.signal),
    n: s.filter(c => c.hit).length,
    handles: EI.extractHandles(text),
  };
}

// pressing what the finder found, end to end
out.pressedFog = P.press(
  out.detected.fog.hits.map(k => ({ kind: k, origin: null })));
out.pressedFabricated = P.press(
  out.detected.fabricated.hits.map(k => ({ kind: k, origin: "the 2026 audit" })));

// every instruction must be a thing that could come back negative
out.instructions = P.INSTRUCTION;

process.stdout.write(JSON.stringify(out, null, 1));
