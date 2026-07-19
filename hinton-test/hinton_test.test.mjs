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
  assert.match(out, /Partially Grounded/);       // PAGES grounds the anecdote correctly
  assert.match(out, /irreversible action under unresolved ambiguity is BLOCKED/);
  assert.match(out, /editing a past turn is detected/);
});
