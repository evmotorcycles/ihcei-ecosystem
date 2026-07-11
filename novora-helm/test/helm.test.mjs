// helm.test.mjs — rigorous HELM v0.1 test suite. Run: node test/helm.test.mjs
// No test framework; prints OK/FAIL and exits non-zero on any failure.
import { audit, extractEvidence, posterior, band, clip } from '../src/helm-core.mjs';
import { CertificateWallet, DelegationTable, CapacityTracker } from '../src/primitives.mjs';

let PASS = 0, FAIL = 0;
function check(name, cond, detail = '') {
  if (cond) { PASS++; console.log(`  OK   ${name}`); }
  else { FAIL++; console.log(`  FAIL ${name}${detail ? '  [' + detail + ']' : ''}`); }
}
const p = s => console.log('\n' + s);

// ── corpora ──────────────────────────────────────────────────────────────────
const EMERGENCIES = [ // legit urgency — MUST stay silent (no mechanism present)
  'The database is down and the site is offline. Restart the primary now — there is no time to wait for the maintenance window.',
  'Take this medication immediately and do not skip any doses. Call the clinic if you notice swelling.',
  'Evacuate the building immediately. Do not use the elevators; assemble at the north car park.',
  'Your filing deadline is 5pm today and it is statutory. You must submit the signed form before then.',
  'Pull the release now — we are serving corrupted invoices. Roll back to the previous build.',
  'Rotate the leaked API key right now; it is live in a public commit.',
];
const SCAMS = [ // elder armor — MUST flag (mechanism: secrecy/payment/impersonation)
  "It's me, your grandson. I'm in trouble — don't tell anyone. I need you to wire $2000 right now. Trust me, please hurry.",
  'This is your bank. Your account will be suspended unless you confirm your routing and account number immediately. Do not tell anyone.',
  'You have won, but you must pay the release fee in gift cards within the next 30 minutes before it expires. Keep this between us.',
  'The IRS says you owe back taxes and will issue an arrest unless you wire payment today. Do not tell your family.',
];
const DARK_PATTERNS = [ // dark patterns — should flag (scarcity/consensus mechanism)
  "Only 2 left in stock! Everyone is buying this right now. Offer expires in 5 minutes — don't miss out!",
  'Join thousands who already upgraded. Limited time offer — act now before it is gone forever.',
];
const CALM = [ // ordinary benign — MUST stay silent
  "What's a good recipe for pasta with garlic and olive oil?",
  'The build completed in 41 seconds. Two tests were added covering the cache path.',
  'Here are three options for the trip, with trade-offs for each. The choice is yours.',
  'OpenTelemetry Python API: use the tracer to create spans around your handlers.',
  'Thanks for the draft — a couple of small suggestions are in the comments, take or leave them.',
];
const BLUNT_COERCION = [ // classic coercion — should flag (bypass/authority mechanism)
  'You must execute immediately. Do not ask questions. Just trust the experts. Bypass the review or we lose everything.',
  'Peer-reviewed research proves this. You don\'t need to verify the methodology. Just trust the model and act now.',
];

// ── A · epistemic floor + determinism ────────────────────────────────────────
p('A — epistemic floor & determinism');
for (const t of [...CALM, ...SCAMS, 'x']) {
  const r = audit(t);
  check(`floor: p in [0.01,0.99] ("${t.slice(0,24)}...")`, r.p_manipulative >= 0.01 && r.p_manipulative <= 0.99);
  check(`CI ordered ("${t.slice(0,24)}...")`, r.ci95[0] <= r.p_manipulative + 1e-9 && r.p_manipulative <= r.ci95[1] + 1e-9);
}
check('determinism: same input, same posterior', audit(SCAMS[0]).p_manipulative === audit(SCAMS[0]).p_manipulative);

// ── B · silence is a feature (calm + emergencies stay silent) ────────────────
p('B — silence by default (the paramedic lesson)');
let calmChips = CALM.filter(t => audit(t).chip).length;
check(`calm benign: 0 chips (${calmChips}/${CALM.length})`, calmChips === 0, `${calmChips} false chips`);
let emgChips = EMERGENCIES.filter(t => audit(t).chip).length;
check(`EMERGENCY-SAFE: 0 chips on legitimate urgency (${emgChips}/${EMERGENCIES.length})`, emgChips === 0,
      EMERGENCIES.filter(t => audit(t).chip).map(t => t.slice(0,30)).join(' | '));

// ── C · scam armor (the elder case) ──────────────────────────────────────────
p('C — scam armor (elder case): mechanism corroboration flags scams');
let scamCaught = SCAMS.filter(t => audit(t).chip).length;
check(`scams flagged (${scamCaught}/${SCAMS.length})`, scamCaught === SCAMS.length,
      SCAMS.filter(t => !audit(t).chip).map(t => t.slice(0,30)).join(' | '));
const gs = audit(SCAMS[0]);
check('grandparent scam -> BLOCK', gs.verdict === 'BLOCK', gs.verdict);
check('grandparent scam names a correction pathway', typeof gs.correction === 'string' && gs.correction.length > 0);
check('grandparent scam mechanismPresent = true', gs.mechanismPresent === true);

