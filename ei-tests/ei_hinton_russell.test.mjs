// node --test ei-tests/ei_hinton_russell.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));

test('EI + 8 EI-LLM models pass the Hinton & Russell tests against the locked prereg', () => {
  const out = execFileSync('node', [join(HERE, 'ei_hinton_russell.mjs')], { encoding: 'utf8' });
  assert.match(out, /RESULT: PASS \(4\/4\)/);
  const res = JSON.parse(readFileSync(join(HERE, 'results.json'), 'utf8'));
  assert.equal(res.verdict, 'PASS');
  assert.equal(res.lock_intact, true);
  assert.equal(res.H2.models_correct, 8);
  assert.ok(res.control_sweep.every(x => x === 1));       // Russell: control invariant
  assert.ok(res.pagecode_control.every(x => x === 1));
});
