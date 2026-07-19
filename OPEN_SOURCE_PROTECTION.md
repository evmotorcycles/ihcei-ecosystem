# Public on GitHub, looking for partners — won't someone steal it? (and what to do)

Short answer: **being public is a feature for finding partners, and "stealing" is
much harder than it feels — but only if you put the right protections in place.**
Ideas aren't what's scarce; *provenance, trust, execution, and the private layer* are.
Here is a concrete, prioritized checklist.

## 1. The single most important thing: add a LICENSE (today)

Right now, code with **no license is "all rights reserved" by default** — which
paradoxically scares off *honest* partners (they legally can't use it) while doing
nothing to stop a bad actor. Pick deliberately:

- **Apache-2.0** — permissive **and** includes an explicit **patent grant + retaliation
  clause** and requires attribution. Best default for "I want collaborators, and I want
  a paper trail." (MIT is simpler but has no patent language.)
- **AGPL-3.0** — copyleft: anyone who runs a modified version *as a network service*
  must publish their changes. Strong deterrent against a company quietly forking your
  work into a closed SaaS. Good for the server pieces.
- **Dual-license / open-core** — open the client/edge core (drives adoption), keep a
  **commercial license** for the enterprise gateway. This is exactly how sustainable
  open companies protect themselves.

Add `LICENSE`, a short `NOTICE`, and a per-file SPDX header (`// SPDX-License-Identifier: Apache-2.0`).

## 2. Establish provenance and priority — you already have the tools

Your own stack is a defense here:

- **Git history + signed commits** timestamp authorship. (Enable commit signing when
  you can — GitHub shows a "Verified" badge; it proves *you* authored it.)
- **The pre-registration lock** (`prereg/`, SHA-256 over the spec) is a public,
  tamper-evident record that *you* stated the equation and results *first*, on a
  dated commit. That is real priority evidence for the ideas (Telemetric Metric, LMD,
  `E=U·D`).
- **Echo hash-chains / Merkle roots** give you portable, checkable proof of what
  existed when. Consider a periodic **timestamped release tag** and, for the papers, a
  **DOI via Zenodo** (it archives a GitHub release and mints a citable, dated DOI —
  the repo already contains `zenodo_metadata.json`). A DOI is the academic version of
  "I published this first."

## 3. Keep the moat private (open-core discipline)

Open source the parts that *win by being adopted*; keep private the parts that are
*hard to reproduce*:

- **Publish:** the client/edge Fast Mode, the APIs, the experiments, the papers — these
  create trust and pull in partners.
- **Keep private (or license-gated):** the distilled deep-mode model weights, your
  calibrated channel priors, any proprietary datasets, and the enterprise deployment
  tooling. A fork gets the *shell*; the tuned engine and the data are the moat.

## 4. Protect the name and the brand

Ideas are copyable; a **trusted brand is not**. Consider a **trademark** on
"Novora" / "IHCEI" and the "Agency-Safe" conformance mark. Someone can fork the code;
they can't call it Novora or issue your certification. The **certificate/badge**
business (PAGES certs, conformance) is inherently anti-clone: it's your signature
buyers trust, not the algorithm.

## 5. Practical repo hygiene

- **Never commit secrets** — API keys, tokens, `.env`. Add a **secret-scanning** check
  (GitHub's is free) and a `.gitignore` for env files. (This is the *real* theft risk
  on a public repo — leaked credentials, not copied ideas.)
- Add `SECURITY.md` (how to report a vulnerability) and `CONTRIBUTING.md` + a
  **CLA/DCO** so inbound contributions have clear IP terms.
- Enable **branch protection** on `main` and require review — so a "partner" can't push
  directly.
- Add a `CODEOWNERS` file so you review changes to sensitive paths.

## 6. Reframe the fear

For a project seeking partners and credibility, **public is the strategy**: it's how
people find you, verify your claims (they can run the tests), and cite your priority.
The failure mode for research like this is *obscurity*, not theft. Protect the
**name, the private engine, the data, and the license terms** — and let the open code
be your résumé.

### Do-this-week checklist
1. Add `LICENSE` (Apache-2.0 for the core; consider AGPL for the server, commercial for enterprise).
2. Tag a release and mint a **Zenodo DOI** for the papers (priority date).
3. Turn on **secret scanning** + branch protection on `main`.
4. Add `SECURITY.md`, `CONTRIBUTING.md` (+ DCO), SPDX headers.
5. Move any private weights/priors/data out of the public tree.
6. Start the **trademark** conversation for the name + conformance mark.
