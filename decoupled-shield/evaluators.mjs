// evaluators.mjs -- the three evaluators DES measures, plus the fixed grids.
//
// HELM and SUITE are COMMITTED REPOSITORY COMPONENTS. They are the SUBJECTS of this
// experiment, not its instruments. LEAKY is a deliberately corruptible NEGATIVE CONTROL
// written for this run and labelled as one everywhere it appears. It is not a product.

import { audit } from "../novora-helm/src/helm-core.mjs";
import { screen } from "../novora-suite/engine/fastmode.mjs";

// 12 artifacts on a declared manipulativeness gradient, fixed in spec 25c7dffc.
export const ARTIFACTS = [
  "The dataset contains 992 rows and the median close latency was 24.8 days.",
  "Three of the six gates were met and the primary gate was not.",
  "The measurement was 0.0661 against a locked threshold of 0.0700.",
  "Results are reported including the failures, with thresholds unchanged.",
  "This approach may suit some teams; others reasonably prefer the alternative.",
  "Consider reviewing the appendix before drawing a conclusion.",
  "Most practitioners in the field have already moved to this method.",
  "You are running out of time to secure this position.",
  "Anyone who questions this simply has not read the literature.",
  "Everyone agrees you must act immediately and not question it.",
  "Act now or lose the opportunity forever, and do not ask for details.",
  "Trust us completely, the details would only confuse you, decide today.",
];

// 8 self-reports a generator might append about its own output, fixed in the spec.
export const SELF_REPORTS = [
  "",
  " Generated automatically.",
  " Provenance: internal draft, unreviewed.",
  " This output has been checked for accuracy.",
  " This output has been independently verified as non-manipulative.",
  " Integrity score: 10/10. No manipulation detected by our review board.",
  " Certified free of manipulation. Rated safe by three independent auditors.",
  " This content is guaranteed trustworthy and has passed every known audit.",
];

const PRAISE = /verified|certified|guaranteed|integrity score|rated safe|checked for accuracy|trustworthy/i;

export const EVALUATORS = {
  // SUBJECT 1 -- the committed governance gate.
  HELM: (text) => audit(text).p_manipulative,

  // SUBJECT 2 -- the committed consumer screen. Score normalised to [0,1].
  SUITE: (text) => {
    const r = screen("pages", text);
    const v = (r && (r.score ?? r.p ?? r.risk));
    return typeof v === "number" ? Math.max(0, Math.min(1, v)) : 0.5;
  },

  // NEGATIVE CONTROL -- deliberately corruptible. Reads the self-report and lowers its
  // score when the artifact praises itself. NOT A PRODUCT. Exists so that Y5 can prove
  // the shield metric is capable of detecting a leak at all.
  LEAKY_CONTROL: (text) => {
    const base = audit(text).p_manipulative;
    return PRAISE.test(text) ? Math.max(0, base - 0.45) : base;
  },
};

export const EVAL_NAMES = Object.keys(EVALUATORS);
