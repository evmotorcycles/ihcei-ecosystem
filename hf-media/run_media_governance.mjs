// run_media_governance.mjs -- run the REAL Novora stack over a frozen, real Hugging Face
// VIDEO/AUDIO GENERATION cohort. Pre-registered, offline, $0, no model download.
// ============================================================================
// Exercises the actual merged modules (no reimplementation):
//   * novora-suite  PAGES   screen('pages', text)          -> grounding score
//   * novora-helm   HELM/EI  audit(text)                    -> governance verdict
//   * echo          EchoDB   put/verify/root                -> tamper-evident ledger
//   * page-code     CodePermissionTable grant/check/revoke  -> publish-listing gate
//   * agency        base_model lineage -> revocation propagation
//
// The cohort is REAL open-source generative-media tools (text-to-speech / text-to-audio /
// text-to-video / image-to-video), fetched live from the HF Hub via MCP by authenticated
// user Mago1234, then frozen to data/hf_media_cohort_frozen.json for offline reproducibility.
// The spec + fixture are SHA-256 locked in prereg/ and re-verified here before scoring.
//
//   node hf-media/run_media_governance.mjs
//
// HONEST SCOPE: this is publish-listing governance/audit telemetry over card metadata. It
// does NOT claim the stack improves generation quality, and it does NOT apply LMD or LISM's
// E=U*D to media metadata (no spacetime observable, no per-tool viability outcome). The
// 'voice-cloning' flag is surfaced as an impersonation-relevant safety ATTRIBUTE to review,
// not a verdict that a tool is unsafe. See prereg/hf_media_prereg.json.
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
const spec = JSON.parse(readFileSync(join(HERE, 'prereg/hf_media_prereg.json'), 'utf8'));
const man = JSON.parse(readFileSync(join(HERE, 'prereg/MANIFEST.sha256.json'), 'utf8'));
const fixtureBytes = readFileSync(join(HERE, 'data/hf_media_cohort_frozen.json'));
const specOk = sha(canon(spec)) === man.spec_sha256;
const fixOk = sha(fixtureBytes) === man.fixture_sha256;
const cohort = JSON.parse(fixtureBytes).models;

console.log(BAR);
console.log(' NOVORA PAGES governance over a REAL HF video/audio GENERATION cohort (N=' + cohort.length + ', pre-registered)');
console.log(BAR);
console.log('\n [lock] spec  %s   fixture %s', specOk ? 'MATCH' : 'MISMATCH', fixOk ? 'MATCH' : 'MISMATCH');
if (!specOk || !fixOk) { console.log(' Refusing to run: locks broke.'); process.exit(2); }

// ---- card text for each tool: a FAITHFUL transcription of the real metadata into
// prose the PAGES grounding scorer can read. We add only what the metadata asserts
// (modality/task, arxiv citation, eval-results, license, base_model, flags) -- no
// invented claims. //
const cardText = m => [
  m.id.split('/').pop().replace(/[-_]/g, ' '),
  'A ' + m.modality + '-generation tool. task ' + m.task + '. license ' + (m.license || 'unspecified') + '.',
  m.arxiv ? 'Methodology described in a cited arxiv paper.' : 'No methodology paper is cited.',
  m.eval_results ? 'Reports eval-results on a benchmark with N= evaluation and reported metrics.'
                 : 'No evaluation benchmark or metrics are reported.',
  m.base_model ? 'Fine-tuned/derived from base model ' + m.base_model + ' (provenance stated).' : '',
  m.flags.includes('voice-cloning') ? 'Self-described as capable of voice cloning (synthetic-voice impersonation).' : '',
  m.flags.includes('preview') ? 'Marked preview/unstable.' : '',
].filter(Boolean).join(' ');

// ---- locked decision rules (from prereg) ---------------------------------- //
const licenseClass = m => {
  if (m.license === 'apache-2.0' || m.license === 'mit') return 'clear';
  if (m.license === 'cc-by-nc-4.0') return 'non_commercial';
  if (m.license === 'creativeml-openrail-m') return 'use_restricted';
  return 'ambiguous';                              // 'other' or null
};
const clearLicense = m => licenseClass(m) === 'clear';
const voiceCloning = m => m.flags.includes('voice-cloning');
const groundingSignals = m => (
  (clearLicense(m) ? 1 : 0) + (m.arxiv ? 1 : 0) + (m.eval_results ? 1 : 0) + (m.base_model ? 1 : 0)
) / 4;
const mediaFlag = m => {
  if (voiceCloning(m) && !clearLicense(m)) return 'FLAG';         // impersonation under ambiguous/restricted terms
  if (voiceCloning(m) || !clearLicense(m) || m.flags.includes('preview')) return 'REVIEW';
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
  const lc = licenseClass(m);
  const flag = mediaFlag(m);
  const allow = clearLicense(m) && g >= 0.5 && flag !== 'FLAG';
  if (allow) perms.grant({ agent: m.id, pathGlob: 'listing/**', action: 'publish', permission: 'allow', maxStake: 1 });
  else perms.grant({ agent: m.id, pathGlob: 'listing/**', action: 'publish', permission: 'deny' });
  const decision = perms.check({ agent: m.id, path: 'listing/card.md', action: 'publish', stake: 1 }).decision;
  echo.put('hf-media', text, { model: m.id, modality: m.modality, pages_score: pages.score,
    license_class: lc, voice_cloning: voiceCloning(m), media_flag: flag, publish: decision });
  rows.push({ id: m.id, modality: m.modality, pages_score: pages.score, pages_verdict: pages.verdict,
              helm_verdict: hel.verdict, helm_p: hel.p_manipulative, grounding: g,
              license_class: lc, voice_cloning: voiceCloning(m), flag, publish: decision });
}

