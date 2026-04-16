import { Anthropic } from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

export default async function handler(req, res) {
  // Handle CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { product, text, systemPrompt } = req.body;

  if (!text || !systemPrompt) {
    return res.status(400).json({ error: 'Missing text or system prompt' });
  }

  try {
    const msg = await anthropic.messages.create({
      model: "claude-3-5-sonnet-20240620",
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: "user", content: text }],
    });

    const raw = msg.content[0].text;
    try {
      // Robust JSON extraction
      const jsonStart = raw.indexOf('{');
      const jsonEnd = raw.lastIndexOf('}');
      if (jsonStart !== -1 && jsonEnd !== -1) {
        const jsonStr = raw.substring(jsonStart, jsonEnd + 1);
        const parsed = JSON.parse(jsonStr);
        return res.status(200).json(parsed);
      }
      return res.status(200).json({ error: 'No JSON found', analysis: raw });
    } catch (e) {
      return res.status(200).json({ error: 'Parse error', analysis: raw });
    }
  } catch (error) {
    console.error('Anthropic API Error:', error);
    return res.status(500).json({ error: error.message });
  }
}
