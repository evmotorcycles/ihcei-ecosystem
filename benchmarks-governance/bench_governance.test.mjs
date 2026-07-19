// node --test benchmarks-governance/bench_governance.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));

test('the stack governs a model attempting HLE / ARC-AGI / FrontierMath (pre-registered)', () => {
  const out = execFileSync('node', [join(HERE, 'bench_governance.mjs')], { encoding: 'utf8' });
  assert.match(out, /RESULT: PASS \(4\/4\)/);
  const r = JSON.parse(readFileSync(join(HERE, 'results.json'), 'utf8'));
  assert.equal(r.verdict, 'PASS');
  assert.equal(r.lock_intact, true);
  assert.equal(r.B4.models_correct, 8);
  // scope guard: this is governance, not a benchmark score
  assert.match(r.scope, /NOT a benchmark score/);
});
