// echo.test.mjs — Echo agency-database assertions. node echo/echo.test.mjs
import { EchoDB, verifyInclusion, sha256, canonical } from './echo.mjs';

let pass = 0, fail = 0;
const ok = (n, c, d = '') => { if (c) { pass++; console.log('  OK  ', n); } else { fail++; console.log('  FAIL', n, d); } };

console.log('\nEcho — the agency database');
const db = new EchoDB();

// A · content-audited, non-suppressive writes
const scam = db.put('message', "It's me, don't tell anyone, wire the money now or lose everything.");
const good = db.put('message', "Here are three options with trade-offs and linked sources; the choice is yours.");
const grant = db.put('delegation', "agent=deploy-bot action=publish stake=40 cap=100 -> allow");
ok('a scam is stored WITH a BLOCK verdict (not dropped)', scam.verdict === 'BLOCK' && db.get(scam.id));
ok('benign content is stored and passes', good.verdict === 'PASS');
ok('every record carries a mechanism_lexicon stamp', db.records.every(r => r.mechanism_lexicon));
ok('non-suppressive: all writes are retained', db.records.length === 3);

// B · query the agency ledger
ok('query BLOCK returns exactly the scam ledger', db.query({ verdict: 'BLOCK' }).length === 1);
ok('query by kind works', db.query({ kind: 'delegation' }).length === 1 && db.query({ kind: 'message' }).length === 2);
ok('query minP threshold works', db.query({ minP: 0.85 }).every(r => r.p_manipulative >= 0.85));

// C · whole-history tamper evidence — capture the published commitments NOW,
// at commit time, exactly as an external auditor would receive them.
ok('clean chain verifies', db.verify().ok);
const root0 = db.root();
const proof0 = db.proofFor(0), proof2 = db.proofFor(2);
const leaf2 = db.records[2].hash;
ok('inclusion proof verifies against the published root', verifyInclusion(leaf2, proof2, root0));
ok('a record NOT in the DB fails inclusion', !verifyInclusion('deadbeef'.repeat(8), proof2, root0));

// D · an insider silently rewrites the stored scam verdict to PASS.
db.records[0].verdict = 'PASS';
db.records[0].p_manipulative = 0.01;
// Layer 1 — the append-only chain: verify() recomputes each hash from its body
// and finds record 0 no longer matches its stored link.
const v = db.verify();
ok('layer 1 — body tamper detected and located by verify()', !v.ok && v.brokenAt === 0, JSON.stringify(v));
// Layer 2 — the published Merkle root: recompute the tampered record's honest
// leaf and check it against the proof issued at commit time. It was never in the
// committed set, so any holder of root0 rejects it — no cooperation from the DB.
const { id, hash, ...body } = db.records[0];
const recomputedLeaf = sha256('GENESIS' + canonical(body));
ok('layer 2 — tampered record rejected by its own pre-issued Merkle proof',
   !verifyInclusion(recomputedLeaf, proof0, root0));
ok('an honest, untouched record still proves inclusion against the published root',
   verifyInclusion(leaf2, proof2, root0));

// E · the normal-database baseline: a plain mutable store has none of this
const normalDB = [{ id: 1, content: scamText() }];
normalDB[0].content = 'harmless';               // admin rewrites the row
ok('normal DB: the rewrite leaves no evidence (no verify, no root)',
   normalDB[0].content === 'harmless' && typeof normalDB.verify !== 'function');

function scamText() { return "It's me, don't tell anyone, wire the money now."; }

console.log(`\n  RESULT: ${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
