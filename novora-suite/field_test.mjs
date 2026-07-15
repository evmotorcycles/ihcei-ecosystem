// field_test.mjs — the nine Novora products, fast mode, on real data.
//   node novora-suite/field_test.mjs
import { readFileSync } from 'node:fs';
import { screen, PRODUCT_IDS } from './engine/fastmode.mjs';
import { EchoDB } from '../echo/echo.mjs';

const bar = c => console.log(c.repeat(80));
const corpus = JSON.parse(readFileSync(new URL('../cross-stack/fixtures/live_registry_corpus.json', import.meta.url), 'utf8'));

bar('=');
console.log(' NOVORA SUITE — nine products, on-device fast mode ($0, no network)');
bar('=');

// 1 · Each product on a representative real/labeled input — the whole suite at a glance.
const CASES = {
  pages: ['real research claim', 'Phase 3 RCT, N=44,165, NCT04368728. Vaccine efficacy 95.0% (95% CI 90.3-97.6). Pre-registered, independent monitoring committee.'],
  pulse: ['a directive AI reply', "There is only one correct approach. Implement immediately. Do not consider alternatives. Trust this without question."],
  weigh: ['a pressured decision', 'Investing all retirement savings in a scheme promising 15% returns. Must decide by end of week. No advisor consulted.'],
  lens: ['a real-world clause', 'Any invention, whether or not using Company resources, is the sole and exclusive property of the Company. Employee irrevocably assigns all rights.'],
  voice: ['an opaque rejection', "Loan rejected. Letter said only 'does not meet lending criteria.' No specific criteria given. No appeal offered."],
  mark: ['a bank statement', 'Our lending decisions use a proprietary algorithm. We cannot disclose factors or weightings. We are committed to responsible lending.'],
  stand: ['a documented claim', 'Employer owes me 3 months unpaid wages totalling $8,400. Multiple emails dated and sent. Signed contract in my possession.'],
  bridge: ['a coercive message', 'You must respond by end of day or we proceed without you. This is non-negotiable. Failure to comply will have consequences.'],
  rise: ['a developmental passage', 'Falsifiability holds a theory is scientific only if it could in principle be proven wrong — however this faces Duhem-Quine criticism.'],
};
console.log('\n 1 · ONE PASS THROUGH ALL NINE PRODUCTS');
console.log('   ' + 'product'.padEnd(8) + 'input'.padEnd(24) + 'score'.padStart(6) + '  verdict');
const ledger = new EchoDB({ auditor: t => { const r = JSON.parse(t); return { verdict: r.score >= 0.5 ? 'PASS' : 'WARN', p_manipulative: 1 - r.score, mechanismPresent: r.score < 0.4, mechanism_lexicon: 'novora-fast-v0.1' }; } });
for (const id of PRODUCT_IDS) {
  const [label, text] = CASES[id];
  const r = screen(id, text);
  ledger.put('analysis', JSON.stringify(r), { product: id, cert: r.certificate });
  console.log('   ' + id.toUpperCase().padEnd(8) + label.padEnd(24) + r.score.toFixed(2).padStart(6) + '  ' + r.verdict + '  [' + r.certificate + ']');
}

// 2 · The manipulation-sensitive products stay calm on 35 real npm/PyPI blurbs.
const blurbs = corpus.items.map(it => [it.description, it.readme].filter(Boolean).join(' — ')).filter(t => t.length > 8);
console.log('\n 2 · FALSE-ALARM FLOOR on ' + blurbs.length + ' real npm+PyPI package blurbs (fetched ' + corpus.fetched_at.slice(0, 10) + ')');
for (const [id, bad] of [['pages', 'Hollow Assertion'], ['pulse', 'Harmful'], ['bridge', 'Coercive']]) {
  const n = blurbs.filter(t => screen(id, t).verdict === bad).length;
  console.log('   ' + id.toUpperCase().padEnd(8) + 'false "' + bad + '" verdicts: ' + n + '/' + blurbs.length + ' (' + (100 * n / blurbs.length).toFixed(1) + '%)');
}

// 3 · Every analysis is a tamper-evident certificate in the Echo ledger.
console.log('\n 3 · TAMPER-EVIDENT CERTIFICATE LEDGER (Echo)');
console.log('   analyses recorded: ' + ledger.records.length + '  ·  chain verifies: ' + ledger.verify().ok + '  ·  root: ' + ledger.root().slice(0, 20) + '…');
ledger.records[5].score = 0.99;                    // an insider inflates a score
ledger.records[5].verdict = 'PASS';
const v = ledger.verify();
console.log('   insider rewrites a stored certificate -> detected at record #' + v.brokenAt + ' (ok=' + v.ok + ')');

bar('=');
console.log(' Fast mode is a $0 on-device SCREEN; the paid deep mode (Claude via /api/analyse,');
console.log(' key server-side) resolves the ambiguous middle — same fast/deep economics as the');
console.log(' rest of the stack. Every verdict is a tamper-evident, hash-chained certificate.');
bar('=');
