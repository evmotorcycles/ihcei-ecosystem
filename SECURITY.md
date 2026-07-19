# Security Policy

## Reporting a vulnerability

Please report security issues privately — do **not** open a public issue for a
vulnerability. Email the maintainer (see the repository owner's profile) or use
GitHub's private vulnerability reporting (Security → Report a vulnerability). We aim
to acknowledge within a few days.

## Secrets

- **No secrets are committed to this repository.** All API keys and tokens are read
  from environment variables at runtime (`process.env.ANTHROPIC_API_KEY`,
  `GOVPHYS_PAT`, etc.) — never hardcoded.
- Automated **secret scanning runs in CI** on every push and pull request
  (`.github/workflows/secret-scan.yml`, gitleaks) and fails the build if a
  credential is detected, including in git history.
- Do not commit `.env` files. See `.gitignore`.

## Recommended admin settings (repository owner)

These are GitHub **Settings** toggles that only a repo admin can enable — they
complement the CI scan above:

1. **Secret scanning + push protection** — Settings → *Code security and analysis* →
   enable **Secret scanning** and **Push protection** (push protection blocks a
   commit that contains a detected secret before it lands). Free for public repos.
2. **Branch protection on `main`** — Settings → *Branches* → *Add branch ruleset* (or
   classic *Add rule*) for `main`:
   - Require a pull request before merging (≥1 approval);
   - Require status checks to pass (add `secret-scan`);
   - Block force pushes; restrict deletions;
   - (optionally) Require signed commits.
3. **CODEOWNERS review** — `.github/CODEOWNERS` routes review of sensitive paths.

## Scope

The keyless on-device core (Fast Mode, the nine-product screen) makes no network
call and holds no secret. Deep mode uses the operator's own key, supplied via the
environment; it is never stored in the repo.
