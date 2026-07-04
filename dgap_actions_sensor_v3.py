#!/usr/bin/env python3
"""
NERE D_gap Sensor — Actions Workflow (v3.1, Human-Primary, Stratified)
======================================================================
>>> THIS DOCSTRING IS THE PRE-REGISTRATION. Commit the SHA-256 printed at
>>> startup BEFORE triggering the fetch. Do not edit after.

SAMPLE STATUS: microsoft/vscode (pages 1-39, fetched 2026-07-04) is the
DISCOVERY sample; its human-only result (coef +2.12, p = 0.074) was observed
exploratorily and is NOT confirmatory. This spec is registered for
CONFIRMATION on data unseen at registration time: a different repository
(default kubernetes/kubernetes) or vscode pages >= 51.

UNIT OF ANALYSIS: one closed pull request with non-empty body text.

OUTCOME E: E=0 if not merged, OR 'revert' in any label, OR 'revert' in the
first 50 chars of the pressed body; else E=1.

AUTHOR STRATIFICATION (locked, from API ground truth):
    is_bot       = (user.type == 'Bot') OR (user.login == 'Copilot')
    is_dependabot = 'dependabot' in user.login (lowercased)
    is_llm_agent  = login == 'Copilot' or login contains 'copilot'

PRIMARY ANALYSIS (pre-registered): human cohort only (is_bot == False).
    Text: pressed via press_template_noise (strip HTML comments <!-- -->,
    markdown checklist lines - / * [ ]/[x], Testing/Verification headers).
    D_enc/D_dec = locked regex counts, MinMax-scaled WITHIN the human cohort.
    D_gap = D_enc - D_dec. Channel gate: VIF < 5.0 else INCONCLUSIVE.
    Logit( E==0 ~ const + D_gap ).
    VALIDATED iff p < 0.05 AND coef > 0. Minimum cohort: N >= 500 with
    >= 50 failure events, else UNDERPOWERED (reported, not interpreted).

SECONDARY (descriptive/exploratory, reported regardless of outcome):
    (a) bot cohort regression, scaled within-cohort;
    (b) dependabot-only and llm-agent-only descriptives;
    (c) unpressed-text robustness re-run of the primary.
No other specifications will be run on this fetch.
"""
import hashlib, json, re, sys, time, os
import requests
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import MinMaxScaler

SPEC_HASH = hashlib.sha256(__doc__.encode()).hexdigest()
print(f"SPEC SHA-256: {SPEC_HASH}", file=sys.stderr)

GITHUB_TOKEN = os.environ.get("GOVPHYS_PAT") or os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("TARGET_OWNER", "kubernetes")
REPO = os.environ.get("TARGET_REPO", "kubernetes")
MAX_PAGES = int(os.environ.get("MAX_PAGES", 50))
START_PAGE = int(os.environ.get("START_PAGE", 1))  # use 51 for vscode holdout

if not GITHUB_TOKEN:
    print("ERROR: GOVPHYS_PAT / GITHUB_TOKEN not set.", file=sys.stderr)
    sys.exit(1)

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}",
           "Accept": "application/vnd.github.v3+json"}

enc_patterns = [r'architecture', r'dependency', r'specification', r'refactor',
                r'memory', r'race condition', r'throughput', r'latency',
                r'pointer', r'algorithm']
dec_patterns = [r'unit test', r'e2e', r'coverage', r'rollback',
                r'ci/cd', r'assert', r'integration', r'mock', r'fixture']

def press_template_noise(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)          # HTML comments
    text = re.sub(r'(?m)^\s*[-*]\s*\[[ xX]\]\s*.*$', '', text)       # checklists
    text = re.sub(r'(?im)^#+\s*(testing|how (was|is) this tested\??|verification|test plan)\s*$',
                  '', text)                                           # template headers
    return text

def score_text(text, patterns):
    if not text:
        return 0
    return sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)

def compute_vif(d_enc, d_dec):
    if np.std(d_enc) == 0 or np.std(d_dec) == 0:
        return float('inf')
    r = np.corrcoef(d_enc, d_dec)[0, 1]
    if r**2 >= 1.0:
        return float('inf')
    return 1.0 / (1.0 - r**2)

