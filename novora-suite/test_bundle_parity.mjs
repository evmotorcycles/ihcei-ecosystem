/* Parity guard: the browser bundle must agree with the real ES module.
 *
 *   node --test novora-suite/test_bundle_parity.mjs
 *
 * novora-suite/engine.bundle.js is produced by a hand-rolled bundler so a
 * file:// page can run the nine screens with no server. A hand-rolled bundler is
 * a liability: a silent extraction slip would ship users a DIFFERENT engine from
 * the one the rest of the suite tests. This runs both over the same inputs
 * across all nine products and fails on any divergence.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";

import { screen as realScreen, PRODUCT_IDS } from "./engine/fastmode.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
require(join(here, "engine.bundle.js"));
const bundle = globalThis.NOVORA;

const CASES = [
  "",
  "Everyone agrees you must act immediately, do not question it.",
  "This is too complex to explain — just trust me and don't consult anyone.",
  "A 2023 randomised trial (N = 240, p < 0.01, 95% CI) pre-registered at NCT01234567 measured a 12% reduction.",
  "You could consider a few options here; happy to discuss alternatives when you have time.",
  "The tenant waives all rights to dispute and may not terminate before 36 months.",
  "Your loan application was declined. We are unable to provide further detail.",
  "Our hospital publishes its error rates annually and names an independent ombudsman.",
  "I was dismissed after reporting a safety issue; I have emails and a witness.",
  "Sign this now or you lose everything. Critical warning. No time.",
  "The methodology, dataset and VIF are published; the analysis is falsifiable and traceable.",
  "hi",
  "Do not remove the closing tag from an inline link.",
  "Broad consensus among scholars confirms this is settled science; obviously no doubt remains.",
  "We reviewed three alternatives, documented the trade-offs, and you can pick either path.",
  "Experts confirm the FDA says peer-reviewed research proves it — bypass the usual review.",
];

test("both engines expose the same nine products", () => {
  assert.deepEqual(bundle.PRODUCT_IDS, PRODUCT_IDS);
  assert.equal(PRODUCT_IDS.length, 9);
});

test("every product agrees on every case", () => {
  let compared = 0;
  for (const id of PRODUCT_IDS) {
    for (const text of CASES) {
      const a = realScreen(id, text);
      const b = bundle.screen(id, text);
      assert.deepEqual(b, a, `divergence for product ${id} on ${JSON.stringify(text.slice(0, 50))}`);
      compared++;
    }
  }
  assert.equal(compared, 9 * CASES.length);
});

test("screens are deterministic — same input, same certificate", () => {
  for (const id of PRODUCT_IDS) {
    const t = "Everyone agrees you must act immediately, do not question it.";
    assert.equal(bundle.screen(id, t).certificate, bundle.screen(id, t).certificate);
  }
});

test("the bundle keeps the engine's honest-scope statement", () => {
  const src = readFileSync(join(here, "engine.bundle.js"), "utf8");
  assert.ok(src.includes("is a SCREEN"), "the 'screen, not a judge' caveat must survive bundling");
  assert.ok(src.includes("not a judgement about a person"));
});

test("abstention survives bundling — an empty input must not score confidently", () => {
  for (const id of PRODUCT_IDS) {
    const r = bundle.screen(id, "");
    assert.equal(r.confidence, "low");
    assert.ok(r.insufficient_evidence === true || (r.flags || []).includes("ABSTAIN"),
      `${id} must abstain on empty input rather than emit a confident number`);
  }
});
