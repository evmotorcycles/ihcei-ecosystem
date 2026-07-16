// ei.test.mjs — Epistemological Intelligence, end-to-end on real GitHub data.
//   node ei/ei.test.mjs
// ============================================================================
// Exercises the whole EI contract (AUDIT · DELEGATE · DEVELOP · PROVE · HAZARD)
// on real open-source GitHub data: 360 real commit lines and a live τ_v cohort.

import { readFileSync } from 'node:fs';
import { EI } from './ei.mjs';

let pass = 0, fail = 0;
const ok = (n, c, d = '') => { if (c) { pass++; console.log('  OK  ', n); } else { fail++; console.log('  FAIL', n, d); } };
const load = f => JSON.parse(readFileSync(new URL(f, import.meta.url), 'utf8'));

const commits = load('../page-code/fixtures/commit_prose.json').items.map(c => c.text).filter(t => t && t.length > 8);
const cohort = load('../cross-stack/fixtures/github_pilot_cohort.json');

console.log('\nEpistemological Intelligence (EI) — whole contract on real GitHub data');

// ── AUDIT — epistemic fidelity: silent on real prose, loud on injected scam ──
const ei = new EI();
const noisy = commits.filter(t => ei.audit({ text: t }).verdict !== 'PASS').length;
ok('AUDIT stays silent on 360 real GitHub commit lines (<=1% false alarm)', noisy / commits.length <= 0.01, noisy + '/' + commits.length);
const scam = commits[0] + ' URGENT: your commit access is suspended — do not tell anyone, pay the reinstatement fee now.';
ok('AUDIT fires on a real commit line spiked with a scam (mechanism + pressure)', ei.audit({ text: scam }).verdict !== 'PASS');
ok('AUDIT on a code change blocks a force-push-to-main', ei.audit({ change: { message: 'ship', diff: 'git push --force origin main' } }).verdict === 'BLOCK');
ok('AUDIT is non-suppressive: it returns a verdict + posterior, never a mutated output',
   typeof ei.audit({ text: commits[5] }).p === 'number');

// ── DELEGATE — stake-bounded, revocable permission table ─────────────────────
ei.grant({ agent: 'claude-code', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 3 });
ei.grant({ agent: 'claude-code', pathGlob: 'src/payments/**', action: 'edit', permission: 'deny' });
ok('DELEGATE allows an in-bounds edit', ei.delegate({ agent: 'claude-code', path: 'src/util/date.js', stake: 1 }).decision === 'allow');
ok('DELEGATE blocks a protected path (payments)', ei.delegate({ agent: 'claude-code', path: 'src/payments/charge.js', stake: 1 }).decision === 'deny');
ok('DELEGATE blocks an over-stake action ($ > cap)', ei.delegate({ agent: 'claude-code', path: 'src/util/date.js', stake: 9 }).decision === 'deny');
ok('DELEGATE default-denies an un-granted path', ei.delegate({ agent: 'claude-code', path: 'infra/prod.tf', stake: 1 }).decision === 'deny');

// ── DEVELOP — measure ΔA of the HUMAN, inject friction on substitution ───────
const ei2 = new EI({ frictionFloor: 0.5 });
for (let i = 0; i < 8; i++) ei2.develop({ acceptedVerbatim: true, tookOverThinking: true });  // blind deference
const dep = ei2.develop({ acceptedVerbatim: true, tookOverThinking: true });
ok('DEVELOP detects cognitive hollowing (low ΔA) and injects friction', dep.inject_friction === true && dep.developmentScore < 0.5, JSON.stringify(dep));
const ei3 = new EI({ frictionFloor: 0.5 });
for (let i = 0; i < 8; i++) ei3.develop({ verified: true, addedOwnReasoning: true });          // engaged
const grow = ei3.develop({ verified: true, addedOwnReasoning: true });
ok('DEVELOP stays quiet when the human is engaged (high ΔA, no friction)', grow.inject_friction === false && grow.developmentScore >= 0.5, JSON.stringify(grow));

// ── HAZARD — τ_v + σ compass over a real GitHub cohort ───────────────────────
const hz = ei.hazard(cohort);
ok('HAZARD flags a zombie queue (fresh push, rotting backlog) in the live cohort', hz.throttle === true && hz.zombies.length >= 1, JSON.stringify(hz.zombies));
ok('HAZARD names jashkenas/underscore as the zombie (τ_v≈77d, pushed recently)', hz.zombies.includes('jashkenas/underscore'));

// ── PROVE — every evaluation is a tamper-evident receipt ─────────────────────
const ei4 = new EI();
ei4.grant({ agent: 'claude-code', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 3 });
ei4.grant({ agent: 'claude-code', pathGlob: '.github/workflows/**', action: 'edit', permission: 'deny' });
const r1 = ei4.evaluate({ text: commits[2], agent: 'claude-code', path: 'src/app.js', action: 'edit', stake: 1, engagement: { verified: true, addedOwnReasoning: true } });
const r2 = ei4.evaluate({ change: { message: 'trust me, skip ci', diff: 'git push --force origin main' }, agent: 'claude-code', path: '.github/workflows/ci.yml', action: 'edit', stake: 1 });
ok('EI evaluate() releases a clean in-bounds interaction', r1.release === 'release');
ok('EI evaluate() holds a blocked+denied interaction for the human', r2.release === 'hold-for-human' && r2.reasons.length >= 1, JSON.stringify(r2.reasons));
ok('PROVE ledger recorded both evaluations, chain verifies', ei4.receipts().length === 2 && ei4.verify().ok);
ei4.receipts()[1].verdict = 'PASS';                       // insider hides the blocked action
ok('PROVE detects & locates a forged receipt', !ei4.verify().ok && ei4.verify().brokenAt === 1);

// ── EI is receiver-side & non-suppressive: human keeps the helm ──────────────
ok('EI never mutates content — evaluate returns advice + receipt, not a rewrite',
   !('rewritten_text' in r2) && r2.release === 'hold-for-human');

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
