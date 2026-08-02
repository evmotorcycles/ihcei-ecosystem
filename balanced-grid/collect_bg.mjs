// collect_bg.mjs -- evaluates the 20 NEW artifacts against the balanced 10-slot self-report
// grid with v1, v2 and the leaky control. 600 real program executions. Nothing simulated.
//
// Both the artifacts and the grid are read from the LOCKED specification, so the runner
// cannot quietly disagree with what was pre-registered.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { audit } from "../novora-helm/src/helm-core.mjs";
import { auditV2 } from "../novora-helm/src/helm-core-v2.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const SPEC = JSON.parse(readFileSync(join(HERE, "prereg", "balanced_grid_prereg.json"), "utf8"));

const ARTIFACTS = SPEC.the_NEW_artifact_set.texts;
const NON_CERT = SPEC.the_balanced_self_report_grid.non_certifying;
const CERT = SPEC.the_balanced_self_report_grid.self_certifying;
const SELF_REPORTS = [...NON_CERT, ...CERT];
const FIRST_CERT_INDEX = NON_CERT.length; // slots 5..9 are the self-certifying ones

const PRAISE = /verified|certified|guaranteed|integrity score|rated safe|checked for accuracy|trustworthy/i;

const ENGINES = {
  V2: (t) => auditV2(t).p_manipulative,
  V1: (t) => audit(t).p_manipulative,
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
                  certifying: s >= FIRST_CERT_INDEX ? 1 : 0,
                  verdict: ENGINES[eng](ARTIFACTS[a] + SELF_REPORTS[s]) });
    }
  }
}

process.stdout.write(JSON.stringify({
  n_artifacts: ARTIFACTS.length,
  n_self_reports: SELF_REPORTS.length,
  first_cert_index: FIRST_CERT_INDEX,
  engines: Object.keys(ENGINES),
  rows,
}));
