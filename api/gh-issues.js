// api/gh-issues.js
// Server-side GitHub issue-timeline fetch for a thorough, live validation of the
// enforcement-latency sensor (tau_v). Returns each repo's lifecycle label inputs
// (archived, pushed_at, stars) plus its non-PR issues' open/close timestamps, so
// tau_v = mean issue-close latency can be computed and failed-vs-surviving repos
// compared exactly as in the manuscript's Third Law.
//
//   GET /api/gh-issues?repo=pallets/flask&pages=3
//     -> { repo, archived, pushed_at, stargazers, open_issues,
//          issues: [ { created_at, closed_at } ] }   // PRs excluded
//   GET /api/gh-issues?health=1  -> { ok, tokenConfigured }
//
// Env: GOVPHYS_PAT / GITHUB_TOKEN (unauth works but is rate-limited).

async function gh(url, token) {
  const headers = { Accept: "application/vnd.github+json", "User-Agent": "ihcei-tauv" };
  if (token) headers.Authorization = `token ${token}`;
  const r = await fetch(url, { headers });
  return r;
}

export default async function handler(req, res) {
  const token = process.env.GOVPHYS_PAT || process.env.GITHUB_TOKEN || null;
  if (req.query.health) {
    res.status(200).json({ ok: true, tokenConfigured: Boolean(token) });
    return;
  }
  const repo = req.query.repo;
  if (!repo || !/^[^/]+\/[^/]+$/.test(repo)) {
    res.status(400).json({ error: "missing/invalid ?repo=owner/name" });
    return;
  }
  const pages = Math.min(Math.max(parseInt(req.query.pages || "3", 10) || 3, 1), 10);
  try {
    const meta = await gh(`https://api.github.com/repos/${repo}`, token);
    if (!meta.ok) {
      res.status(502).json({ error: `repo meta ${meta.status}`, detail: (await meta.text()).slice(0, 160) });
      return;
    }
    const m = await meta.json();
    const issues = [];
    for (let page = 1; page <= pages; page++) {
      const r = await gh(
        `https://api.github.com/repos/${repo}/issues?state=all&per_page=100&page=${page}&sort=created&direction=desc`,
        token
      );
      if (!r.ok) {
        res.status(502).json({ error: `issues ${r.status}`, detail: (await r.text()).slice(0, 160) });
        return;
      }
      const arr = await r.json();
      for (const it of arr) {
        if (it.pull_request) continue; // exclude PRs (Third Law: closed non-PR issues)
        issues.push({ created_at: it.created_at, closed_at: it.closed_at });
      }
      if (arr.length < 100) break;
    }
    res.status(200).json({
      repo,
      archived: Boolean(m.archived),
      pushed_at: m.pushed_at,
      stargazers: m.stargazers_count,
      open_issues: m.open_issues_count,
      n_issues_fetched: issues.length,
      issues,
    });
  } catch (e) {
    res.status(500).json({ error: String((e && e.message) || e) });
  }
}