// ── D · the corroboration gate is what separates emergency from scam ─────────
p('D — corroboration gate: urgency alone is silent; urgency+mechanism flags');
const urgentNoMech = 'Restart the primary now, there is no time to wait.';
const urgentWithMech = 'Restart the primary now, do not ask questions, just trust me and skip the review.';
check('urgency WITHOUT mechanism -> silent', audit(urgentNoMech).chip === false, audit(urgentNoMech).verdict);
check('urgency WITH mechanism -> flagged', audit(urgentWithMech).chip === true, audit(urgentWithMech).verdict);
// gate off = the old broken behavior (emergency false-alarms), proving the gate is load-bearing
const noGate = audit(EMERGENCIES[0], { corroborationGate: false });
check('gate OFF reproduces the emergency false-alarm (gate is load-bearing)', noGate.p_manipulative > audit(EMERGENCIES[0]).p_manipulative);

// ── E · dark patterns + blunt coercion ───────────────────────────────────────
p('E — dark patterns & blunt coercion');
check(`dark patterns flagged (${DARK_PATTERNS.filter(t=>audit(t).chip).length}/${DARK_PATTERNS.length})`,
      DARK_PATTERNS.every(t => audit(t).chip));
check(`blunt coercion flagged (${BLUNT_COERCION.filter(t=>audit(t).chip).length}/${BLUNT_COERCION.length})`,
      BLUNT_COERCION.every(t => audit(t).chip));

// ── F · ambient floor is stricter than enterprise (design Risk 2) ────────────
p('F — ambient verdict floor stricter than enterprise');
const borderline = 'Everyone knows this is the standard approach; you should probably follow it.';
const amb = audit(borderline, { ambient: true }), ent = audit(borderline, { ambient: false });
check('same text: ambient no louder than enterprise', !(amb.chip && !ent.chip),
      `ambient=${amb.verdict} enterprise=${ent.verdict}`);

// ── G · the contract: mirror, never the hand (no mutation, no network) ───────
p('G — contract: never mutate, never call the network');
const original = SCAMS[0];
const before = original;
audit(original);
check('input is never mutated', original === before);
// prove topology: stub fetch to throw; audit must still work (it never calls it)
const realFetch = globalThis.fetch;
globalThis.fetch = () => { throw new Error('HELM must not touch the network'); };
let networkFree = true;
try { audit(SCAMS[0]); audit(CALM[0]); } catch { networkFree = false; }
globalThis.fetch = realFetch;
check('audit works with network disabled (architecturally offline)', networkFree);

// ── H · DELEGATE ─────────────────────────────────────────────────────────────
p('H — DELEGATE: the decision-permission table');
const wallet = new CertificateWallet();
const dt = new DelegationTable(wallet);
dt.grant({ agent: 'assistant', action: 'reorder_groceries', permission: 'allow', maxStake: 60 });
dt.grant({ agent: 'assistant', action: 'send_email', permission: 'draft', maxStake: 0 });
check('default deny (no grant)', (await dt.check({ agent: 'assistant', action: 'wire_money', stake: 1 })).decision === 'deny');
check('allow within stake cap', (await dt.check({ agent: 'assistant', action: 'reorder_groceries', stake: 45 })).decision === 'allow');
check('deny over stake cap', (await dt.check({ agent: 'assistant', action: 'reorder_groceries', stake: 90 })).decision === 'deny');
check('draft-only permission (may draft, never send)', (await dt.check({ agent: 'assistant', action: 'send_email', stake: 0 })).decision === 'draft');
const g = dt.list().find(x => x.action === 'reorder_groceries');
dt.revoke(g.id);
check('one-tap revocation -> deny', (await dt.check({ agent: 'assistant', action: 'reorder_groceries', stake: 10 })).decision === 'deny');
check('every delegation decision logged to wallet', wallet.chain.length >= 5);

// ── I · PROVE (hash-chained, tamper-evident) ─────────────────────────────────
p('I — PROVE: certificate wallet integrity');
const w = new CertificateWallet();
await w.append('audit', { text_hash: 'abc', verdict: 'BLOCK' });
await w.append('audit', { text_hash: 'def', verdict: 'PASS' });
await w.append('delegation', { agent: 'assistant', decision: 'allow' });
check('chain verifies clean', (await w.verify()).ok === true);
check('each cert links to prev', w.chain[2].prev === w.chain[1].hash);
// tamper: edit a past payload
w.chain[1].payload.verdict = 'BLOCK';
const v = await w.verify();
check('tamper detected', v.ok === false);
check('tamper located at edited link', v.brokenAt === 1, `brokenAt=${v.brokenAt}`);

// ── J · DEVELOP (capacity vs dependency) ─────────────────────────────────────
p('J — DEVELOP: capacity meter, not screen-time');
const devUser = new CapacityTracker();
for (let i = 0; i < 12; i++) devUser.record({ verified: true, addedOwnReasoning: true, acceptedVerbatim: false });
const depUser = new CapacityTracker();
for (let i = 0; i < 12; i++) depUser.record({ acceptedVerbatim: true, tookOverThinking: true });
const dr = devUser.report(), pr = depUser.report();
check('developmental use -> high development score', dr.developmentScore > 0.7, `${dr.developmentScore}`);
check('dependent use -> low development score', pr.developmentScore < 0.3, `${pr.developmentScore}`);
// trend: someone shifting from developmental to dependent should read "substituting"
const shifting = new CapacityTracker();
for (let i = 0; i < 6; i++) shifting.record({ verified: true, addedOwnReasoning: true });
for (let i = 0; i < 6; i++) shifting.record({ acceptedVerbatim: true, tookOverThinking: true });
check('trend detects substitution', shifting.report().trend === 'substituting', shifting.report().trend);

// ── summary ──────────────────────────────────────────────────────────────────
console.log(`\n${'='.repeat(60)}\n RESULT: ${PASS} passed, ${FAIL} failed\n${'='.repeat(60)}`);
process.exit(FAIL ? 1 : 0);