def run_cohort(df_sub, text_col):
    """Scale WITHIN cohort, gate, regress. Returns result dict."""
    n, n_fail = len(df_sub), int((df_sub['outcome'] == 0).sum())
    res = {"n": n, "failures_E0": n_fail}
    if n < 500 or n_fail < 50:
        res["status"] = "UNDERPOWERED (pre-registered minimum not met)"
    if n < 10 or df_sub['outcome'].nunique() < 2:
        res["status"] = "INSUFFICIENT_DATA"
        return res
    d = df_sub.copy()
    d['De'] = d[text_col].apply(lambda x: score_text(x, enc_patterns))
    d['Dd'] = d[text_col].apply(lambda x: score_text(x, dec_patterns))
    d[['De_s', 'Dd_s']] = MinMaxScaler().fit_transform(d[['De', 'Dd']])
    d['D_gap'] = d['De_s'] - d['Dd_s']
    vif = compute_vif(d['De_s'], d['Dd_s'])
    res["vif"] = round(vif, 4)
    if vif >= 5.0:
        res["status"] = "INCONCLUSIVE_CHANNEL_COLLAPSE"
        return res
    y = (d['outcome'] == 0).astype(int)
    try:
        m = sm.Logit(y, sm.add_constant(d['D_gap'])).fit(disp=0)
        p, coef = float(m.pvalues['D_gap']), float(m.params['D_gap'])
        lo, hi = m.conf_int().loc['D_gap']
        if p < 0.05 and coef > 0:
            verdict = "[SENSOR VALIDATED]: High D_gap predicts rejection."
        elif p < 0.05 and coef < 0:
            verdict = "[SENSOR INVERTED]: D_gap predicts successful merges."
        else:
            verdict = "[NO SIGNAL]"
        res.update({"d_gap_coefficient": round(coef, 4),
                    "ci_95": [round(float(lo), 4), round(float(hi), 4)],
                    "p_value": round(p, 5), "verdict": verdict,
                    "mean_D_gap_E0": round(float(d.loc[d['outcome'] == 0, 'D_gap'].mean()), 5),
                    "mean_D_gap_E1": round(float(d.loc[d['outcome'] == 1, 'D_gap'].mean()), 5)})
    except Exception as e:
        res["error"] = f"Model failed to converge: {e}"
    return res

# ---- FETCH ----
print(f"── NERE v3.1 ── {OWNER}/{REPO} pages {START_PAGE}-{START_PAGE+MAX_PAGES-1}",
      file=sys.stderr)
prs = []
fetch_error = None
for page in range(START_PAGE, START_PAGE + MAX_PAGES):
    url = (f"https://api.github.com/repos/{OWNER}/{REPO}/pulls"
           f"?state=closed&per_page=100&page={page}")
    data = None
    for attempt in range(6):
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            break
        if r.status_code == 403 and 'rate limit' in r.text.lower():
            reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
            time.sleep(max(reset - int(time.time()), 1))
        else:
            time.sleep(3)
    if data is None:
        fetch_error = f"page {page}: HTTP {r.status_code}"  # truncation is recorded, not silent
        break
    if not data:
        break
    print(f"page {page}: {len(data)} PRs", file=sys.stderr)
    for item in data:
        raw = item.get('body')
        user = item.get('user') or {}
        if raw:
            prs.append({'id': item['number'],
                        'text_raw': raw,
                        'text_pressed': press_template_noise(raw),
                        'merged_at': item.get('merged_at'),
                        'user': user.get('login', ''),
                        'user_type': user.get('type', ''),
                        'labels': [l['name'] for l in item.get('labels', [])]})
    time.sleep(0.3)

if not prs:
    print(json.dumps({"error": "No usable PRs.", "fetch_error": fetch_error}))
    sys.exit(1)

df = pd.DataFrame(prs).drop_duplicates(subset='id')

def define_outcome(row):
    if pd.isna(row['merged_at']):
        return 0
    if any('revert' in l.lower() for l in row['labels']) \
       or 'revert' in str(row['text_pressed']).lower()[:50]:
        return 0
    return 1

df['outcome'] = df.apply(define_outcome, axis=1)

login_lc = df['user'].astype(str).str.lower()
df['is_bot'] = (df['user_type'] == 'Bot') | (login_lc == 'copilot')
df['is_dependabot'] = login_lc.str.contains('dependabot', na=False)
df['is_llm_agent'] = login_lc.str.contains('copilot', na=False)

humans, bots = df[~df['is_bot']], df[df['is_bot']]

out = {"spec_sha256": SPEC_HASH,
       "repository": f"{OWNER}/{REPO}",
       "pages": f"{START_PAGE}-{START_PAGE + MAX_PAGES - 1}",
       "fetch_error": fetch_error,
       "telemetry_stats": {"total_usable_prs": len(df),
                           "humans_n": len(humans), "bots_n": len(bots),
                           "dependabot_n": int(df['is_dependabot'].sum()),
                           "llm_agent_n": int(df['is_llm_agent'].sum())},
       "PRIMARY_human_pressed": run_cohort(humans, 'text_pressed'),
       "secondary_bot_pressed": run_cohort(bots, 'text_pressed'),
       "robustness_human_unpressed": run_cohort(humans, 'text_raw'),
       "descriptive_dependabot": {
           "n": int(df['is_dependabot'].sum()),
           "failure_rate": round(float((df[df['is_dependabot']]['outcome'] == 0).mean()), 4)
           if df['is_dependabot'].any() else None},
       "descriptive_llm_agent": {
           "n": int(df['is_llm_agent'].sum()),
           "failure_rate": round(float((df[df['is_llm_agent']]['outcome'] == 0).mean()), 4)
           if df['is_llm_agent'].any() else None}}

df.drop(columns=['text_raw']).to_csv('dgap_stratified_results.csv', index=False)
print(json.dumps(out, indent=2))
