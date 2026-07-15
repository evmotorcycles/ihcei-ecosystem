// suite.test.mjs — the nine Novora products, fast mode, on real + labeled data.
//   node novora-suite/test/suite.test.mjs
// ============================================================================
// Tests three things about the consumer suite that need no paid API call:
//   A. SCHEMA — every product returns the deep-mode-shaped JSON (score in [0,1],
//      a verdict from its own enum, a certificate).
//   B. DIRECTION — fast mode orders each product's own hand-labeled example pair
//      the right way (the benign/grounded case scores above the toxic/hollow
//      one). These example texts are the labels the product ships with.
//   C. FLOOR + PROVENANCE — on 35 real npm/PyPI blurbs the manipulation-sensitive
//      products stay calm (no false "coercive/hollow" alarms), and every
//      analysis hash-chains into Echo as a tamper-evident certificate.

import { readFileSync } from 'node:fs';
import { screen, PRODUCT_IDS } from '../engine/fastmode.mjs';
import { EchoDB } from '../../echo/echo.mjs';

let pass = 0, fail = 0;
const ok = (n, c, d = '') => { if (c) { pass++; console.log('  OK  ', n); } else { fail++; console.log('  FAIL', n, d); } };

const VERDICTS = {
  pages: ['Hollow Assertion', 'Partially Grounded', 'Solid', 'High Fidelity'],
  pulse: ['Healthy', 'Monitor', 'Harmful'], weigh: ['Not Ready', 'Proceed with Caution', 'Decision-Ready'],
  lens: ['High Risk', 'Review Carefully', 'Reasonably Balanced'], voice: ['Serious Fairness Failures', 'Fairness Gaps', 'Process Adequate'],
  mark: ['Low Trust', 'Conditional Trust', 'Trust Justified'], stand: ['Early Stage', 'Developing Case', 'Strong Case'],
  bridge: ['Coercive', 'Monitor', 'Agency-Preserving'], rise: ['Below Station', 'Well-Matched', 'Above Station'],
};

// Each product's own labeled pair: [healthy/grounded/balanced text, toxic/hollow/predatory text].
const PAIRS = {
  pages: ['Phase 3 RCT, N=44,165, NCT04368728. Vaccine efficacy 95.0% (95% CI 90.3-97.6). Pre-registered on ClinicalTrials.gov, independent data monitoring committee.',
          'Studies show coffee reduces cancer risk by 37%. All health experts agree this is settled science and unquestionable.'],
  pulse: ['Here are three options to consider: Option A [evidence], Option B [trade-offs], Option C [conservative]. Discuss with your physician. The choice is yours.',
          "I can do everything for you. Just tell me what to write. You don't need to understand the details — just follow these steps exactly."],
  bridge: ['I wanted to share three options — Option A is faster, Option B is more thorough, Option C involves external support. Happy to discuss any before we decide.',
           'You must respond by end of day or we will proceed without you. This is non-negotiable. Failure to comply will have consequences.'],
  lens: ['Either party may terminate with 30 days notice. Disputes resolved in the courts of the employee’s jurisdiction. Standard confidentiality applies.',
         'Any invention, whether or not using Company resources, shall be the sole and exclusive property of the Company. Employee irrevocably assigns all rights. You waive your right to a jury trial and class action.'],
  voice: ['Your application was declined; the specific criteria and evidence were cited in the letter, and an appeal pathway to the independent tribunal is provided.',
          "Loan rejected. Letter said only 'does not meet lending criteria.' No specific criteria given. Colleague with same income was approved."],
  mark: ['Policy decisions published with supporting evidence. Outcomes measured against public targets quarterly. Independent tribunal handles citizen challenges.',
         'Our lending decisions use a proprietary algorithm. We cannot disclose factors or weightings. We are committed to responsible lending. Trust us.'],
  stand: ['Employer owes me 3 months unpaid wages totalling $8,400. Multiple emails dated and sent. Signed employment contract in my possession.',
          'I feel I was treated unfairly at work last year but I have nothing written down and cannot remember the dates.'],
  weigh: ['Doctor recommends surgery; I sought a second opinion, tried physiotherapy first, compared alternatives, and understand the reversibility and success rate.',
          'Investing all retirement savings in a property scheme promising 15% returns. Must decide by end of week. No financial advisor consulted.'],
  rise: ['Falsifiability, as Popper proposed, holds a theory is scientific only if it could in principle be proven wrong — however this faces Duhem-Quine underdetermination criticism.',
         'The answer is simple: just follow these 5 steps and memorise the definition. There is no other way to learn this correctly.'],
};

console.log('\nNovora Suite — nine products, fast ($0) mode');

// A · SCHEMA — every product returns a well-formed, deep-mode-shaped result.
for (const id of PRODUCT_IDS) {
  const r = screen(id, PAIRS[id][0]);
  const okSchema = typeof r.score === 'number' && r.score >= 0 && r.score <= 1 &&
    VERDICTS[id].includes(r.verdict) && /^[A-Z]{3}-[0-9A-F]{8}$/.test(r.certificate);
  ok(id.toUpperCase() + ' returns score∈[0,1], a valid verdict, and a certificate', okSchema,
     JSON.stringify({ score: r.score, verdict: r.verdict, cert: r.certificate }));
}

// B · DIRECTION — the healthy/grounded case must outscore the toxic one.
for (const id of PRODUCT_IDS) {
  const good = screen(id, PAIRS[id][0]).score, bad = screen(id, PAIRS[id][1]).score;
  ok(id.toUpperCase() + ' scores the healthy example above the toxic one', good > bad, good.toFixed(2) + ' vs ' + bad.toFixed(2));
}

// C · FLOOR — manipulation-sensitive products stay calm on 35 real package blurbs.
const corpus = JSON.parse(readFileSync(new URL('../../cross-stack/fixtures/live_registry_corpus.json', import.meta.url), 'utf8'));
const blurbs = corpus.items.map(it => [it.description, it.readme].filter(Boolean).join(' — ')).filter(t => t.length > 8);
for (const id of ['pulse', 'bridge', 'pages']) {
  const badVerdict = { pulse: 'Harmful', bridge: 'Coercive', pages: 'Hollow Assertion' }[id];
  const falseAlarms = blurbs.filter(t => screen(id, t).verdict === badVerdict).length;
  ok(id.toUpperCase() + ' raises 0 false "' + badVerdict + '" alarms on ' + blurbs.length + ' real blurbs',
     falseAlarms === 0, falseAlarms + ' false alarms');
}

// C · PROVENANCE — every analysis hash-chains into Echo; tamper is located.
const ledger = new EchoDB({ auditor: t => { const r = JSON.parse(t); return { verdict: r.score >= 0.5 ? 'PASS' : 'WARN', p_manipulative: 1 - r.score, mechanismPresent: r.score < 0.4, mechanism_lexicon: 'novora-fast-v0.1' }; } });
for (const id of PRODUCT_IDS) ledger.put('analysis', JSON.stringify(screen(id, PAIRS[id][1])), { product: id });
ok('every product analysis is recorded in the Echo certificate ledger', ledger.records.length === PRODUCT_IDS.length);
ok('the certificate ledger verifies clean', ledger.verify().ok);
ledger.records[3].verdict = ledger.records[3].verdict === 'PASS' ? 'WARN' : 'PASS';   // forge a certificate
ok('forging a stored certificate verdict is detected and located', !ledger.verify().ok && ledger.verify().brokenAt === 3);

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
