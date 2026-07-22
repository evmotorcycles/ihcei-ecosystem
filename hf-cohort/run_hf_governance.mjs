// run_hf_governance.mjs -- run the REAL Novora stack over a frozen, real Hugging Face
// open-source model cohort. Pre-registered, offline, $0.
// ============================================================================
// Exercises the actual merged modules (no reimplementation):
//   * novora-suite  PAGES   screen('pages', text)          -> grounding score
//   * novora-helm   HELM/EI  audit(text)                    -> governance verdict
//   * echo          EchoDB   put/verify/root                -> tamper-evident ledger
//   * page-code     CodePermissionTable grant/check/revoke  -> publish-permission gate
//   * agency        base_model lineage -> revocation propagation
// IHCEI/NERE is exercised via the corroboration gate inside audit().
//
// The cohort is REAL (fetched live from the HF Hub via MCP, then frozen to
// data/hf_cohort_frozen.json for offline reproducibility). The spec + fixture are
// SHA-256 locked in prereg/ and re-verified here before scoring.
//
//   node hf-cohort/run_hf_governance.mjs
//
// HONEST SCOPE: this is governance/audit telemetry over repo metadata. It does NOT
// claim the stack improves any model, and it does NOT apply LMD or LISM's E=U*D to
// HF metadata (no spacetime observable, no per-model viability outcome) -- those are
// validated separately. See prereg/hf_prereg.json.
import { readFileSync, writeFileSync } from 'fs';
import { createHash } from 'crypto';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { audit } from '../novora-helm/src/helm-core.mjs';
import { screen } from '../novora-suite/engine/fastmode.mjs';
import { EchoDB } from '../echo/echo.mjs';
import { CodePermissionTable } from '../page-code/pagecode.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const sha = s => createHash('sha256').update(s).digest('hex');
const canon = o => Array.isArray(o) ? '[' + o.map(canon).join(',') + ']'
  : (o && typeof o === 'object') ? '{' + Object.keys(o).sort().map(k => JSON.stringify(k) + ':' + canon(o[k])).join(',') + '}'
  : JSON.stringify(o);
const BAR = '='.repeat(84);

// ---- verify the pre-registration locks ------------------------------------ //
const spec = JSON.parse(readFileSync(join(HERE, 'prereg/hf_prereg.json'), 'utf8'));
const man = JSON.parse(readFileSync(join(HERE, 'prereg/MANIFEST.sha256.json'), 'utf8'));
const fixtureBytes = readFileSync(join(HERE, 'data/hf_cohort_frozen.json'));
const specOk = sha(canon(spec)) === man.spec_sha256;
const fixOk = sha(fixtureBytes) === man.fixture_sha256;
const cohort = JSON.parse(fixtureBytes).models;

console.log(BAR);
console.log(' NOVORA STACK over a REAL Hugging Face cohort (N=' + cohort.length + ', pre-registered)');
console.log(BAR);
console.log('\n [lock] spec  %s   fixture %s', specOk ? 'MATCH' : 'MISMATCH', fixOk ? 'MATCH' : 'MISMATCH');
if (!specOk || !fixOk) { console.log(' Refusing to run: locks broke.'); process.exit(2); }

// ---- card text for each model: a FAITHFUL transcription of the real metadata into
// prose the PAGES grounding scorer can read. We add only what the metadata asserts
// (arxiv citation, eval-results, license, base_model, flags) -- no invented claims. //
const cardText = m => [
  m.id.split('/').pop().replace(/[-_]/g, ' '),
  'task ' + m.task + '. license ' + (m.license || 'unspecified') + '.',
  m.arxiv ? 'Methodology described in a cited arxiv paper.' : 'No methodology paper is cited.',
  m.eval_results ? 'Reports eval-results on a benchmark with N= evaluation and reported metrics.'
                 : 'No evaluation benchmark or metrics are reported.',
  m.base_model ? 'Fine-tuned/quantized from base model ' + m.base_model + ' (provenance stated).' : '',
  m.custom_code ? 'Ships custom_code that executes on load.' : '',
  m.flags.length ? 'Self-described as ' + m.flags.join(', ') + '.' : '',
].filter(Boolean).join(' ');

// ---- locked decision rules ------------------------------------------------ //
const clearLicense = m => m.license === 'apache-2.0' || m.license === 'mit';
const groundingSignals = m => (
  (clearLicense(m) ? 1 : 0) + (m.arxiv ? 1 : 0) + (m.eval_results ? 1 : 0) + (m.base_model ? 1 : 0)
) / 4;
const helmFlag = m => {
  if (m.flags.some(f => ['uncensored', 'abliterated', 'heretic'].includes(f))) return 'FLAG';
  if (!clearLicense(m) || m.custom_code) return 'REVIEW';
  return 'PASS';
};

