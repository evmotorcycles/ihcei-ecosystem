// api/screen.js — Novora Suite FAST mode ($0, no Anthropic key).
// ============================================================================
// The zero-cost, no-network-LLM path for all nine Novora products. Runs the
// on-device NERE-kernel screen (novora-suite/engine/fastmode.mjs) server-side
// and returns the SAME JSON shape as the paid /api/analyse deep mode, so the
// client renders either identically. This is what lets the suite deploy and be
// used WITHOUT an Anthropic API key — the deep semantic hop stays optional.
//
//   GET  /api/screen?product=bridge&text=...   -> { score, verdict, ... , mode:'fast' }
//   POST /api/screen  { product, text }        -> same
//   GET  /api/screen?health=1                  -> { ok, products, mode:'fast', cost:'$0' }
//
// No key, no upstream call, no cost. Input capped at 8 KB.

import { screen, PRODUCT_IDS } from '../novora-suite/engine/fastmode.mjs';

const MAX_INPUT = 8000;

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const q = req.query || {};
  if (q.health) return res.status(200).json({ ok: true, products: PRODUCT_IDS, mode: 'fast', cost: '$0', key_required: false });

  const product = (q.product || req.body?.product || '').toString().toLowerCase();
  const text = (q.text || req.body?.text || '').toString();
  if (!PRODUCT_IDS.includes(product)) {
    return res.status(400).json({ error: 'unknown product', products: PRODUCT_IDS });
  }
  if (!text) return res.status(400).json({ error: 'need text' });
  if (text.length > MAX_INPUT) return res.status(413).json({ error: `Input too long (max ${MAX_INPUT} characters)` });

  try {
    return res.status(200).json({ product, ...screen(product, text) });
  } catch (e) {
    return res.status(500).json({ error: 'screen error', detail: e.message });
  }
}
