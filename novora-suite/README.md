# Novora Suite — the product

Novora is the **product**; IHCEI (`../ihcei_v3/`, `../api/govern.js`) is the
**infrastructure** it sits on. This folder is a self-contained, deployable unit:
the nine-product consumer governance suite on a secure serverless backend.

```
novora-suite/
  public/index.html   nine products (PAGES PULSE WEIGH LENS VOICE MARK STAND BRIDGE RISE)
  api/analyse.js      secure server-side inference (key + model never reach the browser)
  vercel.json         static public/ + /api serverless functions
  package.json        ESM
```

## What changed from the uploaded prototype

The prototype (`novora_final.html`) called `api.anthropic.com` **directly from
the browser**, which exposes the API key to anyone who opens dev tools — the
deployment guide flagged this as the pre-launch security fix. This build does
the fix:

- The UI now POSTs `{text, system}` to **`/api/analyse`**; the key and the model
  live server-side and are never sent to the client.
- Model is **`claude-sonnet-5`** (was `claude-sonnet-4-20250514`, which is
  deprecated and retires 2026-06-15). Sonnet 5 is the current Sonnet tier —
  near-Opus quality on this analysis/extraction workload, priced for consumer
  volume ($3/$15 per MTok; intro $2/$10 through 2026-08-31). Override with the
  `NOVORA_MODEL` env var.
- Input length cap (8 KB) and a **best-effort per-IP daily free cap**
  (`NOVORA_FREE_PER_DAY`, default 5) are enforced in `api/analyse.js`.

## Deploy (Vercel)

```bash
cd novora-suite
npm i -g vercel && vercel --prod          # or drag the folder into vercel.com
```

Then in the Vercel project: **Settings → Environment Variables →**
`ANTHROPIC_API_KEY = sk-ant-...` → Redeploy. The engine is live.

Smoke test:

```bash
curl -s https://YOUR-APP.vercel.app/api/analyse -X POST \
  -H 'Content-Type: application/json' \
  -d '{"text":"Everyone agrees you must act immediately, do not question it.","system":"Return ONLY JSON: {\"score\":0-1,\"verdict\":\"...\",\"analysis\":\"...\"}"}'
```

## Known limitations (be honest before launch)

1. **The Anthropic account must have credit.** With a zero-balance key every
   analysis returns HTTP 400 `Your credit balance is too low` — the product is
   dead until the account is funded. (This is the same block documented in
   `../ihcei_v3/EXPERIMENT_REPORT.md` §5b.)
2. **The rate limit is best-effort, not a hard quota.** Serverless instances are
   ephemeral and don't share the in-memory counter, so a determined caller can
   exceed the free cap. Wire **Vercel KV** or **Upstash Redis** keyed by IP (or
   by authenticated user) before the free tier is worth abusing.
3. **No auth / no Stripe / no certificate storage yet.** For Pro tiers, add an
   auth layer, Stripe Checkout, and a store (Supabase) for certificate history —
   these are the Layer-1 monetization pieces in `../REVENUE_ARCHITECTURE.md`.

## Relationship to IHCEI

The nine products are consumer surfaces; the between-LLMs governance verdict
they conceptually rely on (agency delta, coercion holds, calibrated posteriors)
is the IHCEI infrastructure in this same repo. Novora is how humans touch it;
IHCEI is the probabilistic layer underneath.
