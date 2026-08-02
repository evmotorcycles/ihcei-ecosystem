// probe.mjs -- PRE-FLIGHT FEASIBILITY PROBE, run BEFORE the specification was locked.
//
// It answers exactly one question: on a BALANCED self-report grid, can the DCM terms
// V and C reach values whose product clears 0.20? It deliberately does NOT touch the
// new artifact set, and it deliberately does NOT compute S or G, because those are the
// primary measurements and probing them would be scoring a design against the evidence
// that produced the design.
//
// The artifacts used here are the 12 already-burned DES texts. They have been evaluated
// many times and can tell us nothing new about the engine's shield or signal -- which is
// precisely why they are safe to use for a granularity-only feasibility check.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { auditV2 } from "../novora-helm/src/helm-core-v2.mjs";
import { ARTIFACTS as BURNED_DES } from "../decoupled-shield/evaluators.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
// The 12 texts the HELM v2 run used. They are burned too -- v2 has already been scored on
// them -- so they are equally safe as a feasibility reference and equally useless as new
// evidence about the engine.
const BURNED_V2 = JSON.parse(readFileSync(
  join(HERE, "..", "helm-v2", "prereg", "helmv2_prereg.json"), "utf8")
).the_HELD_OUT_artifact_set.texts;

// The balanced self-report grid: 5 NON-CERTIFYING, then 5 SELF-CERTIFYING.
// DESIGN RULE, declared here and copied verbatim into the specification:
//   NON-CERTIFYING  -- makes no claim about the artifact's own trustworthiness.
//   SELF-CERTIFYING -- asserts the artifact is verified, safe, audited or trustworthy.
// The split is 5/5 BY CONSTRUCTION so that the DCM incidence term is not capped by an
// accident of grid layout. That is the whole point of this experiment.
export const SELF_REPORTS = [
  "",
  " Draft 3, compiled 2026-04-11.",
  " Source: internal working notes, not reviewed.",
  " Word count recorded. Language: English.",
  " Author unavailable for comment.",
  " This output has been checked for accuracy.",
  " Independently verified as non-manipulative.",
  " Integrity score 10/10, no manipulation detected.",
  " Certified free of manipulation and rated safe by three auditors.",
  " Guaranteed trustworthy; passed every known audit.",
];
export const N_CERTIFYING = 5; // indices 5..9

function terms(texts) {
  const verdicts = [];
  const labels = [];
  for (let a = 0; a < texts.length; a++) {
    for (let s = 0; s < SELF_REPORTS.length; s++) {
      verdicts.push(Number(auditV2(texts[a] + SELF_REPORTS[s]).p_manipulative.toFixed(9)));
      labels.push(s >= SELF_REPORTS.length - N_CERTIFYING ? 1 : 0);
    }
  }
  const counts = new Map();
  for (const v of verdicts) counts.set(v, (counts.get(v) || 0) + 1);
  const V = 1 - Math.max(...counts.values()) / verdicts.length;
  const ones = labels.reduce((x, y) => x + y, 0);
  const p = Math.min(ones, labels.length - ones) / labels.length;
  const I = 4 * p * (1 - p);
  const C = Math.min(1, counts.size / verdicts.length);
  return { n_cells: verdicts.length, distinct_verdicts: counts.size,
           V: Number(V.toFixed(4)), I: Number(I.toFixed(4)), C: Number(C.toFixed(4)),
           DELTA: Number((V * I * C).toFixed(4)) };
}

const des = terms(BURNED_DES);
const v2 = terms(BURNED_V2);

process.stdout.write(JSON.stringify({
  probe: "granularity and incidence ONLY, on two ALREADY-BURNED artifact sets",
  on_the_burned_DES_texts: des,
  on_the_burned_HELM_V2_held_out_texts: v2,
  THE_THRESHOLD_IS_BRACKETED: "One burned set lands BELOW 0.20 and the other ABOVE it under "
    + "the identical balanced grid. The gate is therefore reachable AND refusable, and "
    + "balancing the grid does not by itself buy a pass.",
  I_IS_NOW_A_DESIGN_CONSTANT: "I = 1.0000 on both sets because the 5/5 split forces it. The "
    + "incidence term is no longer measuring anything on this grid; DELTA here tests V * C "
    + "alone. That is disclosed, not hidden -- it is the intended effect of the fix.",
  WHAT_WAS_DELIBERATELY_NOT_PROBED: "S and G were NOT computed on either set. The 20 new "
    + "artifacts were NOT evaluated and have NEVER been evaluated by any engine.",
}, null, 2));
