// api/kaggle-search.js
// Server-side Kaggle dataset search for the LISM dataset sweep. Vercel egress is
// not scope-bound, so this can reach the Kaggle API where the sandbox cannot.
//
//   GET /api/kaggle-search?q=patient+safety+incident+outcomes
//     -> { query, count, datasets: [ { ref, title, subtitle, totalBytes, url } ] }
//   GET /api/kaggle-search?health=1
//     -> { ok, keyConfigured, envVarsPresent: [names only, never values] }
//
// Credentials are resolved tolerantly (Kaggle needs BOTH a username and a key):
//   * KAGGLE_USERNAME + KAGGLE_KEY (standard)
//   * a kaggle.json blob in KAGGLE_JSON / any *kaggle* var: {"username","key"}
//   * a single *kaggle* var in "username:key" form
// so it works whatever you named the Vercel env var (e.g. Kagglekey, like the
// Congresskey var the bill-text proxy uses).

function resolveKaggle(userOverride) {
  const env = process.env;
  let user =
    userOverride || env.KAGGLE_USERNAME || env.KaggleUsername || env.kaggle_username || env.KAGGLE_USER;
  let key =
    env.KAGGLE_KEY || env.Kagglekey || env.KaggleKey || env.KAGGLEKEY || env.kaggle_key;
  let bareKey = null;

  const tryBlob = (v) => {
    if (!v) return;
    const val = String(v).trim();
    if (val.startsWith("{")) {
      try {
        const j = JSON.parse(val);
        user = user || j.username || j.user;
        key = key || j.key;
      } catch (e) { /* not json */ }
    } else if (val.includes(":")) {
      const idx = val.indexOf(":");
      user = user || val.slice(0, idx);
      key = key || val.slice(idx + 1);
    } else {
      bareKey = bareKey || val; // a lone token: assume it is the API key
    }
  };

  tryBlob(env.KAGGLE_JSON || env.KaggleJson || env.KAGGLE_CREDENTIALS || env.Kagglejson);
  for (const [k, v] of Object.entries(env)) {
    if (/kaggle/i.test(k)) tryBlob(v);
    if (user && key) break;
  }
  if (!key && bareKey) key = bareKey; // key from a lone *kaggle* token
  return { user, key };
}

export default async function handler(req, res) {
  const { user, key } = resolveKaggle(req.query.user);

  if (req.query.health) {
    const envVarsPresent = Object.keys(process.env).filter((k) => /kaggle/i.test(k));
    res.status(200).json({
      ok: true,
      keyConfigured: Boolean(user && key),
      keyResolved: Boolean(key),
      userResolved: Boolean(user),
      envVarsPresent,
      note: "Kaggle needs username + key; pass ?user=<kaggle_username> if only the key is in env",
    });
    return;
  }
  if (!key) {
    res.status(500).json({ error: "Kaggle API key not resolvable from env" });
    return;
  }
  if (!user) {
    res.status(400).json({ error: "Kaggle username required: pass ?user=<kaggle_username> (key is in env)" });
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
