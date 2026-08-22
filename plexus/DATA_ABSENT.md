# DATA_ABSENT — the stablecoin substrate test

Answer to "do we have the reserve attestation data and minute-by-minute price
data for May 2022 and March 2023 in the container, or can we fetch it?"

**No, on both halves — and there is a worse problem than the data.**

## 1. What is blocked, exactly

Checked, not recalled. The proxy logged each refusal itself:

| Artifact | Status |
|---|---|
| Any stablecoin or crypto price series in-container | **absent.** No file matching stablecoin, usdc, usdt, depeg, crypto, price, ohlc anywhere in the tree. |
| `api.coingecko.com` | **403 to CONNECT** — policy denial |
| `api.coinpaprika.com` | **403 to CONNECT** |
| `api.llama.fi` | **403 to CONNECT** |
| `data.messari.io` | **403 to CONNECT** |
| `raw.githubusercontent.com` | **200, serves content.** GitHub-hosted data *is* reachable. |

So minute-level price data is not fetchable from any market API here. A dataset
committed to a public GitHub repository would be reachable — that route is open.

**The reserve attestation half is harder and is not a network problem.**
Attestation reports published before each shock are PDFs on issuer websites
(Circle, Tether, Paxos, and others). They are not an API, they are not in this
container, and several have been revised or withdrawn since. The independent
variable cannot be constructed from anything reachable here.

## 2. The worse problem: this cannot be pre-registered by me

**I already know what happened in May 2022 and March 2023.** UST collapsed. USDC
traded to roughly $0.87 on 11 March 2023 when Silicon Valley Bank failed. Those
outcomes are in my training data and in your memory.

A pre-registration written now, by either of us, about those two shocks, is a
**retrodiction wearing a pre-registration's clothes**. The margins — 20% shallower
drawdown, 50% faster recovery — read as though chosen in advance, and they cannot
have been. Every other locked file in this repository was hashed before its data
existed. This one cannot be, and pretending otherwise would corrupt the only
thing that makes the others worth anything.

Two honest routes remain, and they are different studies:

- **Retrospective, and labelled so.** Run it, state plainly that the analyst knew
  the outcomes, and treat the result as a consistency check rather than a test.
  Blind-coding the reserve categories helps but does not fix it.
- **Prospective, locked now, run at the next shock.** See
  `substrate_preregistration.md`. Unrun, and it stays unrun until a shock nobody
  has seen yet.

## 3. And the claim may already be falsified by its own best case

The flagship Category A asset — 100% cash and treasuries, exactly ΔU = 0 — is
USDC. **USDC is the one that broke in March 2023.** Not because its reserves were
fractional; they were not. Because a large share of them sat in one bank, and
that bank failed.

That is the shape this repository has now met seven times. *Fully reserved* says
nothing about **how many independent places the reserve is held**. One custodian
is one origin, and everything hanging off it goes when it goes.

So the substrate variable may be mis-specified. The press is not

> bedrock versus liquefiable sand

but

> one pier sunk into bedrock versus several piers sunk into bedrock

A pier on bedrock is still one pier. `substratelib.js` carries both pictures and
audits them with the same instrument used on everybody else's, and the second one
is explicitly marked as written **after** the outcome was known.
