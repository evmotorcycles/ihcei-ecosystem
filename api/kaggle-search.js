// api/kaggle-search.js
// Server-side Kaggle dataset search for the LISM dataset sweep. Vercel egress is
// not scope-bound, so this can reach the Kaggle API where the sandbox cannot.
//
//   GET /api/kaggle-search?q=patient+safety+incident+outcomes
//     -> { query, count, datasets: [ { ref, title, subtitle, totalBytes, url } ] }
//   GET /api/kaggle-search?health=1
//     -> { ok: true, keyConfigured: true/false }   (never returns the key)
//
// Env vars (set in Vercel project settings): KAGGLE_USERNAME, KAGGLE_KEY
// (from kaggle.json). The shape mirrors bill-text.js so kaggle_dataset_screen.py
// can consume it via --endpoint.

export default async function handler(req, res) {
  const user = process.env.KAGGLE_USERNAME;
  const key = process.env.KAGGLE_KEY;

  if (req.query.health) {
    res.status(200).json({ ok: true, keyConfigured: Boolean(user && key) });
    return;
  }
  if (!user || !key) {
    res.status(500).json({ error: "KAGGLE_USERNAME / KAGGLE_KEY not set in Vercel env" });
    return;
  }

  const q = req.query.q;
  if (!q) {
    res.status(400).json({ error: "missing ?q=<search terms>" });
    return;
  }
  const page = Math.max(parseInt(req.query.page || "1", 10) || 1, 1);
  const auth = "Basic " + Buffer.from(`${user}:${key}`).toString("base64");
  const url = `https://www.kaggle.com/api/v1/datasets/list?search=${encodeURIComponent(q)}&page=${page}`;

  try {
    const r = await fetch(url, { headers: { Authorization: auth } });
    if (!r.ok) {
      res.status(502).json({ error: `kaggle API ${r.status}`, detail: (await r.text()).slice(0, 200) });
      return;
    }
    const data = await r.json();
    const list = Array.isArray(data) ? data : (data.datasets || []);
    const datasets = list.map((d) => ({
      ref: d.ref,
      title: d.title,
      subtitle: d.subtitle || "",
      description: d.subtitle || "",
      totalBytes: d.totalBytes,
      usabilityRating: d.usabilityRating,
      url: d.url ? `https://www.kaggle.com${d.url}` : `https://www.kaggle.com/datasets/${d.ref}`,
    }));
    res.status(200).json({ query: String(q), page, count: datasets.length, datasets });
  } catch (e) {
    res.status(500).json({ error: String((e && e.message) || e) });
  }
}
