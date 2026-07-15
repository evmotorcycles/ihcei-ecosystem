// api/gemini-ground.js — Gemini-backed GROUNDING check (deep-mode fidelity).
// ============================================================================
// The deep-mode fidelity extractor for Novora PAGES: given a SOURCE passage and
// a spoken CLAIM (a transcript segment), does the claim actually follow from the
// source, or is it a hallucination / over-simplification? Returns a calibrated
// alignment probability. Fast mode (lexical overlap) runs on-device in PAGES;
// this is the paid, semantic deep hop, invoked only on the ambiguous middle.
//
//   GET  /api/gemini-ground?health=1                     -> {ok, keyConfigured, model}
//   GET  /api/gemini-ground?test=1                       -> runs 2 built-in cases live
//   GET  /api/gemini-ground?source=...&claim=...         -> {grounded, p_alignment, reason}
//   POST /api/gemini-ground  {source, claim}             -> same
//
// Uses the Gemini API key from the project env (GEMINI_API_KEY /
// GOOGLE_API_KEY / GOOGLE_GENERATIVE_AI_API_KEY). Vercel egress reaches
// generativelanguage.googleapis.com where the sandbox proxy blocks it.

const MODEL = 'gemini-2.0-flash';
const KEY = () => process.env.Gemini_Key || process.env.GEMINI_KEY || process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || process.env.GOOGLE_GENERATIVE_AI_API_KEY || null;
const clip = p => Math.max(0.01, Math.min(0.99, p));

async function ground(source, claim, key) {
  const prompt = `You are a strict grounding checker for AI-generated media. Decide whether the CLAIM is fully supported by the SOURCE. A claim is grounded ONLY if every factual assertion in it is stated in or directly entailed by the source. Over-simplifications that change meaning, added numbers, or unstated inferences are NOT grounded.
Return ONLY minified JSON: {"grounded":true|false,"p_alignment":<0..1 confidence the claim is grounded>,"reason":"<=15 words"}

SOURCE:
"""${source.slice(0, 4000)}"""

CLAIM:
"""${claim.slice(0, 1000)}"""`;
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${encodeURIComponent(key)}`;
  const r = await fetch(url, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { temperature: 0, maxOutputTokens: 200 } }),
  });
  if (!r.ok) throw new Error('gemini ' + r.status + ': ' + (await r.text()).slice(0, 200));
  const data = await r.json();
  const text = (data.candidates?.[0]?.content?.parts || []).map(p => p.text).join('\n');
  const j = JSON.parse(text.replace(/```json|```/g, '').trim());
  return { grounded: !!j.grounded, p_alignment: clip(+j.p_alignment), reason: String(j.reason || '').slice(0, 120) };
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  const q = req.query || {};
  const key = KEY();
  if (q.health) return res.status(200).json({ ok: true, keyConfigured: Boolean(key), model: MODEL });
  if (!key) return res.status(500).json({ error: 'grounding requires a Gemini API key (GEMINI_API_KEY / GOOGLE_API_KEY)' });

  try {
    if (q.test) {
      const SOURCE = 'The study found a 3.2% reduction in latency after the cache layer was added. No change in error rate was observed.';
      const t0 = Date.now();
      const grounded = await ground(SOURCE, 'Adding the cache reduced latency by about 3 percent.', key);
      const hallucinated = await ground(SOURCE, 'The cache cut latency in half and eliminated all errors.', key);
      return res.status(200).json({ model: MODEL, ms: Date.now() - t0,
        cases: [{ label: 'grounded', ...grounded }, { label: 'hallucinated', ...hallucinated }] });
    }
    const source = q.source || req.body?.source;
    const claim = q.claim || req.body?.claim;
    if (!source || !claim) return res.status(400).json({ error: 'need source and claim' });
    const out = await ground(String(source), String(claim), key);
    return res.status(200).json({ model: MODEL, ...out });
  } catch (e) {
    return res.status(500).json({ error: 'grounding error', detail: e.message });
  }
}
