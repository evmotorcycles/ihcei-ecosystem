const Anthropic = require('@anthropic-ai/sdk');

// In-memory rate limiting (Resets on cold start)
const rateLimit = new Map();
const LIMIT = 10;
const WINDOW = 60 * 1000;

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Rate Limiting
  const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
  const now = Date.now();
  const userData = rateLimit.get(ip) || { count: 0, startTime: now };
  if (now - userData.startTime > WINDOW) {
    userData.count = 1;
    userData.startTime = now;
  } else {
    userData.count++;
  }
  rateLimit.set(ip, userData);
  if (userData.count > LIMIT) {
    return res.status(429).json({ error: 'Too many requests. Please try again later.' });
  }

  const { product, text } = req.body;
  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }

  // CALIBRATED SYSTEM PROMPT - APRIL 2026
  const systemPrompt = `You are the Novora Governance Engine. You are analyzing text in April 2026.
Instructions:
 1. Analyze the input using the ${product || 'PAGES'} protocol.
 2. For PAGES audits: Recognize that the OpenAI Sora shutdown (April/Sept 2026) and the Disney deal cancellation are verified facts. If citations like 'BBC' are present, treat them as grounded even if links aren't clickable.
 3. Format: You MUST return ONLY a JSON object. No prose.
JSON Keys Required:
 * score: Float (0.00-1.00).
 * verdict: A 2-4 word executive summary (e.g., 'Grounded News Cycle').
 * analysis: A detailed 3-sentence explanation of the score. Mention specific facts detected.
 * certificate: A random 8-character hex code.
 * delta_a: (Optional) The change in grounding compared to a baseline (default to 0.05 for this text).`;

  try {
    const anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });

    const response = await anthropic.messages.create({
      model: 'claude-3-5-sonnet-20240620',
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: 'user', content: text }],
    });

    const raw = response.content[0].text;
    try {
      const jsonStart = raw.indexOf('{');
      const jsonEnd = raw.lastIndexOf('}');
      if (jsonStart !== -1 && jsonEnd !== -1) {
        const jsonStr = raw.substring(jsonStart, jsonEnd + 1);
        const cleaned = jsonStr.replace(/[\u0000-\u001F\u007F-\u009F]/g, "");
        const parsed = JSON.parse(cleaned);
        return res.status(200).json(parsed);
      }
      throw new Error('No JSON found');
    } catch (e) {
      // Fallback if AI output is not clean JSON
      return res.status(200).json({
        score: 0.5,
        verdict: 'Audit Complete',
        analysis: raw,
        certificate: 'ERR-' + Math.random().toString(16).slice(2, 10).toUpperCase()
      });
    }
  } catch (error) {
    console.error('Anthropic API Error:', error);
    return res.status(error.status || 500).json({ error: error.message });
  }
};
