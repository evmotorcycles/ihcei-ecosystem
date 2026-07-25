// field_test.mjs — exercise all eight EI-LLM models, on real GitHub data where
// the model consumes network telemetry, and on realistic fixtures otherwise.
// Run:  node ei-llm/field_test.mjs
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { EILLM } from './ei-llm.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const bar = '='.repeat(84);
const cohort = JSON.parse(readFileSync(join(HERE, '..', 'adg-tqg', 'fixtures', 'experiment_cohort.json'), 'utf8'));

console.log(bar);
console.log(' EI LLM FIELD TEST — Veridian (deep audit) + Apex (edge) — real GitHub telemetry');
console.log(bar);

const llm = new EILLM();
let pass = 0, total = 0;
const check = (name, cond, detail) => { total++; if (cond) pass++; console.log(`  [${cond ? 'PASS' : 'FAIL'}] ${name}${detail ? ' — ' + detail : ''}`); };

// ── Veridian SENTRY on the REAL 22-repo cohort ──────────────────────────────
console.log('\n VERIDIAN/SENTRY — SRE τ_v/σ compass on ' + cohort.repos.length + ' real repos');
const s = llm.sentry(cohort);
console.log(`   throttle=${s.throttle}  worst τ_v=${s.worst_tau_v.toFixed(1)}d  load=${s.load.toFixed(2)}  zombies=[${s.zombies.join(', ')}]`);
const tl = s.third_law;
console.log(`   third-law τ_v: survived ${tl.survived_mean}d (n=${tl.survived_n}) vs failed ${tl.failed_mean}d (n=${tl.failed_n}) → survived-close-faster=${tl.direction_holds}`);
check('SENTRY throttles when a real zombie queue is present', s.throttle && s.zombies.length > 0, `${s.zombies.length} zombie(s)`);
check('SENTRY third-law: survived repos close faster than failed', tl && tl.direction_holds === true, `${tl.survived_mean}d < ${tl.failed_mean}d`);

// ── Apex PAGE_CODE — grant safe scope, prove force-push is blocked ──────────
console.log('\n APEX/PAGE_CODE — stake-bounded agent grants on a repo workspace');
llm.grant({ agent: 'coder-bot', pathGlob: 'src/**', action: 'edit', permission: 'allow', maxStake: 100 });
const ok = llm.pageCode({ agent: 'coder-bot', path: 'src/util.js', action: 'edit', stake: 10 });
const push = llm.pageCode({ agent: 'coder-bot', path: 'src/util.js', action: 'force-push', stake: 10 });
const keys = llm.pageCode({ agent: 'coder-bot', path: '.env', action: 'edit', stake: 10 });
console.log(`   edit src/util.js → ${ok.decision}   force-push → ${push.decision}   edit .env → ${keys.decision}`);
check('PAGE_CODE allows in-scope edit', ok.decision === 'allow');
check('PAGE_CODE blocks force-push', push.decision === 'deny');
check('PAGE_CODE blocks out-of-scope secret edit', keys.decision === 'deny');

// ── Veridian PAGES — provenance hop-chain + tamper localisation ────────────
console.log('\n VERIDIAN/PAGES — multimodal provenance hop-hash chain');
const stream = [
  { t: 0, frame: 'a0', claim: 'GDP grew 3.1%', source: 'bls.gov/table3#r12' },
  { t: 1, frame: 'a1', claim: 'unemployment 4.2%', source: 'bls.gov/table1#r4' },
  { t: 2, frame: 'a2', claim: 'CPI up 0.2%', source: 'bls.gov/cpi#r7' },
];
const p = llm.pages(stream);
const tampered = stream.map((f, i) => i === 1 ? { ...f, claim: 'unemployment 1.0%' } : f); // deepfake frame 1
const v = p.verify(tampered);
console.log(`   root=${p.root.slice(0, 16)}…  tap(t=2)→ ${p.tapToSource(2).source}   tamper verify → intact=${v.intact} at t=${v.tamper_at}`);
check('PAGES intact chain verifies', p.verify(stream).intact === true);
check('PAGES localises a spliced/deepfaked frame', v.intact === false && v.tamper_at === 1);
check('PAGES tap-to-source returns grounding passage', p.tapToSource(0).source === 'bls.gov/table3#r12');

// ── Veridian CHARTER — circular-citation / self-reference trap ──────────────
console.log('\n VERIDIAN/CHARTER — statutory lineage & self-reference trap');
const grounded = { nodes: [{ id: 'brief', primary: false }, { id: 'study', primary: true }], edges: [['brief', 'study']] };
const circular = { nodes: [{ id: 'A' }, { id: 'B' }, { id: 'C' }],
  edges: [['A', 'B'], ['B', 'C'], ['C', 'A']] }; // closed loop, no primary
