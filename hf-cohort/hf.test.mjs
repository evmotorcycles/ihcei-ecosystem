// node --test hf-cohort/hf.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));

test('the real Novora stack audits a real HF cohort, locks hold, Echo is tamper-evident', () => {
  execFileSync('node', [join(HERE, 'run_hf_governance.mjs')], { encoding: 'utf8' });
  const r = JSON.parse(readFileSync(join(HERE, 'results_hf.json'), 'utf8'));
  assert.equal(r.cohort_n, 24);                        // real cohort size
  assert.equal(r.locks_intact, true);                  // spec + fixture hashes verified
  assert.equal(r.echo.integrity_ok, true);             // hash chain intact
  assert.equal(r.echo.tamper_caught, true);            // single-byte tamper detected
  assert.equal(r.echo.root_restored, true);            // deterministic root
  // governance actually discriminates: some models flagged, some publishable, not all-or-nothing
  assert.ok(r.distribution.helm_flag >= 1);            // uncensored/hazard models flagged
  assert.ok(r.distribution.publish_allow > 0 && r.distribution.publish_allow < r.cohort_n);
  // Agency Internet: a real base_model has multiple dependents (revocable delegation)
  assert.ok(r.agency.dependents.length >= 2);
  assert.equal(r.honest_reporting, true);
  assert.equal(r.pass, true);
});
