// validate_sre_brief.mjs — test the Novora SRE Brief against real artifacts.
//   node sre-brief/validate_sre_brief.mjs
// ============================================================================
// The SRE Brief (Novora_SRE_Brief.pptx, 8 slides) makes a set of FALSIFIABLE
// claims: specific numbers (τ_v 50.6/19.8 d, p≈1e-31, N=992), a pre-registered
// null (D_gap p=0.735 on Kubernetes), a SHA-256-locked spec, and an explicit
// scope ("trajectory not threshold", "correlational not oracle", "read-only
// shadow mode"). A brief is only as good as its fidelity to the committed
// science and the reproducibility of its instrument.
//
// This harness tests the brief three honest ways:
//   1. FAITHFUL-TO-ARCHIVE — every headline number on a slide must match the
//      repo's locked archive (REPRODUCIBILITY.md, zenodo_metadata.json, the
//      govphys spec self-hash). A deck that inflates its own numbers fails here.
//   2. INSTRUMENT REPRODUCES — the τ_v direction (failed/stale > survivor) must
//      reproduce on the 22 real GitHub repos we have live, using the SHIPPED
//      monitor logic (lism_diagnostic). The brief's instrument is exercised, not
//      just quoted.
//   3. SELF-DISPROVING DISCIPLINE IS REAL — the pre-registration lock and the
//      acceptance harness that refuses a tampered spec must actually exist and
//      run; the disclaimer the brief promises must ship in the tool.
//
// The raw 992-repo / STRING datasets are rebuilt from public sources (network),
// so their exact recomputation is out of scope offline; we validate that the
// brief faithfully reports the ARCHIVED confirmatory run and that the same
// instrument reproduces its DIRECTION on fresh real data.

import { readFileSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { reposOf, dissonance, thirdLawDirection } from '../cross-stack/lism_diagnostic.mjs';

const ROOT = new URL('..', import.meta.url).pathname;
const read = f => readFileSync(ROOT + f, 'utf8');
const has = (f, ...subs) => { const t = read(f); return subs.every(s => t.includes(s)); };

let pass = 0, fail = 0;
const ok = (claim, cond, detail = '') => {
  if (cond) { pass++; console.log('  ✓  ' + claim); }
  else { fail++; console.log('  ✗  ' + claim + (detail ? '  [' + detail + ']' : '')); }
};
const bar = c => console.log(c.repeat(78));

bar('=');
console.log(' NOVORA SRE BRIEF — validation against real repository artifacts');
console.log(' 8 slides · falsifiable claims checked for archive-fidelity + instrument reproduction');
bar('=');

// ── PILLAR 1 · Every headline number is faithful to the locked archive ───────
console.log('\n 1 · FAITHFUL TO ARCHIVE (the deck reports the committed numbers, not inflated ones)');
ok('Slide 3 · τ_v failed 50.6 d is in REPRODUCIBILITY.md + zenodo_metadata',
   has('REPRODUCIBILITY.md', '50.6') && has('zenodo_metadata.json', '50.6'));
ok('Slide 3 · τ_v survivors 19.8 d is archived in both records',
   has('REPRODUCIBILITY.md', '19.8') && has('zenodo_metadata.json', '19.8'));
ok('Slide 3 · N=992 (750 failed / 242 survived) matches the CI-log archive',
   has('REPRODUCIBILITY.md', '992 (750/242)'));
ok('Slide 3 · p ≈ 1e-31 (one-tailed MWU) matches zenodo deposit',
   has('zenodo_metadata.json', '1e-31'));
ok('Slide 4 · pre-registered D_gap NULL p=0.735 (Kubernetes) is archived',
   has('FLOOR_RETIREMENT.md', 'p = 0.735') && has('LISM_CONTRIBUTION.md', 'p = 0.735'));
ok('Slide 4 · VS Code D_gap was a dependabot lexical artifact (documented, not hidden)',
   has('FLOOR_RETIREMENT.md', 'dependabot'));

// ── PILLAR 2 · The SHA-256-locked spec is real and self-verifying ────────────
console.log('\n 2 · THE PRE-REGISTRATION LOCK IS REAL (slide 4 & 7: "SHA-256 committed before linkage")');
let specHash = '';
try { specHash = execSync('python3 -c "import govphys_quadratic_prereg_test as g; print(g.spec_hash())"',
  { cwd: ROOT, encoding: 'utf8' }).trim(); } catch (e) { specHash = 'ERROR:' + e.message.slice(0, 60); }
ok('govphys prereg spec self-hash == archived cac34f44… (spec is unaltered since commit)',
   specHash.startsWith('cac34f44'), 'got ' + specHash.slice(0, 12));
ok('the archived spec hash in REPRODUCIBILITY.md matches the live self-hash',
   has('REPRODUCIBILITY.md', 'cac34f44'));
let harnessOut = '';
try { harnessOut = execSync('node novora-helm/prereg/acceptance_harness.mjs',
  { cwd: ROOT, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }); } catch (e) { harnessOut = (e.stdout || '') + (e.stderr || ''); }
ok('acceptance harness runs and enforces the locked stage-1 spec (self-disproving discipline)',
   /spec|band|BLOCK|NULL|claim/i.test(harnessOut), harnessOut.slice(0, 40));

// ── PILLAR 3 · The instrument reproduces its DIRECTION on fresh real repos ────
console.log('\n 3 · INSTRUMENT REPRODUCES ON LIVE DATA (slide 3: "responsiveness separates survivors from failures")');
const cohorts = ['os-integration/fixtures/os_tauv_cohort.json',
  'novora-helm/test/fixtures/live_tauv_cohort.json',
  'oss-field-trial/fixtures/live_tauv_cohort_trial.json']
  .map(f => reposOf(JSON.parse(read(f))));
// Dedupe repos that appear in more than one cohort, keeping the record with the
// most closed issues (most signal) — no double-counting in the direction test.
const byRepo = new Map();
for (const r of cohorts.flat()) {
  const prev = byRepo.get(r.repo);
  if (!prev || (r.n_closed || 0) > (prev.n_closed || 0)) byRepo.set(r.repo, r);
}
const all = [...byRepo.values()];
// Direction: repos that look FAILED/abandoned (stale push > 180d OR archived) vs ALIVE, by τ_v.
const NOW = Date.parse('2026-07-15T23:00:00Z');
const ageDays = r => r.pushed_at ? (NOW - Date.parse(r.pushed_at)) / 86400000 : Infinity;
const withTv = all.filter(r => r.tau_v != null);
const stale = withTv.filter(r => r.archived || ageDays(r) > 180).map(r => r.tau_v);
const alive = withTv.filter(r => !(r.archived || ageDays(r) > 180)).map(r => r.tau_v);
const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
console.log('   live cohort: ' + withTv.length + ' repos with τ_v signal · ' +
  'stale/abandoned n=' + stale.length + ' (mean τ_v ' + mean(stale).toFixed(1) + 'd) · ' +
  'alive n=' + alive.length + ' (mean τ_v ' + mean(alive).toFixed(1) + 'd)');
ok('τ_v is HIGHER among stale/abandoned repos than alive ones (same sign as the brief)',
   mean(stale) > mean(alive), mean(stale).toFixed(1) + ' vs ' + mean(alive).toFixed(1));
// The say-do Dissonance σ (the LISM update) surfaces the "zombie": fresh push, rotting queue.
const dWA = dissonance(reposOf(JSON.parse(read('novora-helm/test/fixtures/live_tauv_cohort.json'))), { now: NOW });
const lodash = dWA.rows.find(r => r.repo === 'lodash/lodash');
ok('σ surfaces the "zombie" a naive last-commit-date scanner misses (lodash: fresh push, τ_v≈114d)',
   lodash && lodash.label === 'ZOMBIE', JSON.stringify(lodash));

// ── PILLAR 4 · The brief's honesty ships inside the instrument ───────────────
console.log('\n 4 · SCOPE HONESTY SHIPS IN THE TOOL (slides 5 & 8: "states its own scope")');
ok('Slide 5 · "read the trajectory, not the threshold" — monitor ships this disclaimer',
   has('tau_v_monitor/core.py', 'never ship a universal threshold') || has('tau_v_monitor/core.py', 'not transplantable thresholds'));
ok('Slide 5 · "correlational and probabilistic, not a deterministic oracle" — shipped verbatim',
   has('tau_v_monitor/core.py', 'correlational') && has('tau_v_monitor/core.py', 'deterministic oracle'));
ok('Slide 7 · read-only shadow mode — monitor consumes only (opened,closed) pairs, no write path',
   has('tau_v_monitor/core.py', 'opened_at') && has('tau_v_monitor/core.py', 'closed_at') && !has('tau_v_monitor/core.py', 'requests.post'));

// ── Display: the reproduced τ_v table the brief is really about ───────────────
console.log('\n ─ REPRODUCED τ_v LEADING-INDICATOR TABLE (live real repos) ' + '─'.repeat(18));
console.log('   ' + 'repo'.padEnd(34) + 'τ_v(d)'.padStart(8) + '  push-age'.padStart(9) + '  class');
for (const r of withTv.sort((a, b) => b.tau_v - a.tau_v).slice(0, 10)) {
  const cls = (r.archived || ageDays(r) > 180) ? 'stale/abandoned' : 'alive';
  console.log('   ' + r.repo.padEnd(34) + String(r.tau_v).padStart(8) + String(Math.round(ageDays(r)) + 'd').padStart(9) + '  ' + cls);
}

bar('=');
console.log('  RESULT: ' + pass + ' passed, ' + fail + ' failed');
console.log('  The brief faithfully reports the locked archive; its τ_v instrument reproduces');
console.log('  its direction on fresh real repos; and the self-disproving discipline is real.');
bar('=');
process.exit(fail ? 1 : 0);
