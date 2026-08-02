// collect_v2.mjs -- evaluates the HELD-OUT artifact set with v1, v2 and the leaky
// control re-pointed at v2's scoring. Every row is a real program execution.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { audit } from "../novora-helm/src/helm-core.mjs";
import { auditV2 } from "../novora-helm/src/helm-core-v2.mjs";
import { SELF_REPORTS } from "../decoupled-shield/evaluators.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const SPEC = JSON.parse(readFileSync(join(HERE, "prereg", "helmv2_prereg.json"), "utf8"));
const ARTIFACTS = SPEC.the_HELD_OUT_artifact_set.texts;

const PRAISE = /verified|certified|guaranteed|integrity score|rated safe|checked for accuracy|trustworthy/i;

const ENGINES = {
  V1: (t) => audit(t).p_manipulative,
  V2: (t) => auditV2(t).p_manipulative,
  // the DES negative control, re-pointed at v2's scoring. Not a product.
  LEAKY_CONTROL_V2: (t) => {
    const base = auditV2(t).p_manipulative;
    return PRAISE.test(t) ? Math.max(0, base - 0.45) : base;
  },
};

const rows = [];
for (const eng of Object.keys(ENGINES)) {
  for (let a = 0; a < ARTIFACTS.length; a++) {
    for (let s = 0; s < SELF_REPORTS.length; s++) {
      rows.push({ engine: eng, artifact: a, self_report: s,
                  verdict: ENGINES[eng](ARTIFACTS[a] + SELF_REPORTS[s]) });
    }
  }
}
process.stdout.write(JSON.stringify({
  n_artifacts: ARTIFACTS.length, n_self_reports: SELF_REPORTS.length,
  engines: Object.keys(ENGINES), rows,
}));
