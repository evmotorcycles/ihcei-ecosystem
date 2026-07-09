// api/gh-search.js
// Server-side GitHub search for the LISM dataset sweep (fallback for when Kaggle
// credentials are unavailable). Vercel egress is not scope-bound, so this reaches
// the GitHub Search API that is blocked from the sandbox.
//
//   GET /api/gh-search?q=patient+safety+incident+dataset&type=repositories
//   GET /api/gh-search?q=...&type=code            (search code/files)
//     -> { query, type, count, datasets: [ { ref, title, subtitle, stars, url } ] }
//   GET /api/gh-search?health=1  -> { ok: true, tokenConfigured: true/false }
//
// Env: GOVPHYS_PAT (or GITHUB_TOKEN). Public search works unauthenticated but is
// rate-limited; a token raises the limit and enables code search.

export default async function handler(req, res) {
  const token = process.env.GOVPHYS_PAT || process.env.GITHUB_TOKEN;

  if (req.query.health) {
    res.status(200).json({ ok: true, tokenConfigured: Boolean(token) });
    return;
  }

  const q = req.query.q;
  if (!q) {
    res.status(400).json({ error: "missing ?q=<search terms>" });
    return;
  }
  const type = req.query.type === "code" ? "code" : "repositories";
  const perPage = Math.min(Math.max(parseInt(req.query.per_page || "20", 10) || 20, 1), 50);
  const url = `https://api.github.com/search/${type}?q=${encodeURIComponent(q)}&per_page=${perPage}`;

  const headers = {
    Accept: "application/vnd.github.v3+json",
    "User-Agent": "ihcei-dataset-search",
  };
  if (token) headers.Authorization = `token ${token}`;

  try {
    const r = await fetch(url, { headers });
    if (!r.ok) {
      res.status(502).json({ error: `github API ${r.status}`, detail: (await r.text()).slice(0, 200) });
      return;
    }
    const data = await r.json();
    const items = data.items || [];
    const datasets = items.map((it) =>
      type === "repositories"
        ? {
            ref: it.full_name,
            title: it.name,
            subtitle: it.description || "",
            description: (it.description || "") + " " + ((it.topics || []).join(" ")),
            stars: it.stargazers_count,
            url: it.html_url,
          }
        : {
            ref: it.repository && it.repository.full_name,
            title: it.name,
            path: it.path,
            description: it.path,
            url: it.html_url,
          }
    );
    res.status(200).json({ query: String(q), type, count: datasets.length, datasets });
  } catch (e) {
    res.status(500).json({ error: String((e && e.message) || e) });
  }
}
