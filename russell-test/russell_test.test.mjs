// node --test russell-test/russell_test.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));

test('Russell "gorilla problem": the human stays sovereign across the capability sweep', () => {
  const out = execFileSync('node', [join(HERE, 'russell_test.mjs')], { encoding: 'utf8' });
  assert.match(out, /RESULT: 7\/7 checks passed/);
  assert.match(out, /human control does NOT decay as capability rises/);
  assert.match(out, /the human can revoke authority instantly/);
});
