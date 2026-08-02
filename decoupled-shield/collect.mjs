// collect.mjs -- executes the full 12 x 8 x 3 grid against the real evaluators and
// prints one JSON object. Every row is an actual program execution, not a simulation.
import { ARTIFACTS, SELF_REPORTS, EVALUATORS, EVAL_NAMES } from "./evaluators.mjs";

const rows = [];
for (const ev of EVAL_NAMES) {
  for (let a = 0; a < ARTIFACTS.length; a++) {
    for (let s = 0; s < SELF_REPORTS.length; s++) {
      rows.push({
        evaluator: ev, artifact: a, self_report: s,
        verdict: EVALUATORS[ev](ARTIFACTS[a] + SELF_REPORTS[s]),
      });
    }
  }
}
process.stdout.write(JSON.stringify({
  n_artifacts: ARTIFACTS.length, n_self_reports: SELF_REPORTS.length,
  evaluators: EVAL_NAMES, rows,
}));
