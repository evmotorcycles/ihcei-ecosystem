import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
globalThis.LMD = require(join(here, "..", "smi", "lmd.js"));
globalThis.PLEXUS = require(join(here, "engines.js"));
const M = require(join(here, "metaphor.js"));
const LIB = require(join(here, "metaphorlib.js"));

const out = { order: LIB.metaphors.map(m => m.id), ours: LIB.OURS, audits: {} };
for (const m of LIB.metaphors) out.audits[m.id] = M.audit(m);
out.tally = M.tally(LIB.metaphors);

// the 1/m^2 law, on metaphors this time
out.law = {};
for (let m = 1; m <= 3; m++) {
  const fake = {
    id: "shape-" + m, name: "A shape with " + m, says: "x", where: "the suite",
    predicts: Array.from({ length: m }, (_, i) => (
      { says: "prediction " + (i + 1), presenterControls: false })),
  };
  const r = M.audit(fake);
  out.law[m] = { settles: r.predictions.map(p => p.settles), structure: r.structure };
}

// refusals
out.refusals = {};
function refuse(name, mutate) {
  const m = JSON.parse(JSON.stringify(LIB.metaphors[0]));
  mutate(m);
  let why;
  try { why = M.problems(m); } catch (e) { why = "THREW: " + e.message; }
  out.refusals[name] = why;
}
refuse("ok", () => {});
refuse("noPredictsField", m => { delete m.predicts; });
refuse("noControlFlag", m => { delete m.predicts[0].presenterControls; });
refuse("emptyPrediction", m => { m.predicts[0].says = "   "; });
refuse("noWhere", m => { delete m.where; });
refuse("badId", m => { m.id = "Corpuscles"; });

process.stdout.write(JSON.stringify(out, null, 1));
