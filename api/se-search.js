// api/se-search.js
// Server-side Stack Exchange fetch for the LISM "Barakah / knowledge-propagation"
// two-hop extension. Vercel egress reaches the SE API where the sandbox proxy
// blocks it. Unauthenticated works (modest daily quota); set SE_KEY to raise it.
//
//   GET /api/se-search?site=stackoverflow&tag=python&pages=3&pagesize=100
//     -> { site, tag, count, questions: [ {id, score, answer_count, view_count,
//           is_answered, accepted, closed, reputation, creation_date, tags} ] }
//   GET /api/se-search?health=1  -> { ok, keyConfigured }
//
// Fields map to the two-hop model:
//   D_enc (sincere seeking / query fidelity)  <- question quality (score, answered)
//   D_dec (selflessness / onward transmission) <- community answering (answer_count, accepted)
//   E     (Barakah / downstream reuse)         <- view_count (compounding attention)
//   U     (capacity)                           <- asker reputation

export default async function handler(req, res) {
  const key = process.env.SE_KEY || process.env.STACKEXCHANGE_KEY || null;
  if (req.query.health) {
    res.status(200).json({ ok: true, keyConfigured: Boolean(key) });
    return;
  }
  const site = req.query.site || "stackoverflow";
  const tag = req.query.tag || null;
  const pages = Math.min(Math.max(parseInt(req.query.pages || "3", 10) || 3, 1), 10);
  const pagesize = Math.min(Math.max(parseInt(req.query.pagesize || "100", 10) || 100, 1), 100);
  // filter includes accepted_answer_id + closed_date + owner.reputation
  const filter = "!nNPvSNVZBz"; // withbody off; adds accepted_answer_id, closed_date
  const out = [];
  try {
    for (let page = 1; page <= pages; page++) {
      const params = new URLSearchParams({
        site, page: String(page), pagesize: String(pagesize),
        order: "desc", sort: "creation", filter,
      });
      if (tag) params.set("tagged", tag);
      if (key) params.set("key", key);
      const url = `https://api.stackexchange.com/2.3/questions?${params.toString()}`;
      const r = await fetch(url);
      if (!r.ok) {
        res.status(502).json({ error: `SE API ${r.status}`, detail: (await r.text()).slice(0, 200) });
        return;
      }
      const data = await r.json();
      for (const q of (data.items || [])) {
        out.push({
          id: q.question_id,
          score: q.score,
          answer_count: q.answer_count,
          view_count: q.view_count,
          is_answered: q.is_answered ? 1 : 0,
          accepted: q.accepted_answer_id ? 1 : 0,
          closed: q.closed_date ? 1 : 0,
          reputation: (q.owner && q.owner.reputation) || 0,
          creation_date: q.creation_date,
          tags: q.tags || [],
        });
      }
      if (!data.has_more) break;
      if (data.backoff) await new Promise((s) => setTimeout(s, (data.backoff + 1) * 1000));
    }
    res.status(200).json({ site, tag, count: out.length, questions: out });
  } catch (e) {
    res.status(500).json({ error: String((e && e.message) || e) });
  }
}
