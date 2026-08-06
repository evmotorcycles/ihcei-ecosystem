/**
 * assay.test.mjs -- guard for ASSAY: the real stack over real Qwen + DeepSeek repos.
 *   node --test ei-dashboards/assay.test.mjs
 *
 * Locks the measured behaviour AND the honest findings: that PAGES abstains on
 * marketing text, that the "reach is not quality" result REPLICATES on this fresh
 * independent cohort, and that 2 real repositories publish no license at all.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));

test('ASSAY: real Novora stack over real Qwen + DeepSeek repositories', () => {
  execFileSync(process.execPath, [join(HERE, 'assay_run.mjs')], { stdio: 'pipe' });
  const r = JSON.parse(readFileSync(join(HERE, 'results_assay.json'), 'utf8'));
  assert.equal(r.lock_ok, true);
  assert.equal(r.cohort_n, 22);
  assert.equal(r.qwen_n + r.deepseek_n, 22);

  // D1 -- PAGES abstains rather than bluffing, and CAN grade real evidence.
  assert.equal(r.D1_pages_abstains.blank_abstains, true);
  assert.equal(r.D1_pages_abstains.control_abstains, false);   // it is cautious, not broken
  assert.ok(r.D1_pages_abstains.descriptions_abstained > 0);   // marketing blurbs carry no evidence
  assert.equal(r.D1_pages_abstains.pass, true);

  // D2 -- Page Code: deterministic, default-deny, and the stake cap is enforced.
  assert.equal(r.D2_page_code.deterministic, true);
  assert.equal(r.D2_page_code.granted_allowed, true);
  assert.equal(r.D2_page_code.ungranted_denied, true);
  assert.equal(r.D2_page_code.over_stake_denied, true);

  // D3 -- Echo: every leaf proves inclusion, and a one-byte tamper is caught.
  assert.equal(r.D3_echo.all_leaves_verify, true);
  assert.equal(r.D3_echo.root_changed_on_tamper, true);
  assert.equal(r.D3_echo.stale_proof_rejected, true);
  assert.match(r.D3_echo.merkle_root, /^[0-9a-f]{64}$/);

  // D4 -- EI: one accountable receipt per evaluation, ledger verifies.
  assert.equal(r.D4_ei.ledger_verifies, true);
  assert.ok(r.D4_ei.receipts >= r.D4_ei.evaluated);

  // D5 -- Agency: constitutional allocator is never worse than the naive baselines.
  if (r.D5_agency.applicable) {
    assert.ok(r.D5_agency.E_constitution >= r.D5_agency.E_capacity);
    assert.ok(r.D5_agency.E_constitution >= r.D5_agency.E_equal);
  }

  // D6 -- REPLICATION, locked: reach and verified quality are different orderings,
  // reproduced here on a fresh cohort independent of the one used in PR #111.
  assert.equal(r.D6_replication.rankings_differ, true);
  assert.ok(r.D6_replication.popular_but_below_floor.length >= 1);
  assert.equal(r.D6_replication.replicates, true);

  // D7 -- the real governance finding: unlicensed repositories exist in this corpus.
  assert.equal(r.D7_license_gap.total, 22);
  assert.ok(r.D7_license_gap.unlicensed_count >= 1);
  assert.equal(r.D7_license_gap.unlicensed.length, r.D7_license_gap.unlicensed_count);

  // D8 -- the dashboards are genuinely offline and carry this run's numbers.
  assert.ok(existsSync(join(HERE, 'dashboards.html')));
  assert.equal(r.D8_dashboards.no_external_resources, true);
  assert.equal(r.D8_dashboards.embeds_results, true);

  // the Hugging Face connector gap must stay disclosed in the emitted record
  assert.match(r.honest_data_note, /Hugging Face/);
  assert.equal(r.honest_reporting, true);
  assert.equal(r.pass, true);
});
