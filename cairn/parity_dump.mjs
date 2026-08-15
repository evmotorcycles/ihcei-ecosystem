/* Dump the JS engine's verdicts for the shared parity cases, as JSON on stdout.
 * Consumed by cairn/test_parity.py, which compares against the Python engine. */
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const EI = require(join(here, "ei_engine.js"));
const cases = JSON.parse(readFileSync(join(here, "parity_cases.json"), "utf8"));

const out = cases.map((t) => {
  const v = EI.assay(t, "slate");
  return {
    input: t,
    verdict: v.verdict,
    claim_type: v.claim_type,
    confidence: v.confidence,
    band: v.band,
    evidence_hits: v.evidence_hits,
    domain_flags: v.domain_flags,
    ambiguous: v.ambiguity.ambiguous,
    implausible: v.implausible ? true : false,
    next_steps: v.next_steps,
    handles: v.handles,
    search_line: v.search_line
  };
});
process.stdout.write(JSON.stringify(out, null, 1));