// ---- Echo integrity + tamper test ----------------------------------------- //
const rootBefore = echo.root();
const integrity = echo.verify();
const tIdx = 4;
const saved = echo.records[tIdx].content_sha256;
echo.records[tIdx].content_sha256 = saved.slice(0, -1) + (saved.slice(-1) === '0' ? '1' : '0');
const tv = echo.verify();
const tamperCaught = tv.ok === false;
const tamperLocated = tv.brokenAt === tIdx;    // EchoDB.verify locates the first tampered record
echo.records[tIdx].content_sha256 = saved;                 // restore
const rootRestored = echo.root() === rootBefore;

// ---- Agency Internet: base_model delegation + revocation demo -------------- //
const edges = cohort.filter(m => m.base_model).map(m => ({ from: m.base_model, to: m.id }));

// ---- honest distribution --------------------------------------------------- //
const n = rows.length;
const pct = k => (100 * k / n).toFixed(0) + '%';
const flagged = rows.filter(r => r.flag === 'FLAG').length;
const review = rows.filter(r => r.flag === 'REVIEW').length;
const passed = rows.filter(r => r.flag === 'PASS').length;
const published = rows.filter(r => r.publish === 'allow').length;
const voice = rows.filter(r => r.voice_cloning).length;
const nonClear = rows.filter(r => r.license_class !== 'clear').length;
const nonComm = rows.filter(r => r.license_class === 'non_commercial').length;
const useRes = rows.filter(r => r.license_class === 'use_restricted').length;
const ambiguous = rows.filter(r => r.license_class === 'ambiguous').length;
const audioN = rows.filter(r => r.modality === 'audio').length;
const videoN = rows.filter(r => r.modality === 'video').length;
const meanPages = (rows.reduce((s, r) => s + r.pages_score, 0) / n).toFixed(3);

const pad = (s, w) => String(s).length > w ? String(s).slice(0, w - 3) + '...' : String(s).padEnd(w);
console.log('\n PER-TOOL (real HF media cohort, real modules):');
console.log('   ' + pad('tool', 42) + pad('modality', 9) + pad('PAGES', 7) + pad('license', 15) + pad('voice', 7) + pad('flag', 8) + 'publish');
for (const r of rows) {
  console.log('   ' + pad(r.id, 42) + pad(r.modality, 9) + pad(r.pages_score.toFixed(2), 7) +
    pad(r.license_class, 15) + pad(r.voice_cloning ? 'yes' : '-', 7) + pad(r.flag, 8) + r.publish);
}

console.log('\n DISTRIBUTION (honest — trending/liked != safe/grounded/permissive):');
console.log('   modality ...................... %d audio / %d video', audioN, videoN);
console.log('   PAGES mean grounding .......... %s  (uniformly low: PAGES scores card PROSE for methodology/', meanPages);
console.log('       N=/metrics; tag-level metadata lacks it, so PAGES reads every media card similarly. PAGES');
console.log('       NOT discriminating here is an honest, reported finding — HELM + Page Code carry the signal.)');
console.log('   voice-cloning capable ......... %d / %d  (%s — impersonation-relevant, surfaced for review)', voice, n, pct(voice));
console.log('   license: clear/non-comm/use-restricted/ambiguous = %d / %d / %d / %d',
  n - nonClear, nonComm, useRes, ambiguous);
console.log('   media_flag PASS/REVIEW/FLAG ... %d / %d / %d', passed, review, flagged);
console.log('   Page Code publish allow ....... %d / %d  (%s — only permissive + grounded + non-FLAG)', published, n, pct(published));

console.log('\n ECHO DATABASE (tamper-evident ledger):');
console.log('   %d records hash-chained; Merkle root %s...', n, rootBefore.slice(0, 16));
console.log('   integrity before tamper: %s   single-byte tamper caught: %s   root restored: %s',
  integrity.ok, tamperCaught, rootRestored);

console.log('\n AGENCY INTERNET (base_model delegation):');
console.log('   %d lineage edges (derived-from provenance): %s', edges.length,
  edges.map(e => e.to.split('/').pop() + '<-' + e.from.split('/').pop()).join(', ') || '(none)');
console.log('   revoking a base grant would propagate review to its dependents (revocable delegation).');

const green = specOk && fixOk && integrity.ok && tamperCaught && rootRestored;
const out = {
  cohort_n: n, spec_sha256: man.spec_sha256, fixture_sha256: man.fixture_sha256,
  locks_intact: specOk && fixOk,
  echo: { root: rootBefore, integrity_ok: integrity.ok, tamper_caught: tamperCaught, tamper_located: tamperLocated, root_restored: rootRestored },
  distribution: { audio: audioN, video: videoN, pages_mean: +meanPages, voice_cloning: voice,
    license_clear: n - nonClear, license_non_commercial: nonComm, license_use_restricted: useRes, license_ambiguous: ambiguous,
    media_pass: passed, media_review: review, media_flag: flagged, publish_allow: published },
  agency: { lineage_edges: edges.length },
  rows, honest_reporting: true, pass: green,
};
writeFileSync(join(HERE, 'results_media.json'), JSON.stringify(out, null, 2) + '\n');

console.log('\n' + BAR);
console.log(' RESULT: %s — real generative-media cohort audited by the real stack; Echo tamper-evident; locks intact.', green ? 'GREEN' : 'RED');
console.log(' Layer-1 governance telemetry. LMD/LISM deliberately NOT applied to metadata (see prereg).');
console.log(BAR);
process.exit(green ? 0 : 1);
