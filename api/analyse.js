// api/analyse.js
// Vercel Serverless Function — keeps ANTHROPIC_API_KEY server-side
// This is the secure proxy between the browser and Claude API

export default async function handler(req, res) {
  // CORS headers for browser requests
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(500).json({
      error: 'API key not configured',
      message: 'Add ANTHROPIC_API_KEY to Vercel environment variables'
    });
  }

  const { text, system, product } = req.body;

  if (!text || !system) {
    return res.status(400).json({ error: 'Missing text or system prompt' });
  }

  // Basic rate limiting by IP (simple — upgrade with Redis for production)
  // For now, Vercel's edge handles most abuse

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 900,
        system: system,
        messages: [{ role: 'user', content: text }]
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Anthropic API error:', response.status, errorText);
      return res.status(response.status).json({
        error: 'API error',
        status: response.status
      });
    }

    const data = await response.json();
    return res.status(200).json(data);

  } catch (error) {
    console.error('Handler error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
