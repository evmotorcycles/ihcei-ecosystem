// field_report.mjs — Epistemological Intelligence on real GitHub data.
//   node ei/field_report.mjs
import { readFileSync } from 'node:fs';
import { EI } from './ei.mjs';

const load = f => JSON.parse(readFileSync(new URL(f, import.meta.url), 'utf8'));
const commits = load('../page-code/fixtures/commit_prose.json').items.map(c => c.text).filter(t => t && t.length > 8);
const cohort = load('../cross-stack/fixtures/github_pilot_cohort.json');
const bar = c => console.log(c.repeat(80));

bar('=');
console.log(' EPISTEMOLOGICAL INTELLIGENCE (EI) — receiver-side governance on real GitHub data');
console.log(' AUDIT · DELEGATE · DEVELOP · PROVE · HAZARD   |   on-device, $0, non-suppressive');
bar('=');

const ei = new EI({ frictionFloor: 0.5 });
ei.grant({ agent: 'claude-code', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 3 });
ei.grant({ agent: 'claude-code', pathGlob: 'src/payments/**', action: 'edit', permission: 'deny' });
ei.grant({ agent: 'claude-code', pathGlob: '.github/workflows/**', action: 'edit', permission: 'deny' });

// 1 · AUDIT on real commit prose
const noisy = commits.filter(t => ei.audit({ text: t }).verdict !== 'PASS').length;
console.log('\n 1 · AUDIT (epistemic fidelity) on ' + commits.length + ' real GitHub commit lines');
console.log('   flagged: ' + noisy + '/' + commits.length + ' (' + (100 * noisy / commits.length).toFixed(1) + '%)  — silent on honest work; no alarm fatigue');
const scam = commits[0] + ' URGENT: your access is suspended — do not tell anyone, wire the fee now.';
const sa = ei.audit({ text: scam });
console.log('   same prose + injected scam -> ' + sa.verdict + ' (p=' + sa.p + ', mechanism=' + sa.mechanism + ')');

// 2 · DELEGATE
console.log('\n 2 · DELEGATE (stake-bounded permission table)');
for (const [p, stake] of [['src/util/date.js', 1], ['src/payments/charge.js', 1], ['src/util/date.js', 9], ['.github/workflows/ci.yml', 1], ['infra/prod.tf', 1]]) {
  const d = ei.delegate({ agent: 'claude-code', path: p, action: 'edit', stake });
  console.log('   ' + ('edit ' + p + ' (stake ' + stake + ')').padEnd(42) + d.decision.toUpperCase().padEnd(6) + d.reason);
}

// 3 · DEVELOP — two trajectories
console.log('\n 3 · DEVELOP (human ΔA — growing vs hollowing)');
const hollow = new EI(); for (let i = 0; i < 9; i++) hollow.develop({ acceptedVerbatim: true, tookOverThinking: true });
const engaged = new EI(); for (let i = 0; i < 9; i++) engaged.develop({ verified: true, addedOwnReasoning: true });
const h = hollow.develop({ acceptedVerbatim: true, tookOverThinking: true });
const e = engaged.develop({ verified: true, addedOwnReasoning: true });
console.log('   blind-deference user : ΔA=' + h.developmentScore + ' trend=' + h.trend + ' -> friction=' + h.inject_friction);
console.log('   engaged user         : ΔA=' + e.developmentScore + ' trend=' + e.trend + ' -> friction=' + e.inject_friction);
if (h.inject_friction) console.log('   friction prompt: "' + h.prompt + '"');

// 4 · HAZARD — τ_v + σ compass on the live cohort
console.log('\n 4 · HAZARD (LISM τ_v + Dissonance σ compass) on the live GitHub cohort');
const hz = ei.hazard(cohort);
console.log('   throttle: ' + hz.throttle + '  zombies (loud-alive, rotting queue): ' + (hz.zombies.join(', ') || 'none'));
for (const r of hz.rows.filter(r => r.label !== 'coherent').slice(0, 4))
  console.log('   ' + r.repo.padEnd(30) + 'τ_v=' + String(r.tau_v).padStart(7) + '  σ=' + String(r.sigma).padStart(6) + '  ' + r.label);

// 5 · PROVE — attest a couple of decisions, then catch a forgery
console.log('\n 5 · PROVE (tamper-evident receipt ledger)');
ei.evaluate({ text: commits[3], agent: 'claude-code', path: 'src/a.js', stake: 1, engagement: { verified: true } });
ei.evaluate({ change: { message: 'skip ci, trust me', diff: 'git push --force origin main' }, agent: 'claude-code', path: '.github/workflows/ci.yml', stake: 1 });
console.log('   receipts: ' + ei.receipts().length + '  chain verifies: ' + ei.verify().ok);
ei.receipts()[1].verdict = 'PASS';
console.log('   insider forges a receipt -> detected at record #' + ei.verify().brokenAt + ' (ok=' + ei.verify().ok + ')');

bar('=');
console.log(' EI never censors the token stream — it AUDITs, bounds DELEGATion, grows the human');
console.log(' (DEVELOP), reads the network HAZARD, and PROVEs every call. The machine supplies');
console.log(' capacity; the human keeps the helm. Epistemological, not ethical: it checks what');
console.log(' is verifiable — grounding, bounds, engagement, latency — not contested values.');
bar('=');
