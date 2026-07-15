// aips.mjs — Agency Internet Protocol Suite, reference implementation (GT v18.2)
// ============================================================================
// The normal internet moves bits and proves nothing about them above the
// transport: TCP checksums verify the wire, TLS encrypts the pipe, and then a
// validly-addressed packet is handed to the human raw. AIPS is the layer that
// was never built: every message crossing the network accumulates a HOP
// ENVELOPE — a hash-chained record of what each node's audit concluded, under
// which mechanism lexicon — and the receiver can verify the entire path.
//
// This file wires the ALREADY-TESTED primitives into the network shape:
//   L2 Cognitive Audit  = the gated kernel (govern.js enterprise / HELM consumer)
//   L3 Trust Attestation= the hop envelope (SHA-256 chain over canonical records)
//   L4 Delegation       = DelegationTable (default-deny, stake caps, revocable)
//   L5 Capacity         = CapacityTracker (receiver-side, reported to the person)
// L1 (the Shannon substrate) is inherited, not reimplemented.
//
// Contract, inherited and non-negotiable: NON-SUPPRESSIVE. No node drops or
// mutates content. Verdicts ride alongside the payload; release stays with the
// receiver. The network's job is to make manipulation VISIBLE and history
// UNFORGEABLE, not to censor.

import { createHash } from 'node:crypto';
import { extractEvidenceFast, posterior, band } from '../api/govern.js';
import { audit } from '../novora-helm/src/helm-core.mjs';

export const canonical = v => {
  if (v === null || typeof v !== 'object') return JSON.stringify(v);
  if (Array.isArray(v)) return '[' + v.map(canonical).join(',') + ']';
  return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canonical(v[k])).join(',') + '}';
};
export const sha256 = s => createHash('sha256').update(s).digest('hex');

// ── L2 · audit engines by node class ────────────────────────────────────────
function auditEnterprise(text) {
  const post = posterior(extractEvidenceFast(text), 0.10, 3000, 7, true);
  const [verdict, action] = band(post.mean, post.ci);
  return { verdict, action, p: +post.mean.toFixed(4), ci95: [+post.ci[0].toFixed(4), +post.ci[1].toFixed(4)],
           mechanism_present: post.mechanismPresent, mechanism_lexicon: 'enterprise-v1', engine: 'nere-v3-fast' };
}
function auditConsumer(text) {
  const r = audit(text);
  return { verdict: r.verdict, action: r.chip ? 'CHIP' : 'SILENT', p: r.p_manipulative, ci95: r.ci95,
           mechanism_present: r.mechanismPresent, mechanism_lexicon: r.mechanism_lexicon, engine: r.engine };
}

// ── L3 · the hop envelope ────────────────────────────────────────────────────
export function createEnvelope(text, origin) {
  return { v: 'aips-0.1', origin, content_sha256: sha256(text), hops: [] };
}

// ── an Agency node (router / gateway / device) ───────────────────────────────
export class AgencyNode {
  constructor(name, { cls = 'enterprise', delegation = null } = {}) {
    this.name = name;
    this.cls = cls;                    // 'enterprise' | 'consumer'
    this.delegation = delegation;      // L4 table, if this node enforces one
  }

  // Relay: audit the payload, chain the attestation. NEVER drops the message.
  relay(envelope, text) {
    const a = this.cls === 'consumer' ? auditConsumer(text) : auditEnterprise(text);
    const prev = envelope.hops.length ? envelope.hops[envelope.hops.length - 1].hash : 'GENESIS';
    const body = { node: this.name, ts: new Date().toISOString(), content_sha256: sha256(text), ...a, prev };
    const hash = sha256(prev + canonical(body) + envelope.content_sha256);
    envelope.hops.push({ ...body, hash });
    return envelope;
  }

  // L4: an agent-initiated ACTION at this node must clear the delegation table.
  async authorize(action) {
    if (!this.delegation) return { decision: 'deny', reason: 'node has no delegation table (default deny)' };
    return this.delegation.check(action);
  }
}

// Receiver-side path verification: recompute every link + the content hash.
// Any tamper — payload edit in flight, or retroactive verdict rewrite — breaks
// the chain at the exact hop.
export function verifyPath(envelope, text) {
  if (sha256(text) !== envelope.content_sha256)
    return { ok: false, brokenAt: 0, reason: 'payload does not match origin content hash' };
  for (let i = 0; i < envelope.hops.length; i++) {
    const { hash, ...body } = envelope.hops[i];
    const prev = i === 0 ? 'GENESIS' : envelope.hops[i - 1].hash;
    if (body.prev !== prev) return { ok: false, brokenAt: i, reason: 'prev-link mismatch' };
    if (body.content_sha256 !== envelope.content_sha256)
      return { ok: false, brokenAt: i, reason: 'hop saw different content (in-flight mutation)' };
    const recomputed = sha256(prev + canonical(body) + envelope.content_sha256);
    if (recomputed !== hash) return { ok: false, brokenAt: i, reason: 'hop record tampered' };
  }
  return { ok: true, brokenAt: -1 };
}

// Convenience: send a message across a path of nodes (the "normal internet"
// baseline is the same call with zero audit nodes — bits move, nothing attests).
export function send(text, path, origin = 'sender') {
  let env = createEnvelope(text, origin);
  for (const node of path) env = node.relay(env, text);
  return env;
}
