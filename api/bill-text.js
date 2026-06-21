// api/bill-text.js
// Batch proxy for Congress.gov bill full text.
// GET /api/bill-text?bills=104-hr-831,104-s-1044,...
//   -> { results: [ { congress, billType, billNumber, text, textLength, error } ] }
// GET /api/bill-text?health=1
//   -> { ok: true, keyConfigured: true/false }   (never returns the key itself)
//
// Env var: Congresskey  (Congress.gov / api.data.gov key, set in Vercel project settings)

const MAX_BATCH = 60;
const CONCURRENCY = 8;

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return res.json();
}

async function fetchText(url) {
  const res = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9",
    },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return res.text();
}

// LOCKED citation regex (same rule used in the repeal-classification pipeline,
// decided before any of these bills were examined): matches "NN U.S.C. NNNN"
// / "NN U.S.C. § NNNN" style citations.
const CITE_RE = /(\d{1,2})\s*U\.S\.C\.\s*§?\s*(\d{2,5}[A-Za-z]?)/g;

function extractCitations(text) {
  const out = new Set();
  let m;
  CITE_RE.lastIndex = 0;
  while ((m = CITE_RE.exec(text)) !== null) {
    out.add(`${m[1]}|${m[2]}`);
  }
  return Array.from(out).map(s => {
    const [title, section] = s.split("|");
    return [parseInt(title, 10), section];
  });
}

async function getBillFullText(congress, billType, billNumber, apiKey) {
  // Step 1: ask Congress.gov which text versions exist for this bill
  const metaUrl = `https://api.congress.gov/v3/bill/${congress}/${billType}/${billNumber}/text?api_key=${apiKey}&format=json`;
  const meta = await fetchJSON(metaUrl);

  const versions = (meta.textVersions || []);
  if (versions.length === 0) {
    return { text: null, note: "no text versions available" };
  }

  // Prefer the most recent version (first in list), prefer a "Formatted Text" format
  const latest = versions[0];
  const formats = latest.formats || [];
  const formatted = formats.find(f => f.type === "Formatted Text")
                  || formats.find(f => f.type === "Formatted XML")
                  || formats[0];

  if (!formatted) {
    return { text: null, note: "no usable format in latest text version" };
  }

  let raw = await fetchText(formatted.url);

  // Strip HTML tags if we got an HTML/XML formatted version, keep plain text
  const text = raw.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();

  return { text, note: `source: ${formatted.type}`, versionDate: latest.date || null };
}

async function mapWithConcurrency(items, limit, worker) {
  const results = new Array(items.length);
  let idx = 0;
  async function runOne() {
    while (idx < items.length) {
      const cur = idx++;
      results[cur] = await worker(items[cur], cur);
    }
  }
  const runners = Array.from({ length: Math.min(limit, items.length) }, runOne);
  await Promise.all(runners);
  return results;
}

export default async function handler(req, res) {
  const apiKey = process.env.Congresskey;

  if (req.query.health) {
    res.status(200).json({ ok: true, keyConfigured: Boolean(apiKey) });
    return;
  }

  if (!apiKey) {
    res.status(500).json({ error: "Congresskey environment variable is not set" });
    return;
  }

  const billsParam = req.query.bills;
  if (!billsParam) {
    res.status(400).json({ error: "missing ?bills=congress-billtype-billnumber,... (e.g. 104-hr-831)" });
    return;
  }

  const ids = String(billsParam).split(",").map(s => s.trim()).filter(Boolean);
  if (ids.length === 0) {
    res.status(400).json({ error: "no valid bill identifiers parsed" });
    return;
  }
  if (ids.length > MAX_BATCH) {
    res.status(400).json({ error: `batch too large (${ids.length}); max ${MAX_BATCH} per request` });
    return;
  }

  const parsed = ids.map(id => {
    const parts = id.split("-");
    if (parts.length < 3) return { id, error: "malformed id, expected congress-billtype-number" };
    const [congress, billType, ...rest] = parts;
    return { id, congress, billType: billType.toLowerCase(), billNumber: rest.join("-") };
  });

  const includeText = req.query.fullText === "1";

  const results = await mapWithConcurrency(parsed, CONCURRENCY, async (item) => {
    if (item.error) return { id: item.id, error: item.error };
    try {
      const r = await getBillFullText(item.congress, item.billType, item.billNumber, apiKey);
      const citations = r.text ? extractCitations(r.text) : [];
      const out = {
        id: item.id,
        congress: item.congress,
        billType: item.billType,
        billNumber: item.billNumber,
        textLength: r.text ? r.text.length : 0,
        citations,
        note: r.note,
        versionDate: r.versionDate || null,
      };
      if (includeText) out.text = r.text;
      return out;
    } catch (e) {
      return { id: item.id, congress: item.congress, billType: item.billType, billNumber: item.billNumber, error: String(e.message || e) };
    }
  });

  res.status(200).json({ count: results.length, results });
}