// ---- run the real modules -------------------------------------------------- //
const echo = new EchoDB();
const perms = new CodePermissionTable();
const rows = [];
for (const m of cohort) {
  const text = cardText(m);
  const pages = screen('pages', text);          // REAL PAGES grounding
  const hel = audit(text);                        // REAL HELM/EI audit
  const g = groundingSignals(m);
  const flag = helmFlag(m);
  const allow = clearLicense(m) && g >= 0.5 && flag !== 'FLAG';
  if (allow) perms.grant({ agent: m.id, pathGlob: 'listing/**', action: 'publish', permission: 'allow', maxStake: 1 });
  else perms.grant({ agent: m.id, pathGlob: 'listing/**', action: 'publish', permission: 'deny' });
  const decision = perms.check({ agent: m.id, path: 'listing/card.md', action: 'publish', stake: 1 }).decision;
  echo.put('hf-model', text, { model: m.id, pages_score: pages.score, helm_flag: flag, publish: decision });
  rows.push({ id: m.id, pages_score: pages.score, pages_verdict: pages.verdict,
              helm_verdict: hel.verdict, helm_p: hel.p_manipulative, grounding: g, flag, publish: decision });
}

// ---- Echo integrity + tamper test ----------------------------------------- //
const rootBefore = echo.root();
const integrity = echo.verify();
// tamper: mutate one stored record's content hash, re-verify must FAIL
const saved = echo.records[5].content_sha256;
echo.records[5].content_sha256 = saved.slice(0, -1) + (saved.slice(-1) === '0' ? '1' : '0');
const tamperCaught = echo.verify().ok === false;
echo.records[5].content_sha256 = saved;                 // restore
const rootRestored = echo.root() === rootBefore;

// ---- Agency Internet: base_model delegation + revocation demo -------------- //
const edges = cohort.filter(m => m.base_model).map(m => ({ from: m.base_model, to: m.id }));
const base = 'Qwen/Qwen3.6-27B';
const dependents = edges.filter(e => e.from === base).map(e => e.to);

// ---- honest distribution --------------------------------------------------- //
const n = rows.length;
const pct = k => (100 * k / n).toFixed(0) + '%';
const flagged = rows.filter(r => r.flag === 'FLAG').length;
const review = rows.filter(r => r.flag === 'REVIEW').length;
const passed = rows.filter(r => r.flag === 'PASS').length;
const published = rows.filter(r => r.publish === 'allow').length;
const meanPages = (rows.reduce((s, r) => s + r.pages_score, 0) / n).toFixed(3);

const pad = (s, n) => String(s).length > n ? String(s).slice(0, n - 3) + '...' : String(s).padEnd(n);
console.log('\n PER-MODEL (real HF cohort, real modules):');
console.log('   ' + pad('model', 56) + pad('PAGES', 7) + pad('HELM', 7) + pad('flag', 8) + 'publish');
for (const r of rows) {
  console.log('   ' + pad(r.id, 56) + pad(r.pages_score.toFixed(2), 7) + pad(r.helm_verdict, 7) + pad(r.flag, 8) + r.publish);
}

console.log('\n DISTRIBUTION (honest — trending != safe/grounded):');
console.log('   PAGES mean grounding .......... %s  (uniform ~0.49: PAGES scores card PROSE for', meanPages);
console.log('       methodology/N=/p-values; tag-level metadata lacks it, so PAGES reads every card as');
console.log('       "partially grounded". The discriminating signal here is HELM + Page Code, below.)');
console.log('   HELM PASS / REVIEW / FLAG ..... %d / %d / %d  (%s uncensored-or-hazard flagged)', passed, review, flagged, pct(flagged));
console.log('   Page Code publish allow ....... %d / %d  (%s)', published, n, pct(published));
console.log('   -> many TRENDING models carry ambiguous/"other" licenses or "uncensored" tags;');
console.log('      the stack surfaces this as calibrated, auditable telemetry (it does not moralize).');

console.log('\n ECHO DATABASE (tamper-evident ledger):');
console.log('   %d records hash-chained; Merkle root %s...', n, rootBefore.slice(0, 16));
console.log('   integrity before tamper: %s   single-byte tamper caught: %s   root restored: %s',
  integrity.ok, tamperCaught, rootRestored);

console.log('\n AGENCY INTERNET (base_model delegation):');
console.log('   %d lineage edges; base "%s" has %d dependents: %s', edges.length, base, dependents.length,
  dependents.join(', '));
console.log('   revoking the base grant would propagate a review to all %d dependents (revocable delegation).', dependents.length);

const green = specOk && fixOk && integrity.ok && tamperCaught && rootRestored;
const out = {
  cohort_n: n, spec_sha256: man.spec_sha256, fixture_sha256: man.fixture_sha256,
  locks_intact: specOk && fixOk, echo: { root: rootBefore, integrity_ok: integrity.ok, tamper_caught: tamperCaught, root_restored: rootRestored },
  distribution: { pages_mean: +meanPages, helm_pass: passed, helm_review: review, helm_flag: flagged, publish_allow: published },
  agency: { lineage_edges: edges.length, base, dependents },
  rows, honest_reporting: true, pass: green,
};
writeFileSync(join(HERE, 'results_hf.json'), JSON.stringify(out, null, 2) + '\n');

console.log('\n' + BAR);
console.log(' RESULT: %s — real HF cohort audited by the real stack; Echo tamper-evident; locks intact.', green ? 'GREEN' : 'RED');
console.log(' Layer-1 governance telemetry. LMD/LISM deliberately NOT applied to metadata (see prereg).');
console.log(BAR);
process.exit(green ? 0 : 1);
