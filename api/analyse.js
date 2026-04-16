const Anthropic = require('@anthropic-ai/sdk');

// Very basic in-memory rate limiting (Note: resets on function cold start)
const rateLimit = new Map();
const LIMIT = 10; // 10 requests per minute per IP
const WINDOW = 60 * 1000;

module.exports = async (req, res) => {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Basic rate limiting
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

  const { messages, productType } = req.body;

  if (!messages) {
    return res.status(400).json({ error: 'Messages are required' });
  }

  // Overhauled System Instruction from user prompt
  const systemPrompt = `You are the Novora Governance Engine. You are analyzing text in April 2026.
Instructions:
 1. Analyze the input using the ${productType || 'PAGES'} protocol.
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
      model: 'claude-sonnet-4-20250514',
      max_tokens: 800,
      system: systemPrompt,
      messages: messages,
    });

    return res.status(200).json(response);
  } catch (error) {
    console.error('Anthropic API Error:', error);
    return res.status(error.status || 500).json({
      error: error.message || 'An error occurred during analysis'
    });
  }
};
