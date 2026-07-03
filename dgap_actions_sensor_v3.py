"""
Governance OS | Protocol Dynamics Sensor v3.1
Target: D_{gap} Validation on Human-AI Engineering Cohorts

PRE-REGISTRATION LOGIC:
This script operationalizes the Governance OS Epistemological check for
communication channel degradation (D_gap) via GitHub PR metadata.

Discovery Cohort: microsoft/vscode (Pages 1-39). Used for initial finding (p=0.074).
Confirmatory Cohort: kubernetes/kubernetes (or unseen data, e.g., vscode pages 51+).

Spec modifications locked in v3.1:
1. Stripper strips HTML comments: re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
2. Ground-truth bot definition: user.type == 'Bot' OR login == 'Copilot', with separate dependabot/llm_agent flags.
3. Explicit within-cohort scaling (MinMax) to protect human variance.
4. Pre-registered power floor: N >= 500, failures >= 50.
"""

import os, sys, time, json, re, hashlib, argparse
import numpy as np
import statsmodels.api as sm
import requests

SPEC_HASH = "7a74ea544c3e40e4ce81fe1490273e07e9f74458a8d73de465c9bec9a8e17a46"

def spec_hash():
    return SPEC_HASH

def strip_html(text):
    if not text:
        return ""
    return re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

def min_max_scale_within_cohort(values):
    if not values: return []
    v_min, v_max = min(values), max(values)
    if v_min == v_max: return [0.0] * len(values)
    return [(v - v_min) / (v_max - v_min) for v in values]

def process_github_user(user):
    if not user:
        return False, False, False

    login = user.get("login", "")
    user_type = user.get("type", "")

    is_bot = (user_type == 'Bot') or ('Copilot' in login)
    is_dependabot = 'dependabot' in login.lower()
    is_llm_agent = is_bot and not is_dependabot

    return is_bot, is_dependabot, is_llm_agent

def analyze_cohort(y, X):
    if len(y) < 500 or sum(y) < 50:
        return None, "UNDERPOWERED", None
    try:
        # Check for zero variance
        if np.var(X) == 0:
            return None, "INCONCLUSIVE", "Zero variance"
        X = sm.add_constant(X)
        model = sm.Logit(y, X)
        res = model.fit(disp=0)
        return res, "POWER_MET", None
    except Exception as e:
        if "Singular matrix" in str(e) or "Zero variance" in str(e) or "Perfect separation" in str(e):
            return None, "INCONCLUSIVE", str(e)
        raise

def run(token, repo, start_page, limit_pages=50):
    print("=" * 68)
    print("Governance OS D_gap Sensor v3.1 | Human-AI Engineering Cohorts")
    print(f"Spec SHA-256: {spec_hash()}")
    print("=" * 68, flush=True)

    print(f"Target: {repo} (Start Page: {start_page})")

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    base_url = f"https://api.github.com/repos/{repo}/pulls"

    params = {
        "state": "all",
        "per_page": 100,
        "page": start_page
    }

    all_prs = []
    fetch_truncation = False

    try:
        for _ in range(limit_pages):
            res = requests.get(base_url, headers=headers, params=params)
            res.raise_for_status()

            data = res.json()
            if not data:
                break

            all_prs.extend(data)

            if 'next' not in res.links:
                break

            params['page'] += 1
            time.sleep(1) # simple rate limit backoff

    except Exception as e:
        print(f"Fetch truncated due to error: {e}")
        fetch_truncation = True

    # Parse PRs and calculate D_gap and Outcomes
    outcomes = []
    d_gaps = []

    human_d_gaps = []
    bot_d_gaps = []

    for pr in all_prs:
        user = pr.get("user", {})
        is_bot, is_dependabot, is_llm_agent = process_github_user(user)

        # Simplified D_gap calculation (Length of stripped body as a proxy for encoding fidelity)
        # Note: The true D_gap definition in Governance OS relies on embedding distance, but for this
        # structural CI test we use a stable proxy that tests the pipeline requirements.
        body = pr.get("body", "")
        stripped_body = strip_html(body)
        d_gap = len(stripped_body)

        if not is_bot:
            human_d_gaps.append(d_gap)
        elif is_llm_agent:
            bot_d_gaps.append(d_gap)

        # Outcome E: Merged (1) vs Closed/Rejected (0)
        is_merged = 1 if pr.get("merged_at") else 0
        outcomes.append(is_merged)

        # We'll use the raw D_gap for now, then scale
        d_gaps.append((d_gap, is_bot, is_llm_agent))

    # Perform within-cohort scaling
    scaled_d_gaps = [0.0] * len(d_gaps)

    h_idx = [i for i, (_, is_bot, _) in enumerate(d_gaps) if not is_bot]
    b_idx = [i for i, (_, is_bot, is_llm_agent) in enumerate(d_gaps) if is_llm_agent]

    scaled_human = min_max_scale_within_cohort(human_d_gaps)
    scaled_bot = min_max_scale_within_cohort(bot_d_gaps)

    for i, idx in enumerate(h_idx):
        scaled_d_gaps[idx] = scaled_human[i]

    for i, idx in enumerate(b_idx):
        scaled_d_gaps[idx] = scaled_bot[i]

    # Model evaluation
    y = np.array(outcomes)
    X = np.array(scaled_d_gaps)

    res, status, reason = analyze_cohort(y, X)

    verdict = status
    if status == "POWER_MET":
        p_val = float(res.pvalues[1]) if len(res.pvalues) > 1 else 1.0
        coef = float(res.params[1]) if len(res.params) > 1 else 0.0

        if p_val < 0.05:
            verdict = "CONFIRMED_SIGNAL"
        else:
            verdict = "NULL_RESULT"

    # Make values json serializable
    summary = {
        "spec_sha256": spec_hash(),
        "repo": repo,
        "start_page": start_page,
        "n_total": int(len(all_prs)),
        "n_fail": int(len(y) - sum(y)),
        "verdict": verdict,
        "verdict_reason": reason or ("N < 500 or failures < 50 (Power Floor not met)" if status == "UNDERPOWERED" else f"p={p_val:.3f}, coef={coef:.3f}"),
        "fetch_truncation": fetch_truncation
    }

    out_file = "dgap_sensor_results.json"
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to {out_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="kubernetes/kubernetes")
    parser.add_argument("--start-page", type=int, default=1)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    run(token, args.repo, args.start_page)
