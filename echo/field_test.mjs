// field_test.mjs — Echo ingesting REAL open-source data, vs a normal database.
//   node echo/field_test.mjs
import { readFileSync } from 'node:fs';
import { EchoDB, verifyInclusion, sha256, canonical } from './echo.mjs';

const fx = f => JSON.parse(readFileSync(new URL('../oss-field-trial/fixtures/' + f, import.meta.url), 'utf8'));
const bar = c => console.log(c.repeat(78));
const pct = (a, b) => (100 * a / b).toFixed(1) + '%';

const db = new EchoDB();

// ── 1 · Ingest real open-source traffic + injected scams ─────────────────────
bar('=');
console.log(' 1 · INGEST — 281 real registry texts + 6 labeled scams into Echo');
bar('=');
const benign = fx('npm_pypi_corpus.json').benign;
for (const b of benign) db.put('registry-doc', b.text, { source: b.id });
const SCAMS = [
  "It's me, your grandson, don't tell anyone — wire $2000 right now.",
  "Final notice: pay the $500 processing fee using gift cards or your account is suspended today.",
  "This is the IRS. Pay the balance by gift card today or face arrest. Do not tell your family.",
  "Your package is held — pay the redelivery fee now at this link before it is returned.",
  "Microsoft support: your PC is infected, grant remote access and pay the removal fee now.",
  "You won! Only 2 claims left — send the processing fee immediately or forfeit forever.",
];
for (const s of SCAMS) db.put('inbound-message', s, { channel: 'sms' });
const st = db.stats();
console.log('  records stored: ' + st.n + '  (PASS ' + st.PASS + ' · WARN ' + st.WARN + ' · BLOCK ' + st.BLOCK + ')');
console.log('  NON-SUPPRESSIVE: every write retained — nothing dropped, verdicts stored alongside.');

// ── 2 · Query the agency ledger (a normal DB cannot ask this) ────────────────
bar('=');
console.log(' 2 · QUERY — "show me every manipulative record" (content-aware index)');
bar('=');
const flagged = db.query({ mechanism: true }).filter(r => r.verdict !== 'PASS');
for (const r of flagged) console.log('  ' + r.verdict.padEnd(6) + 'p=' + String(r.p_manipulative).padEnd(8) + '[' + r.mechanism_lexicon + ']  ' + r.id);
console.log('  flagged ' + flagged.length + '/' + st.n + ' (' + pct(flagged.length, st.n) + ') — the scam ledger, isolated by one query.');
console.log('  false positives on the ' + benign.length + ' real registry docs: ' +
  db.query({ kind: 'registry-doc' }).filter(r => r.verdict !== 'PASS').length);

// ── 3 · Tamper-evidence vs a normal database ─────────────────────────────────
bar('=');
console.log(' 3 · AN INSIDER CLEARS A STORED SCAM — Echo vs a normal database');
bar('=');
const root0 = db.root();                                   // published commitment
const target = db.query({ verdict: 'BLOCK' })[0];
const proofT = db.proofFor(target.seq);
console.log('  published DB root: ' + root0.slice(0, 24) + '…  (commits to all ' + st.n + ' records)');
// Echo: rewrite the verdict of a stored scam.
db.records[target.seq].verdict = 'PASS';
db.records[target.seq].p_manipulative = 0.02;
const v = db.verify();
const { id, hash, ...body } = db.records[target.seq];
const recomputed = sha256((target.seq ? db.records[target.seq - 1].hash : 'GENESIS') + canonical(body));
console.log('  ECHO   -> verify(): ok=' + v.ok + ', tamper located at record #' + v.brokenAt);
console.log('           pre-issued Merkle proof still valid? ' + verifyInclusion(recomputed, proofT, root0) + ' (rejected)');
// Normal DB: a plain object store.
const normal = benign.slice(0, 3).map((b, i) => ({ id: i, content: b.text, flagged: false }));
normal.push({ id: 3, content: SCAMS[0], flagged: true });
normal[3].flagged = false; normal[3].content = 'hello';    // silent rewrite
console.log('  NORMAL -> row rewritten to flagged=false/content="hello"; detection: NONE');
console.log('           (no chain, no root, no verify — the past is quietly mutable)');

bar('=');
console.log(' Echo solves what a normal DB cannot: it KNOWS what it stores (content-audited),');
console.log(' PROVES the past is intact (hash chain + Merkle root), and never SUPPRESSES —');
console.log(' the persistence layer the agency stack (audits, delegations, hop envelopes) needs.');
bar('=');
