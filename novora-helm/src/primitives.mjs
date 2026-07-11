// primitives.mjs — HELM DELEGATE / DEVELOP / PROVE · GT v18.2
// ============================================================================
// The three primitives beyond AUDIT (helm-core.mjs). All local, no network.
// PROVE uses Web Crypto SHA-256 (present in browsers and Node 18+), so the
// wallet's append/verify are async; everything else is synchronous.

const enc = new TextEncoder();
async function sha256(str) {
  const buf = await crypto.subtle.digest('SHA-256', enc.encode(str));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
}

// ── PROVE: the personal certificate wallet (hash-chained, tamper-evident) ────
// Each entry's hash = SHA-256(prevHash + canonical(payload)). Any edit to a
// past entry breaks the chain from that point forward — verify() locates it.
export class CertificateWallet {
  constructor() { this.chain = []; }

  static _canonical(value) {
    // Deterministic, RECURSIVE key-sorted serialization so the hash covers all
    // nested payload content and is reproducible across engines. (A plain array
    // replacer would silently drop nested keys and make the chain forgeable.)
    if (value === null || typeof value !== 'object') return JSON.stringify(value);
    if (Array.isArray(value)) return '[' + value.map(CertificateWallet._canonical).join(',') + ']';
    return '{' + Object.keys(value).sort().map(k =>
      JSON.stringify(k) + ':' + CertificateWallet._canonical(value[k])).join(',') + '}';
  }

  async append(kind, payload) {
    const prev = this.chain.length ? this.chain[this.chain.length - 1].hash : 'GENESIS';
    const ts = new Date().toISOString();
    const body = { kind, ts, payload };
    const hash = await sha256(prev + CertificateWallet._canonical(body));
    const cert = { id: 'CERT-' + hash.slice(0, 8).toUpperCase(), prev, hash, ...body };
    this.chain.push(cert);
    return cert;
  }

  // Returns { ok, brokenAt }. brokenAt is the index of the first tampered link.
  async verify() {
    for (let i = 0; i < this.chain.length; i++) {
      const c = this.chain[i];
      const prev = i === 0 ? 'GENESIS' : this.chain[i - 1].hash;
      if (c.prev !== prev) return { ok: false, brokenAt: i, reason: 'prev-link mismatch' };
      const recomputed = await sha256(prev + CertificateWallet._canonical({ kind: c.kind, ts: c.ts, payload: c.payload }));
      if (recomputed !== c.hash) return { ok: false, brokenAt: i, reason: 'hash mismatch' };
    }
    return { ok: true, brokenAt: -1 };
  }

  export() { return JSON.parse(JSON.stringify(this.chain)); }
}

// ── DELEGATE: the decision-permission table (the OAuth of agency) ─────────────
// Stake-bounded, revocable grants from a person to an agent. check() returns
// allow | draft | deny with the reason, and (optionally) writes a certificate.
export class DelegationTable {
  constructor(wallet = null) { this.grants = new Map(); this.wallet = wallet; this._n = 0; }

  // permission: 'allow' | 'draft' | 'deny'; maxStake in currency units (0 = none)
  grant({ agent, action, permission = 'allow', maxStake = 0 }) {
    const id = 'GRANT-' + (++this._n).toString().padStart(4, '0');
    const g = { id, agent, action, permission, maxStake, revoked: false, created: new Date().toISOString() };
    this.grants.set(id, g);
    return g;
  }

  revoke(id) {
    const g = this.grants.get(id);
    if (!g) return false;
    g.revoked = true; g.revokedAt = new Date().toISOString();
    return true;
  }

  // Decide whether an agent may take an action at a given stake. Default deny.
  async check({ agent, action, stake = 0 }) {
    const g = [...this.grants.values()].find(x => x.agent === agent && x.action === action && !x.revoked);
    let decision, reason;
    if (!g) { decision = 'deny'; reason = 'no active grant (default deny)'; }
    else if (g.permission === 'deny') { decision = 'deny'; reason = 'explicit deny grant'; }
    else if (stake > g.maxStake) { decision = 'deny'; reason = `stake ${stake} exceeds cap ${g.maxStake}`; }
    else { decision = g.permission; reason = `grant ${g.id} (cap ${g.maxStake})`; }
    if (this.wallet) await this.wallet.append('delegation', { agent, action, stake, decision, reason });
    return { decision, reason, grant: g ? g.id : null };
  }

  list() { return [...this.grants.values()]; }
}

// ── DEVELOP: capacity vs. dependency, not screen-time (design §5) ─────────────
// Records observable proxies per AI interaction and reports a trend to the
// PERSON ONLY. Higher developmentScore = growing capacity; lower = substituting.
// Proxies (each 0..1): did the person verify the AI's answer? did they add their
// own reasoning rather than accept verbatim? was the task within their capacity
// (development) vs. fully outsourced (dependency)?
export class CapacityTracker {
  constructor(windowSize = 30) { this.events = []; this.windowSize = windowSize; }

  record({ verified = false, addedOwnReasoning = false, acceptedVerbatim = false, tookOverThinking = false }) {
    // developmental if the person stays in the loop; dependent if they outsource.
    const dev = (verified ? 0.4 : 0) + (addedOwnReasoning ? 0.4 : 0) + (acceptedVerbatim ? 0 : 0.2);
    const dep = (tookOverThinking ? 0.6 : 0) + (acceptedVerbatim ? 0.4 : 0);
    const e = { t: Date.now(), dev: Math.min(1, dev), dep: Math.min(1, dep) };
    this.events.push(e);
    return e;
  }

  // Returns a score in (0,1): fraction of recent capacity that is developmental.
  // Also a trend: comparing the newer half of the window to the older half.
  report() {
    const w = this.events.slice(-this.windowSize);
    if (!w.length) return { developmentScore: null, trend: 'no-data', n: 0 };
    const mean = arr => arr.reduce((a, b) => a + b, 0) / Math.max(arr.length, 1);
    const dev = mean(w.map(e => e.dev)), dep = mean(w.map(e => e.dep));
    const score = dev / Math.max(dev + dep, 1e-9);
    let trend = 'steady';
    if (w.length >= 6) {
      const half = Math.floor(w.length / 2);
      const older = w.slice(0, half), newer = w.slice(half);
      const s = a => { const d = mean(a.map(e => e.dev)), p = mean(a.map(e => e.dep)); return d / Math.max(d + p, 1e-9); };
      const delta = s(newer) - s(older);
      trend = delta > 0.08 ? 'developing' : delta < -0.08 ? 'substituting' : 'steady';
    }
    return { developmentScore: +score.toFixed(3), trend, n: w.length };
  }
}