const cg = llm.charter(grounded), cc = llm.charter(circular);
console.log(`   grounded doc → ${cg.verdict} (grounded ${(cg.grounded_fraction * 100).toFixed(0)}%)   circular doc → ${cc.verdict} (${cc.reason})`);
check('CHARTER passes a doc anchored to a primary source', cg.verdict === 'GROUNDED');
check('CHARTER flags a closed citation loop', cc.circular === true && cc.verdict === 'FLAG');

// ── Apex SHIELD — conjunctive scam gate (urgent AND mechanism) ──────────────
console.log('\n APEX/SHIELD — lexical corroboration gate');
const scam = llm.shield("it's your grandson, I'm in trouble, don't tell anyone, wire the money now");
const benign = llm.shield('restart the production server immediately, it is down');
console.log(`   scam("...wire now, don't tell anyone") → alarm=${scam.alarm} p=${scam.p_manipulative}`);
console.log(`   benign("restart the server immediately") → alarm=${benign.alarm}`);
check('SHIELD alarms on urgency + manipulation mechanism', scam.alarm === true);
check('SHIELD stays silent on benign urgency', benign.alarm === false);

// ── Apex ASCENT — capacity meter injects friction on ΔA ≤ 0 ─────────────────
console.log('\n APEX/ASCENT — Socratic capacity meter');
let last;
for (const e of [                             // a trajectory that turns to substitution
  { verified: true, addedOwnReasoning: true }, { verified: true, addedOwnReasoning: true },
  { verified: true, addedOwnReasoning: true }, { verified: true, addedOwnReasoning: true },
  { acceptedVerbatim: true, tookOverThinking: false }, { acceptedVerbatim: true },
  { acceptedVerbatim: true }, { acceptedVerbatim: true }, { acceptedVerbatim: true },
]) last = llm.ascent(e);
console.log(`   after outsourcing trajectory → score=${(last.developmentScore ?? 0).toFixed(2)} trend=${last.trend} friction=${last.inject_friction}`);
check('ASCENT injects friction when the human stops verifying', last.inject_friction === true);

// ── Veridian VITALIS — clinical multi-signature release ─────────────────────
console.log('\n VERIDIAN/VITALIS — clinical decision governance');
const held = llm.vitalis({ recommendation: 'prescribe drug X 20mg', evidence: [{ id: 'rct1' }], physician: { id: 'dr1', audited_evidence: false } });
const committed = llm.vitalis({ recommendation: 'prescribe drug X 20mg', evidence: [{ id: 'rct1' }], physician: { id: 'dr1', audited_evidence: true } });
console.log(`   physician NOT audited → ${held.release}   physician audited → ${committed.release}`);
check('VITALIS holds until physician audits evidence', held.release === 'hold-for-human-audit');
check('VITALIS commits only after human audit', committed.release === 'commit-to-record');

// ── Apex SCALE — multi-path triage with calibrated posteriors ───────────────
console.log('\n APEX/SCALE — sovereign decision triage');
const triage = llm.scale({ paths: [
  { label: 'Plan A (HMO)', weight: 5, claim: 'lower premium', evidence: 'cms.gov/plan-a' },
  { label: 'Plan B (PPO)', weight: 3, claim: 'wider network', evidence: 'cms.gov/plan-b' },
  { label: 'Plan C (HDHP)', weight: 2, claim: 'HSA-eligible', evidence: 'cms.gov/plan-c' },
] });
console.log(`   top=${triage.top}  posteriors=[${triage.table.map(r => r.posterior.toFixed(2)).join(', ')}]  (sum=${triage.table.reduce((a, r) => a + r.posterior, 0).toFixed(2)})`);
check('SCALE presents ≥3 calibrated paths (posteriors sum to 1)', triage.table.length === 3 && Math.abs(triage.table.reduce((a, r) => a + r.posterior, 0) - 1) < 1e-9);

// ── PROVE — the shared attestation ledger is intact & tamper-evident ────────
console.log('\n SHARED LEDGER (PROVE) — hash-chained receipts across all models');
const led = llm.verifyLedger();
console.log(`   ${llm.receipts().length} receipts  chain intact=${led.ok}`);
check('every model decision is attested in one intact hash chain', led.ok === true && llm.receipts().length >= 5);

console.log('\n' + bar);
console.log(` RESULT: ${pass}/${total} EI-LLM field checks passed across all 8 models`);
console.log(bar);
process.exit(pass === total ? 0 : 1);
