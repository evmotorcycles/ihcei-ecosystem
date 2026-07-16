// api/analyse.js — Novora Suite consumer analysis endpoint
// ============================================================================
// The secure server-side inference call for all nine Novora products. The
// browser POSTs {text, system}; the key and the model live here and never
// reach the client. Returns the raw Anthropic Messages response so the
// existing client parser (data.content[0].text) works unchanged.
//
// Model: claude-sonnet-5 — current Sonnet tier, near-Opus quality on the
// analysis/extraction workload these products run, priced for consumer volume
// ($3/$15 per MTok; intro $2/$10 through 2026-08-31). Override with NOVORA_MODEL.
//
// Rate limiting: best-effort per-IP daily cap held in module memory. Serverless
// instances are ephemeral and not shared, so this caps abuse per warm instance
// but is NOT a hard quota — wire Upstash/Vercel KV for real enforcement before
// monetizing the free tier (see README).

const MODEL = process.env.NOVORA_MODEL || 'claude-sonnet-5';
const FREE_PER_DAY = parseInt(process.env.NOVORA_FREE_PER_DAY || '5', 10);
const MAX_INPUT_CHARS = 8000;

// { ip: { day: 'YYYY-MM-DD', count: n } } — reset when the UTC day rolls over.
const hits = new Map();

function rateLimited(ip) {
  if (!ip || FREE_PER_DAY <= 0) return false;
  const day = new Date().toISOString().slice(0, 10);
  const rec = hits.get(ip);
  if (!rec || rec.day !== day) { hits.set(ip, { day, count: 1 }); return false; }
  rec.count += 1;
  return rec.count > FREE_PER_DAY;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(500).json({
      error: 'API key not configured',
      message: 'Add ANTHROPIC_API_KEY in Vercel Settings → Environment Variables and redeploy.',
    });
  }

  const { text, system } = req.body || {};
  if (!text || !system) return res.status(400).json({ error: 'Missing text or system prompt' });
  if (typeof text !== 'string' || typeof system !== 'string') {
    return res.status(400).json({ error: 'text and system must be strings' });
  }
  if (text.length > MAX_INPUT_CHARS) {
    return res.status(413).json({ error: `Input too long (max ${MAX_INPUT_CHARS} characters)` });
  }

  const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || req.socket?.remoteAddress;
  if (rateLimited(ip)) {
    return res.status(429).json({ error: `Daily free limit reached (${FREE_PER_DAY}/day). Upgrade to Pro for unlimited checks.` });
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 1024,
        system,
        messages: [{ role: 'user', content: text }],
      }),
    });

    if (!response.ok) {
      const detail = await response.text();
      return res.status(response.status).json({ error: 'Upstream API error', detail: detail.slice(0, 300) });
    }
    return res.status(200).json(await response.json());
  } catch (error) {
    return res.status(500).json({ error: 'Server error', detail: error.message });
  }
}
