// echo.mjs — Echo, the Agency Database (GT v18.2)
// ============================================================================
// A normal database trusts whoever writes to it: it stores what it is given,
// keeps no proof the past wasn't rewritten, and has no idea whether the thing it
// just persisted is a scam or a genuine record. Echo is the database for the
// agency stack — the place audits, delegations, and hop envelopes live — built
// on three properties a normal store does not have:
//
//   1. APPEND-ONLY + HASH-CHAINED   every record links to the previous by hash,
//      so any edit to history is detectable and locatable (verify()).
//   2. CONTENT-AUDITED ON WRITE     every record is passed through the NERE
//      kernel; the verdict (PASS/WARN/BLOCK, posterior, mechanism, lexicon) is
//      stored ALONGSIDE the record. Echo is NON-SUPPRESSIVE: it never refuses a
//      write; it records what it concluded and lets the reader decide.
//   3. MERKLE-PROVABLE              a published root hash lets anyone verify a
//      single record is in the database — without being shown the others.
//
// Echo reuses only already-tested primitives: the HELM audit kernel and the same
// canonical SHA-256 serialization as the certificate wallet and the hop envelope.
// Fully synchronous (node:crypto), no network — it inherits privacy-by-topology.

import { createHash } from 'node:crypto';
import { audit } from '../novora-helm/src/helm-core.mjs';

export const sha256 = s => createHash('sha256').update(s).digest('hex');
export const canonical = v => {
  if (v === null || typeof v !== 'object') return JSON.stringify(v);
  if (Array.isArray(v)) return '[' + v.map(canonical).join(',') + ']';
  return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canonical(v[k])).join(',') + '}';
};

// ── Merkle tree over record hashes (published root + inclusion proofs) ────────
const pair = (a, b) => sha256(a + b);
function levels(leaves) {
  if (!leaves.length) return [['']];
  const out = [leaves.slice()];
  while (out[out.length - 1].length > 1) {
    const cur = out[out.length - 1], next = [];
    for (let i = 0; i < cur.length; i += 2) next.push(pair(cur[i], i + 1 < cur.length ? cur[i + 1] : cur[i]));
    out.push(next);
  }
  return out;
}
export const merkleRoot = leaves => levels(leaves)[levels(leaves).length - 1][0];
export function merkleProof(leaves, index) {
  const lv = levels(leaves), proof = [];
  let idx = index;
  for (let l = 0; l < lv.length - 1; l++) {
    const cur = lv[l], isRight = idx % 2 === 1;
    const sib = isRight ? idx - 1 : (idx + 1 < cur.length ? idx + 1 : idx);
    proof.push({ hash: cur[sib], siblingOnRight: !isRight });
    idx = Math.floor(idx / 2);
  }
  return proof;
}
export function verifyInclusion(leafHash, proof, root) {
  let h = leafHash;
  for (const s of proof) h = s.siblingOnRight ? pair(h, s.hash) : pair(s.hash, h);
  return h === root;
}

// ── Echo ─────────────────────────────────────────────────────────────────────
export class EchoDB {
  constructor({ auditor = audit } = {}) { this.records = []; this.auditor = auditor; }

  // NON-SUPPRESSIVE write. Audits the content, appends a hash-chained record
  // with the verdict stamped. Returns the stored record. Never throws on content.
  put(kind, content, meta = {}) {
    const text = String(content);
    const a = this.auditor(text);
    const prev = this.records.length ? this.records[this.records.length - 1].hash : 'GENESIS';
    const body = {
      seq: this.records.length, kind, ts: new Date().toISOString(),
      content_sha256: sha256(text),
      verdict: a.verdict, p_manipulative: a.p_manipulative,
      mechanism_present: a.mechanismPresent, mechanism_lexicon: a.mechanism_lexicon,
      meta, prev,
    };
    const hash = sha256(prev + canonical(body));
    const rec = { id: 'ECHO-' + hash.slice(0, 10).toUpperCase(), ...body, hash };
    this.records.push(rec);
    return rec;
  }

  get(id) { return this.records.find(r => r.id === id) || null; }

  // Query the agency ledger. All filters optional and ANDed.
  query({ kind, verdict, minP, sinceTs, mechanism } = {}) {
    return this.records.filter(r =>
      (kind === undefined || r.kind === kind) &&
      (verdict === undefined || r.verdict === verdict) &&
      (minP === undefined || r.p_manipulative >= minP) &&
      (mechanism === undefined || r.mechanism_present === mechanism) &&
      (sinceTs === undefined || r.ts >= sinceTs));
  }

  // Whole-history integrity: recompute every link. Locates the first tampered record.
  verify() {
    for (let i = 0; i < this.records.length; i++) {
      const { id, hash, ...body } = this.records[i];
      const prev = i === 0 ? 'GENESIS' : this.records[i - 1].hash;
      if (body.prev !== prev) return { ok: false, brokenAt: i, reason: 'prev-link mismatch' };
      if (sha256(prev + canonical(body)) !== hash) return { ok: false, brokenAt: i, reason: 'record tampered' };
    }
    return { ok: true, brokenAt: -1 };
  }

  // The published database root (commit to the whole set in one hash).
  root() { return merkleRoot(this.records.map(r => r.hash)); }
  // A portable proof that record `seq` is in the DB, checkable against root().
  proofFor(seq) { return merkleProof(this.records.map(r => r.hash), seq); }

  stats() {
    const by = v => this.records.filter(r => r.verdict === v).length;
    return { n: this.records.length, PASS: by('PASS'), WARN: by('WARN'), BLOCK: by('BLOCK') };
  }
}
