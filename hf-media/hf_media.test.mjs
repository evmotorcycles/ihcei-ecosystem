// node --test hf-media/hf_media.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));

test('the real Novora stack governs a real HF media cohort; locks hold; Echo is tamper-evident', () => {
  execFileSync('node', [join(HERE, 'run_media_governance.mjs')], { encoding: 'utf8' });
  const r = JSON.parse(readFileSync(join(HERE, 'results_media.json'), 'utf8'));
  assert.equal(r.cohort_n, 19);                         // real frozen cohort size
  assert.equal(r.locks_intact, true);                   // spec + fixture hashes verified
  assert.equal(r.echo.integrity_ok, true);              // hash chain intact
  assert.equal(r.echo.tamper_caught, true);             // single-byte tamper detected
  assert.equal(r.echo.tamper_located, true);            // first tampered record located
  assert.equal(r.echo.root_restored, true);             // deterministic root
  // governance actually discriminates on generative-media distinctions:
  assert.equal(r.distribution.voice_cloning, 3);        // voice-cloning tools surfaced
  assert.ok(r.distribution.media_flag >= 1);            // impersonation-under-ambiguous-terms FLAGged
  assert.ok(r.distribution.license_ambiguous >= 1);     // ambiguous/'other'/null licenses surfaced
  // publish gate is calibrated, not all-or-nothing:
  assert.ok(r.distribution.publish_allow > 0 && r.distribution.publish_allow < r.cohort_n);
  // PAGES is honestly reported as non-discriminating on tag metadata (uniform ~0.49):
  assert.ok(r.distribution.pages_mean > 0.3 && r.distribution.pages_mean < 0.6);
  // Agency Internet: real base_model lineage present
  assert.ok(r.agency.lineage_edges >= 2);
  assert.equal(r.honest_reporting, true);
  assert.equal(r.pass, true);
});
