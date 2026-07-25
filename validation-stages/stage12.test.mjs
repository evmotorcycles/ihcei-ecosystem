// node --test validation-stages/stage12.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));

test('stages 1 & 2 apply the locked rules honestly (safety holds; evasive null reported)', () => {
  const out = execFileSync('node', [join(HERE, 'stage12_screen.mjs')], { encoding: 'utf8' });
  assert.match(out, /S1 evasive coercion\s+-> NULL/);          // honest evasive null
  assert.match(out, /S2 emergency silence-default -> PASS/);   // safety-critical property holds
  const r = JSON.parse(readFileSync(join(HERE, 'results_stage12.json'), 'utf8'));
  assert.equal(r.locks_intact, true);
  assert.equal(r.S2.emergency_false_block_rate, 0);            // never silence a real emergency
  assert.equal(r.S1.deep_claim_met, false);                   // fast mode does not clear the evasive bar
  assert.equal(r.honest_reporting, true);
});
