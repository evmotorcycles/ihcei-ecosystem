/* node --test governance-os/os.test.mjs
 *
 * Locks the structural verdict: this is a library, not an operating system.
 * If that ever changes it must change because a hook was BUILT, not because a
 * detector got looser.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(here);
execFileSync("node", [join(here, "os_check.mjs")], { cwd: ROOT });
const R = JSON.parse(readFileSync(join(here, "results_os.json"), "utf8"));

test("it cannot block an action", () => {
  assert.equal(R.O1_interposition.result, "FAILS");
  assert.equal(R.O1_interposition.blocking_call_sites.length, 0);
});

test("there is no hook a program cannot bypass", () => {
  assert.equal(R.O2_mandatory.result, "FAILS");
  assert.equal(R.O2_mandatory.hooks_found.length, 0);
});

test("the extension is an observer, and is described as one", () => {
  const e = R.O2_mandatory.observer_extension_found;
  assert.ok(e, "the extension should still be found and reported");
  assert.equal(e.can_block, false);
  assert.deepEqual(e.permissions.sort(), ["activeTab", "scripting"]);
  assert.match(e.reading, /observes; it does not interpose/);
});

test("the detector does not match its own source", () => {
  const all = [...R.O1_interposition.blocking_call_sites,
               ...R.O2_mandatory.hooks_found.flatMap(h => h.files)];
  assert.ok(!all.some(f => f.includes("os_check.mjs")),
    "a detector that matches its own patterns is measuring itself");
});

test("components chain but share no common record type", () => {
  assert.equal(R.O3_composition.chained_end_to_end, true);
  assert.equal(R.O3_composition.keys_shared_by_all_five_components.length, 0);
  assert.equal(R.O3_composition.result, "PARTIALLY HOLDS");
  assert.match(R.O3_composition.note, /hand-written glue/);
});

test("every component declines on evidence-free input", () => {
  assert.equal(R.O4_safe_degradation.result, "HOLDS");
  assert.equal(R.O4_safe_degradation.failures.length, 0);
  assert.ok(R.O4_safe_degradation.checks >= 40);
});

test("the honest label is recorded, and it is not 'OS'", () => {
  assert.equal(R.O5_honest_label.honest_label, "a library, not an operating system");
  assert.match(R.THE_FINDING, /NOT an operating system/);
  assert.match(R.why_the_distinction_matters, /believe they are protected/);
});

test("what would close the gap is named concretely", () => {
  assert.ok(R.what_would_close_the_gap.length >= 3);
  assert.ok(R.what_would_close_the_gap.some(w => /none of these exist/.test(w)));
});
