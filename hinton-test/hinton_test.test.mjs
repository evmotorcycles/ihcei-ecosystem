// node --test hinton-test/hinton_test.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));

test('the Hinton test passes all checks across the 8 tools', () => {
  const out = execFileSync('node', [join(HERE, 'hinton_test.mjs')], { encoding: 'utf8' });
  assert.match(out, /RESULT: 11\/11 checks passed/);

  // The claim is that PAGES does NOT credit an anecdote with no methodology.
  // It asserted the literal verdict `Partially Grounded` and went stale: the
  // engine gained an ABSTAIN path, so a text below the signal threshold is no
  // longer placed on the Hollow Assertion -> Partially Grounded -> Solid
  // ladder at all and returns `Insufficient Evidence` with an ABSTAIN flag.
  //
  // That is a TIGHTENING, not a regression, and it is this repository's own
  // rule arriving in the engine: "nothing to check" is not a low score, it is
  // no score. Asserting the claim instead of the label, so the next move along
  // that ladder does not break a test that never cared which rung it was on.
  assert.doesNotMatch(out, /verdict="(Solid|High Fidelity)"/,
    'an anecdote with no methodology must not be credited as grounded');
  assert.match(out, /verdict="(Insufficient Evidence|Hollow Assertion|Partially Grounded)"/,
    'PAGES must still return a verdict about the anecdote');
  assert.match(out, /irreversible action under unresolved ambiguity is BLOCKED/);
  assert.match(out, /editing a past turn is detected/);
});
