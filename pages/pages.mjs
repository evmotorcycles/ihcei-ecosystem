// pages.mjs — Novora PAGES: provenance + attestation for generative media.
// ============================================================================
// A generated podcast/video is a flat file: you cannot pause a spoken sentence
// and trace it to the source, and you cannot tell if the audio was spliced.
// PAGES binds a transcript to its sources with two tested structures:
//
//   TEMPORAL HOP CHAIN   each segment t is hash-chained to t-1 over its content
//     + metadata, so editing a spoken claim ("not safe" -> "safe") or splicing
//     the stream breaks the chain at the exact timestamp.
//   TAP-TO-SOURCE        the grounding passages form a Merkle tree; each segment
//     carries an inclusion proof of its passage, so one tap shows the un-mutated
//     source AND proves it is the one committed in the published root.
//
// AUDIT per segment: (a) manipulation (NERE consumer gate) and (b) GROUNDING —
// fast mode is on-device lexical alignment (overlap + fabricated-number
// detection); deep mode is an optional pluggable async grounder (buildStream's
// `ground` hook) — bring your own semantic checker for the ambiguous middle.
// Non-suppressive: verdicts ride alongside; the listener decides.

import { sha256, canonical, merkleRoot, merkleProof, verifyInclusion } from '../echo/echo.mjs';
import { audit } from '../novora-helm/src/helm-core.mjs';

// ── fast-mode grounding (on-device) ──────────────────────────────────────────
const STOP = new Set('the a an and or of to in is are was were be been being for on with as by at this that these those it its from into their our your his her they we you i not no do does did have has had will would can could may might than then so such also more most much many few'.split(' '));
const words = s => (s.toLowerCase().match(/[a-z0-9]+/g) || []);
const nums = s => (s.match(/\d+(?:\.\d+)?%?/g) || []);
export function groundFast(source, claim) {
  const src = new Set(words(source));
  const cw = words(claim).filter(w => !STOP.has(w) && w.length > 2);
  const overlap = cw.length ? cw.filter(w => src.has(w)).length / cw.length : 1;
  const claimNums = nums(claim), srcNums = new Set(nums(source));
  const addedNumbers = claimNums.filter(n => !srcNums.has(n));   // fabricated statistic = classic media hallucination
  let p = overlap;
  if (addedNumbers.length) p = Math.min(p, 0.25);
  return {
    grounded: p >= 0.6 && addedNumbers.length === 0,
    p_alignment: +Math.max(0.02, Math.min(0.98, p)).toFixed(3),
    overlap: +overlap.toFixed(2), addedNumbers, mode: 'fast',
  };
}

const metaOf = s => ({ t: s.t, sourceId: s.sourceId, grounded: s.grounded, p_alignment: s.p_alignment, ground_mode: s.ground_mode, verdict: s.verdict, mechanism_lexicon: s.mechanism_lexicon });

// ── build a PAGES-certified stream from a transcript + its sources ───────────
// transcript: [{ t, text, sourceId }]   sources: { id: passageText }
// ground: optional async (source, claim) => {grounded, p_alignment, mode} for deep mode.
export async function buildStream(transcript, sources, { ground = null } = {}) {
  const ids = Object.keys(sources);
  const leaves = ids.map(id => sha256(sources[id]));       // content hash of each source passage
  const root = merkleRoot(leaves);
  const idx = Object.fromEntries(ids.map((id, i) => [id, i]));

  const segments = [];
  let prev = 'GENESIS';
  for (const seg of transcript) {
    const srcText = sources[seg.sourceId] || '';
    const g = ground ? await ground(srcText, seg.text) : groundFast(srcText, seg.text);
    const a = audit(seg.text);                             // manipulation check on the spoken words
    const contentHash = sha256(seg.text);
    const s = { t: seg.t, sourceId: seg.sourceId, text: seg.text, contentHash,
      grounded: g.grounded, p_alignment: g.p_alignment, ground_mode: g.mode || 'deep',
      verdict: a.verdict, mechanism_lexicon: a.mechanism_lexicon, prev,
      source_leaf: leaves[idx[seg.sourceId]], source_proof: merkleProof(leaves, idx[seg.sourceId]) };
    s.hash = sha256(contentHash + canonical(metaOf(s)) + prev);
    segments.push(s);
    prev = s.hash;
  }
  return { v: 'pages-0.1', root, segments };
}

// ── verify the temporal chain (splice / word-swap detection) ─────────────────
export function verifyStream(stream) {
  let prev = 'GENESIS';
  for (let i = 0; i < stream.segments.length; i++) {
    const s = stream.segments[i];
    if (s.prev !== prev) return { ok: false, brokenAt: i, t: s.t, reason: 'prev-link mismatch (splice)' };
    if (sha256(s.text) !== s.contentHash) return { ok: false, brokenAt: i, t: s.t, reason: 'spoken text altered' };
    if (sha256(s.contentHash + canonical(metaOf(s)) + prev) !== s.hash) return { ok: false, brokenAt: i, t: s.t, reason: 'segment metadata tampered' };
    prev = s.hash;
  }
  return { ok: true, brokenAt: -1 };
}

// ── tap-to-source: prove a segment's grounding passage is the committed one ──
export function tapToSource(stream, i, sources) {
  const s = stream.segments[i];
  const passage = sources[s.sourceId];
  const inSet = verifyInclusion(sha256(passage), s.source_proof, stream.root);
  return { t: s.t, sourceId: s.sourceId, passage, p_alignment: s.p_alignment, grounded: s.grounded, provenInGroundingSet: inSet };
}

// ── attestation: is a stream PAGES-certified and intact? (deepfake armor) ────
export function isCertified(stream) {
  if (!stream || stream.v !== 'pages-0.1' || !Array.isArray(stream.segments) || !stream.segments.length) return false;
  return verifyStream(stream).ok;
}
