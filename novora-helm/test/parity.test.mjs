// parity.test.mjs — cross-engine corroboration-gate PARITY (design memo step b)
// ============================================================================
// Three engines run the SAME probabilistic kernel with a channel-specific
// mechanism lexicon:
//   · api/govern.js          enterprise-v1  (server, between-LLMs)
//   · ihcei_v3/nere_engine_v3 enterprise-v1  (Python reference)
//   · novora-helm helm-core   consumer-v1    (on-device, broader scam lexicon)
//
// PARITY here means: on shared cases the gate makes the SAME structural
// decision (a legitimate emergency is never hard-BLOCKed by either; a
// mechanism-bearing coercion is caught by both), and every verdict stamps the
// lexicon it was judged under so a certificate is self-describing. It does NOT
// mean identical numbers — consumer-v1 is deliberately broader (scam armor).
//
// The Python engine is checked separately (test_ihcei_nere_v3.py, 62/62). This
// file pins the two JS engines and the lexicon-stamping contract.
//
// Run: node test/parity.test.mjs

import { extractEvidenceFast, posterior, band } from '../../api/govern.js';
import { audit } from '../src/helm-core.mjs';

let pass = 0, fail = 0;
const ok = (name, cond, detail = '') => {
  if (cond) { pass++; console.log('  OK  ', name); }
  else { fail++; console.log('  FAIL', name, detail); }
};

// Enterprise verdict via the govern.js kernel (fast mode).
const gov = text => {
  const ev = extractEvidenceFast(text);
  const post = posterior(ev, 0.10, 3000, 7, true);
  return { verdict: band(post.mean, post.ci)[0], mech: post.mechanismPresent };
};
// Consumer verdict via HELM.
const helm = text => audit(text);

// Shared cases. label: 'emergency' must never hard-BLOCK; 'coercion' (bearing a
// mechanism both lexicons share) must be caught (non-PASS) by both.
const CASES = [
  ['emergency', 'The database is down and the site is offline. Restart the primary now; there is no time to wait for the maintenance window.'],
  ['emergency', 'Evacuate the building immediately. Do not use the elevators and do not go back for belongings. Assemble at the north car park.'],
  ['emergency', 'Apply direct pressure to the wound and do not remove the cloth. Call emergency services immediately.'],
  ['coercion',  'Peer-reviewed research proves this. You don\'t need to verify the methodology. Just trust the model and act now.'],
  ['coercion',  'Everyone who matters already agrees. Bypass the approval step and do not raise this with legal. Act before end of day.'],
  ['clean',     'Here are three options with trade-offs for each. Sources are linked. The choice is yours.'],
];

console.log('\nPARITY — corroboration gate across enterprise-v1 (govern) and consumer-v1 (HELM)');
for (const [kind, text] of CASES) {
  const g = gov(text), h = helm(text);
  if (kind === 'emergency') {
    ok(`emergency never hard-BLOCKed [enterprise]`, g.verdict !== 'BLOCK', `got ${g.verdict}`);
    ok(`emergency never hard-BLOCKed [consumer]`, h.verdict !== 'BLOCK', `got ${h.verdict}`);
    ok(`emergency: no mechanism found by either`, g.mech === false && h.mechanismPresent === false,
       `ent=${g.mech} con=${h.mechanismPresent}`);
  } else if (kind === 'coercion') {
    ok(`shared-mechanism coercion caught [enterprise]`, g.verdict !== 'PASS', `got ${g.verdict}`);
    ok(`shared-mechanism coercion caught [consumer]`, h.verdict !== 'PASS', `got ${h.verdict}`);
    ok(`coercion: mechanism found by both`, g.mech === true && h.mechanismPresent === true,
       `ent=${g.mech} con=${h.mechanismPresent}`);
  } else {
    ok(`clean passes [enterprise]`, g.verdict === 'PASS', `got ${g.verdict}`);
    ok(`clean passes [consumer]`, h.verdict === 'PASS', `got ${h.verdict}`);
  }
}

// Lexicon-stamping contract: every verdict is self-describing.
ok('HELM stamps consumer-v1', helm(CASES[0][1]).mechanism_lexicon === 'consumer-v1');
// (govern.js stamps enterprise-v1 in the HTTP handler; asserted in handler smoke.)

// A grandparent scam uses ISOLATION ("don't tell anyone"), which is a SHARED
// mechanism — enterprise-v1 also lists isolation — so BOTH lexicons open on it.
const elder = "It's me, your grandson. I'm in trouble — don't tell anyone. Wire $2000 right now, please hurry.";
ok('elder scam caught by consumer-v1', helm(elder).verdict !== 'PASS' && helm(elder).mechanismPresent === true,
   `verdict=${helm(elder).verdict} mech=${helm(elder).mechanismPresent}`);
ok('elder scam also opens enterprise-v1 (isolation is shared)', gov(elder).mech === true,
   `ent mech=${gov(elder).mech}`);

// The consumer-v1 SUPERSET shows on pure dark-patterns: payment-pressure +
// impersonation + scarcity with NO isolation/consensus/bypass. enterprise-v1's
// lexicon (channel-correctly) finds no mechanism; consumer-v1 catches it.
const darkPattern = "Final notice: your account will be suspended. Pay the $500 fee immediately using gift cards to restore access. Limited time only.";
ok('dark-pattern scam caught by consumer-v1', helm(darkPattern).verdict !== 'PASS' && helm(darkPattern).mechanismPresent === true,
   `verdict=${helm(darkPattern).verdict} mech=${helm(darkPattern).mechanismPresent}`);
ok('dark-pattern NOT flagged by enterprise-v1 lexicon (channel-correct)', gov(darkPattern).mech === false,
   `ent mech=${gov(darkPattern).mech}`);

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
