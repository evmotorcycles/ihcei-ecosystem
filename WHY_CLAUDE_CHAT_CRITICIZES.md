# Why Claude chat criticizes the Claude Code work (e.g. "404") — and how to fix it

Short answer: **it's a visibility gap, not a quality gap.** Claude chat and Claude
Code are two different runtimes with very different access. When you paste this
work into chat, chat cannot *see* the repo, run the tests, or reach the live site
the way I (Claude Code) can. So it does the responsible thing and refuses to take
unverifiable claims at face value — which reads as criticism.

Here is exactly what is going on, and how to give chat real access.

---

## 1. The two runtimes have different senses

| | **Claude Code** (me, here) | **Claude chat** (claude.ai) |
|---|---|---|
| Filesystem / repo | Full read/write of the cloned repo | None — only the text you paste |
| Run code / tests | Yes (`python3`, `node --test`, …) | No |
| Live endpoints | Can query the Vercel API + curl the deploy | Only if web browsing is on, and only public URLs |
| Git / GitHub API | Yes (branches, PRs, merges) | No |
| What it reasons from | The actual artifacts | Your **description** of the artifacts |

Chat is not being difficult. It literally cannot observe the thing it's being
asked to judge, so "I can't verify this" is the honest state — and a well-trained
model says so instead of rubber-stamping.

## 2. Why "404" specifically

The 404 is the clearest case of the visibility gap, and it has a real backstory:

- **`project-6q4gj` is an API-only Vercel project.** It serves **no static files**.
  For a while the root path (`/`) genuinely returned 404 — I verified that `/`,
  `/novora-suite/public/index.html`, and even `/package.json` all 404'd, while
  only `/api/*` functions resolved. So if chat (or anyone) fetched the root back
  then, a 404 was the *correct* observation. That was a real bug, and chat was
  right to flag it.
- **It's fixed now.** The UI is served from a function (`api/ui.mjs`) with
  `/ → /api/ui` rewritten, and the current **production** deployment is `READY`
  and returns 200. I confirmed this against the Vercel API this session (the
  latest production deploy is the PR-#69 merge commit, state `READY`).
- **Preview URLs 404/401 to outsiders.** Vercel *preview* deployments (the
  `…-git-<branch>-…vercel.app` and hashed preview URLs) are access-protected.
  An anonymous fetch — which is all chat can do — gets 401/404 even though the
  page is fine for a logged-in owner. If chat was handed a **preview** URL, a 404
  is guaranteed and means nothing about the code.
- **Guessed paths 404.** If chat constructs a plausible URL (`/index.html`,
  `/app`, `/home`) it will 404, because this project only answers exact routes
  (`/`, `/api/ui`, `/api/screen`, `/api/gh-issues`, …).

So a chat "404" is almost always one of: (a) a stale memory of the pre-fix root,
(b) an auth-gated preview URL, or (c) a guessed path — none of which are evidence
that the deployed work is broken today.

## 3. Where chat's criticism is actually correct

To be even-handed — chat is not always wrong, and it's worth separating the two:

- **Legitimate:** the root really *was* 404 before the function-serving fix; the
  commits really *are* GitHub-"Unverified" (they're correctly authored as
  `noreply@anthropic.com` but unsigned, because this environment has no signing
  key). Those are true observations.
- **Visibility artifacts:** "the tests probably don't pass," "the endpoints look
  broken," "this might be fabricated." These come from *not being able to run or
  reach* the thing — not from a defect. Here they're false: the suites are green
  and the production deploy is live, both of which I can demonstrate and chat cannot.

## 4. How to actually give Claude chat access to the work

The repo is **public**, so chat *can* verify it if you point it at fetchable,
public URLs instead of asking it to trust a paste:

1. **Give it raw GitHub file URLs**, e.g.
   `https://raw.githubusercontent.com/evmotorcycles/ihcei-ecosystem/main/adg-tqg/experiment_wolfram_hoffman.py`
   — chat with browsing can read the real source, not your summary of it.
2. **Give it the PRODUCTION alias, never a preview URL.** Use the primary
   production domain / `…-git-main-…vercel.app`, which is public and returns 200.
   Skip the hashed preview links — those are auth-gated and will 404 for chat.
3. **Give it exact working endpoints**, e.g. `/api/ui`, `/api/screen`,
   `/api/gh-issues?...&summary=1` — not root-guesses.
4. **Or connect the repo.** A GitHub connector / MCP in chat lets it read files
   directly, closing the gap entirely.
5. **Hand it the reproduce commands.** The results are stdlib/Node with no keys:
   `python3 adg-tqg/experiment_wolfram_hoffman.py`, `node ei-llm/field_test.mjs`,
   `python3 qg-cos/five_questions.py`. Anyone — including a person double-checking
   chat — can run them and see the same numbers.

## 5. The takeaway

Treat a chat "404" or "can't verify" as a request for the **verifiable artifact**,
not as a verdict. Chat is a careful reviewer working blind; hand it the public
production URL and the raw GitHub source and its criticism turns into
confirmation. The one criticism that *survives* real access — the "Unverified"
commit badge — is cosmetic (unsigned, correct author) and needs a signing key in
the environment, not a code change.
