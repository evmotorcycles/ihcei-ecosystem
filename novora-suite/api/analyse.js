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

  const { system, messages } = req.body;

  if (!messages) {
    return res.status(400).json({ error: 'Messages are required' });
  }

  try {
    const anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });

    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514', // Exact model from prompt
      max_tokens: 800,
      system: system,
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
