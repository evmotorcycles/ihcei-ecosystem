# Deploying the Novora ecosystem beyond Vercel

**Yes — the ecosystem is not locked to Vercel.** The architecture that makes it $0
to run is exactly what makes it portable: the core is **keyless, on-device / pure
in-process math** (Node + Python, no upstream model call for the free tier). Nothing
about it depends on Vercel-specific services. Anywhere that can serve a static page
and/or run a small serverless function will host it.

## What actually has to run

| Piece | What it needs | Portable? |
|---|---|---|
| The suite UI (`novora-suite/public/index.html`) | static file hosting | trivially — any static host |
| `/api/screen`, `/api/ui`, `/api/govern` (keyless `$0`) | a Node serverless/edge function | any FaaS/edge runtime |
| `/api/gh-issues`, `/api/gh-proxy` (public GitHub reads) | outbound HTTPS | any host with network egress |
| Deep mode (optional, paid) | the user's own model key, or on-device | provider-agnostic |

Because the free tier makes **no upstream paid call**, the only "backend" is a few
small functions doing arithmetic — the easiest thing in the world to relocate.

## Drop-in alternatives (keyless free tiers)

- **Netlify** — Netlify Functions (Node). Move `api/*.mjs` to `netlify/functions/`,
  add a `[[redirects]]` for `/` → the UI function. Same $0 model.
- **Cloudflare Pages + Workers** — static UI on Pages, the endpoints as Workers.
  Global edge, generous free tier; ideal for the on-device/edge ethos. (Workers use
  the Web `fetch` handler; the pure-math handlers port with a thin adapter.)
- **Deno Deploy** — the `.mjs` handlers run with minimal change; global edge, free
  tier, no build step.
- **GitHub Pages / any static CDN** — for a **fully static** build: since Fast Mode
  is pure client-side-capable math, the screen logic can run **entirely in the
  browser** (import `fastmode.mjs` client-side), so you can ship the whole free
  product as a static site with *no server at all*. This is the most robust, most
  portable, and cheapest option.
- **Render / Railway / Fly.io** — run it as a tiny Node service or a Docker
  container (`docker-compose` already exists in the ecosystem tree). Best when you
  want a long-lived process or to co-locate the Python experiments.
- **Self-host (Docker / a VPS / on-prem VPC)** — the B2B story: ship the gateway as
  a container the client runs inside their own VPC. Your hosting cost stays $0; they
  supply hardware and their own keys.

## Recommended by goal

- **Cheapest, most durable, most on-brand:** static build on **Cloudflare Pages** or
  **GitHub Pages**, Fast Mode running in the browser — no server, no keys, no vendor
  lock-in.
- **Same shape as today with functions:** **Netlify** or **Deno Deploy** — near
  drop-in for the current `api/*.mjs`.
- **Enterprise / regulated:** **Docker self-host** in the client VPC.

## Migration is small

1. Copy `novora-suite/public/` (static) + `api/*.mjs` (functions).
2. Add the host's routing rule for `/ → /api/ui` (or serve the UI statically and
   point it at the screen endpoint).
3. No secrets to configure for the free tier — it's keyless by design.
4. Optional: for the fully-static route, import `novora-suite/engine/fastmode.mjs`
   in the browser and drop the functions entirely.

**Bottom line:** Vercel is a convenience, not a dependency. The keyless, on-device
core means the Novora ecosystem can be deployed on Netlify, Cloudflare, Deno,
GitHub Pages, Render, Fly, or a self-hosted Docker box — and in the static-build
case, with no backend at all.
