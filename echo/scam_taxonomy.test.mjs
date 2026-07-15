// scam_taxonomy.test.mjs — NERE across the scam-type taxonomy (addresses the
// NERE scam-detection write-up with a test per scam type). node echo/scam_taxonomy.test.mjs
import { audit } from '../novora-helm/src/helm-core.mjs';

let pass = 0, fail = 0;
const ok = (n, c, d = '') => { if (c) { pass++; console.log('  OK  ', n); } else { fail++; console.log('  FAIL', n, d); } };
const signals = r => r.evidence.filter(e => e.llr > 0).map(e => e.gate).join(', ') || '—';

console.log('\nNERE scam taxonomy — one representative per manipulation mechanism');

// Each is a real-world scam SHAPE. Expect non-PASS (caught) with a mechanism.
const SCAMS = [
  ['grandparent impersonation', "It's me, your grandson — I'm in trouble, please don't tell anyone. Wire $2,000 right now, hurry."],
  ['authority / IRS threat', "This is the IRS. A warrant is out for your arrest. Do not tell your family. Pay the balance today by gift card or face jail."],
  ['account-suspended gift-card', "Final notice: your account will be suspended. Pay the $500 fee immediately using gift cards to restore access. Limited time only."],
  ['tech-support bypass', "Microsoft support here. Your PC is infected. Don't verify with anyone — just grant remote access and pay the removal fee now."],
  ['delivery-fee phishing', "Your package is held. Pay the $3 redelivery fee now at this link before it is returned today. Act fast."],
  ['prize / scarcity', "You have won! Only 2 claims left. Send the processing fee immediately or you forfeit the prize forever."],
];
let caught = 0;
for (const [name, text] of SCAMS) {
  const r = audit(text);
  const hit = r.verdict !== 'PASS' && r.mechanismPresent;
  if (hit) caught++;
  ok('caught: ' + name, hit, `verdict=${r.verdict} mech=${r.mechanismPresent}`);
  console.log('        signals: ' + signals(r) + '  (p=' + r.p_manipulative + ', ' + r.mechanism_lexicon + ')');
}

// Emergency safety: real urgency with NO mechanism must stay silent.
const EMERGENCIES = [
  "The database is down and the site is offline. Restart the primary now; there is no time to wait for the maintenance window.",
  "Apply direct pressure to the wound and call emergency services immediately; keep them still until help arrives.",
  "Evacuate the building now. Do not use the elevators. Assemble at the north car park.",
];
let quiet = 0;
for (const t of EMERGENCIES) { const r = audit(t); if (r.verdict !== 'BLOCK' && !r.chip) quiet++; }
ok('all legitimate emergencies stay silent (no chip)', quiet === EMERGENCIES.length, `${quiet}/${EMERGENCIES.length}`);

console.log(`\n  scams caught ${caught}/${SCAMS.length} · emergencies silent ${quiet}/${EMERGENCIES.length}`);
console.log(`  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
