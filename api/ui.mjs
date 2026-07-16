// api/ui.mjs — serve the Novora suite UI as HTML from a function.
// ============================================================================
// project-6q4gj is an API-only Vercel project: it serves /api/* functions but
// NO static files (a rewrite to novora-suite/public/index.html 404s because that
// path isn't served statically). So we serve the self-contained suite HTML
// through a function instead — the one thing that demonstrably works here — and
// rewrite `/` -> `/api/ui` in vercel.json. The HTML file is bundled via the
// `includeFiles` config so readFileSync finds it at runtime.

import { readFileSync } from 'node:fs';
import { join } from 'node:path';

let cached = null;
function loadHtml() {
  if (cached) return cached;
  const candidates = [
    join(process.cwd(), 'novora-suite/public/index.html'),
    new URL('../novora-suite/public/index.html', import.meta.url).pathname,
  ];
  for (const p of candidates) {
    try { cached = readFileSync(p, 'utf8'); return cached; } catch { /* try next */ }
  }
  return null;
}

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const html = loadHtml();
  if (!html) {
    res.setHeader('Content-Type', 'application/json');
    return res.status(500).json({ error: 'UI asset not found in bundle' });
  }
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate');
  return res.status(200).send(html);
}
