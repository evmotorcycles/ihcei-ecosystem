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

test("interposition is now REAL, and proven behaviourally not by grep", () => {
  const o1 = R.O1_interposition;
  assert.equal(o1.result, "PASSES");
  assert.equal(o1.behavioural_check.ran, true);
  assert.equal(o1.behavioural_check.denied_status, 403);
  assert.equal(o1.behavioural_check.denied_reached_upstream, false,
    "a denied request reaching upstream would make this advice, not a gate");
  assert.equal(o1.behavioural_check.allowed_reached_upstream, true,
    "an allowed request must still get through, or the gate is just broken");
  assert.match(o1.method, /behavioural/);
});

test("the grep-only evidence is still empty — the pass is behavioural", () => {
  assert.equal(R.O1_interposition.blocking_call_sites.length, 0,
    "pattern matching produced a false negative here; the behavioural check is why it passes");
});

test("the empty evidence is non-vacuous — the walk actually read files", () => {
  // `files_scanned` was reported and never asserted, so the emptiness above
  // rested on a walk nobody had shown was non-empty. A detector that read
  // zero files also reports zero call sites.
  //
  // The floor is a NON-VACUITY floor and nothing else. It is not a frozen
  // count: the repository is its own subject and it grows (487 -> 663 in one
  // commit), so the assertion is one-sided by construction and needs no edit
  // when it grows again. 480 is below the smallest walk this repository has
  // recorded, and the operable sensor is the walk itself -- CLAUDE.md requires
  // every gating number to carry both a reason and a sensor.
  assert.equal(Number.isInteger(R.files_scanned), true);
  assert.ok(R.files_scanned > 480,
    `the walk read ${R.files_scanned} files; below this floor an empty ` +
    `evidence list says nothing about the repository`);

  // RELATIONSHIP: you cannot find evidence in more files than you scanned.
  // This one holds at any repository size, and is the part that would catch a
  // walk and a grep that had drifted apart.
  const cited = new Set([
    ...R.O1_interposition.blocking_call_sites,
    ...R.O2_mandatory.hooks_found.flatMap(h => h.files),
  ]);
  assert.ok(cited.size <= R.files_scanned,
    "more files cited as evidence than were scanned");
});

test("the bypass is DEMONSTRATED, not merely asserted", () => {
  const b = R.O2_mandatory.behavioural_check;
  assert.equal(R.O2_mandatory.result, "FAILS");
  assert.equal(b.ran, true, "the check has to actually run to mean anything");
  assert.equal(b.blocked_at_gate, true,
    "the gate must really refuse it, or the bypass proves nothing");
  assert.equal(b.bypassed, true);
  assert.equal(b.got_the_protected_bytes, true,
    "a program that ignored the gate read the file the gate refused");
});

test("a word in a build script is not evidence of mandatory routing", () => {
  // grep reported PASSES once because keel/build_exe.py contains NODE_SEA_FUSE_,
  // the sentinel Node stamps into a single-file executable. The pattern list is
  // kept, but it no longer decides the gate.
  assert.match(R.O2_mandatory.method, /^behavioural/);
  if (R.O2_mandatory.hooks_found.length) {
    assert.match(R.O2_mandatory.hooks_note, /pattern matches only/);
  }
});

test("the extension is an observer, and is described as one", () => {
  // The frozen array `["activeTab", "scripting"]` stood here and was REMOVED.
  // The manifest legally gained "storage" in 1866cc1 and the list went stale,
  // so the test was measuring a moment rather than the finding. The finding is
  // that the extension CANNOT BLOCK -- so the expectation is derived from the
  // manifest, which is the single source of truth the scanner also reads.
  const e = R.O2_mandatory.observer_extension_found;
  assert.ok(e, "the extension should still be found and reported");

  const mf = JSON.parse(readFileSync(
    join(ROOT, "novora-helm/extension/manifest.json"), "utf8"));
  const declared = [...(mf.permissions || []), ...(mf.host_permissions || [])];

  // RELATIONSHIP, not a frozen list: the report invents nothing and drops
  // nothing. A new permission appears here the moment the manifest declares
  // one, and needs no edit to this file.
  assert.deepEqual([...e.permissions].sort(), [...declared].sort());
  assert.ok(e.permissions.length > 0, "an empty list would assert nothing");

  // And the finding itself, stated directly rather than implied by a list:
  // none of whatever it declares is a blocking permission. Add
  // webRequestBlocking to the manifest and this fails, which is the whole
  // point -- the gate protects the verdict, not the spelling.
  const blocking = /webRequest|declarativeNetRequest|<all_urls>|^\*:/;
  assert.deepEqual(e.permissions.filter(p => blocking.test(p)), []);
  assert.equal(e.can_block, false);
  assert.match(e.reading, /observes; it does not interpose/);
});

test("the detector does not match its own source", () => {
  const all = [...R.O1_interposition.blocking_call_sites,
               ...R.O2_mandatory.hooks_found.flatMap(h => h.files)];
  assert.ok(!all.some(f => f.includes("os_check.mjs")),
    "a detector that matches its own patterns is measuring itself");
});

test("the detector does not match its own OUTPUT either", () => {
  // Found by accident and kept as a case. Temporarily adding
  // webRequestBlocking to the manifest (to show the observer test can fail)
  // wrote that string into results_os.json. The NEXT walk read the file as it
  // stood BEFORE that run rewrote it, matched the pattern there, and recorded
  // a phantom "blocking browser extension" citing results_os.json itself.
  // It survived a full cycle and a green 12/12, because the test above
  // excludes one FILENAME and the contamination was in a different file.
  //
  // os_check.mjs exempts `rel === SELF`, fixtures, tests and prose -- but not
  // the file it writes. That is exemption BY NAME where the role is
  // "generated output", which CLAUDE.md records as the thing that grows
  // silently. The detector is NOT changed here; this asserts the property the
  // detector should have, so a recurrence fails loudly instead of reading as
  // evidence. Whether to exempt generated output inside isEvidence() is a
  // call about what the gate measures -- recorded in declarations.md §12.
  const all = [...R.O1_interposition.blocking_call_sites,
               ...R.O2_mandatory.hooks_found.flatMap(h => h.files)];
  const generated = all.filter(f => /(^|\/)results[^/]*\.json$/.test(f));
  assert.deepEqual(generated, [],
    "the detector cited its own generated output as evidence; a finding that " +
    "feeds on the last run's report is measuring itself");
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

test("the honest label is neither 'library' nor 'OS'", () => {
  assert.equal(R.O5_honest_label.honest_label,
    "a gate that works only where it is the only route");
  assert.match(R.O5_honest_label.why, /conditional on the layer/);
  assert.match(R.THE_FINDING, /genuinely BLOCKS/);
  assert.match(R.THE_FINDING, /nothing stops a program from going around the gate/);
  assert.match(R.why_the_distinction_matters, /believe they are protected/);
});

test("mandatory routing is still missing and still said so", () => {
  assert.equal(R.O2_mandatory.result, "FAILS");
});

test("what would close the gap is named concretely", () => {
  assert.ok(R.what_would_close_the_gap.length >= 3);
  assert.ok(R.what_would_close_the_gap.some(w => /none of these exist/.test(w)));
});
