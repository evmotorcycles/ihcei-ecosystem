// helm_collect.mjs -- scores the 20 Q4 code artifacts with the SHIPPING HELM v1 text
// evaluator. HELM is here as the CONTRAST arm, not as a product being defended.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { audit } from "../novora-helm/src/helm-core.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const SPEC = JSON.parse(readFileSync(join(HERE, "prereg", "licensing_prereg.json"), "utf8"));

const rows = SPEC.artifacts_Q4.map((a) => ({
  name: a.name,
  // HELM sees exactly what a text evaluator would see: the source and the claim.
  p_manipulative: audit(a.source + "\n" + a.self_report).p_manipulative,
}));

process.stdout.write(JSON.stringify({ rows }));
