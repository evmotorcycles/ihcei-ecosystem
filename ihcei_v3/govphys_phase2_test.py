"""
govphys_github_test.py
======================
GovPhys Phase 2 Gradient Prediction Test — REAL GitHub Data
GT v18.0 / QG-COS — Preprint v8 Pre-registered Prospective Test

PRE-REGISTRATION (set before any data is fetched)
---------------------------------------------------
This file contains the complete pre-registered specification for the
Gradient Prediction test. All variable definitions, thresholds, and
comparison criteria are locked here BEFORE any GitHub API call is made.

Failure to run against live data with these exact specifications
invalidates the pre-registration. Do not alter the thresholds after
seeing results.

GRADIENT PREDICTION (from Preprint v8, §6.3):
  As D proxy quality improves from hardware-layer to OS-layer measurement,
  the functional form shifts: linear → quadratic.
  
  Specifically:
  HARDWARE PROXY → linear D outperforms quadratic D²
  OS PROXY       → quadratic D² outperforms linear D

THIRD LAW PREDICTION:
  Mean τ_v (issue close latency) for failed projects > survived projects.

PRE-REGISTERED SPECIFICATIONS
------------------------------
Failure criterion:
  A repository is E=0 (failed) if:
  (a) archived = True, OR
  (b) pushed_at < 2 years before query date AND stars < 10
  Survived = E=1 otherwise

D_enc proxy (hardware layer):
  commit_message_length_ratio = mean(len(msg) for msg in commit_messages) / 100
  Rationale: longer commit messages = more documentation = surface compliance
  Layer: HARDWARE (measures volume of text, not semantic direction)

D_enc proxy (OS layer):
  sentence embedding cosine similarity of commit messages against OQM
  reference frame (16 methodology-documentation sentences)
  Layer: OS (measures semantic alignment, not keyword count)

D_dec proxy (hardware layer):
  merge_ratio = merged_PRs / total_PRs (if total_PRs > 0 else 0)
  Rationale: merged PR fraction = delivery compliance
  Layer: HARDWARE (binary completion, not verification quality)

D_dec proxy (OS layer):
  review_completion_rate = PRs_with_>=1_review_comment / total_PRs
  Rationale: actual review engagement = execution verification
  Layer: OS (measures verification behaviour, not just merge status)

U proxy (both layers):
  log(1 + contributors) * log(1 + total_commits)
  Rationale: team size × activity = transactional utility

τ_v (Third Law, enforcement latency):
  mean(days from issue_created_at to issue_closed_at) for closed issues
  Capped at 365 days to exclude abandoned issues

D_crit:
  1 / mean_degree of the contributor-repository bipartite graph
  Pre-specified: expected ~0.05-0.15 for OSS networks

MINIMUM SAMPLE: N_failures >= 30, N_total >= 100
ΔAIC threshold for gradient confirmation: 
  Hardware: linear ΔAIC(lin-quad) < 0  (linear superior)
  OS layer: quadratic ΔAIC(quad-lin) > 3  (quadratic decisive)

REPOSITORIES TO QUERY:
  Search GitHub for Python repositories with >50 stars, created before 2021.
  Sample 200 repositories stratified by activity level.
  This produces a natural mix of active/archived/abandoned projects.
"""

import os
import json
import time
import math
import hashlib
import datetime
import numpy as np
from collections import defaultdict
from typing import List, Dict, Optional, Tuple

# ── DEPENDENCIES ─────────────────────────────────────────────────────────────
# pip install requests scipy numpy
# Optional for OS-layer D_enc: pip install sentence-transformers
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("requests not available — pip install requests")

try:
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    import torch
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("sentence-transformers not available — OS-layer D_enc will use enhanced TF-IDF")


# ── OQM REFERENCE FRAME (pre-registered, do not modify) ─────────────────────

OQM_REFERENCE = [
    "The methodology is documented and independently verifiable.",
    "This commit fixes the following procedure: [specific steps]",
    "Added verification step before executing the main operation.",
    "Refactored with explicit error handling and rollback procedure.",
    "This change was reviewed against the specification document.",
    "Added tests that verify the expected behavior explicitly.",
    "The extraction process applied was the following sequential procedure.",
    "All claims are falsifiable and the counter-case is documented.",
    "Options considered: [A, B, C]. Selected [A] because [reason].",
    "The methodology was reviewed and approved by [role, not person].",
    "Breaking change: alternatives considered were [list], selected because [reason].",
    "Source: [reference]. Verified against [independent source].",
    "Revert: this restores verified behavior after failing execution.",
    "Fix: closes issue with documented root cause and verification.",
    "Added: new capability with methodology documented in [location].",
    "Merged after: code review, test pass, documentation update.",
    # Anti-D anchors (weighted negative)
    "minor fix",
    "wip",
    "update",
    "stuff",
]

OQM_WEIGHTS = [1.0]*16 + [-0.5]*4


# ── LOGISTIC AIC COMPUTATION ─────────────────────────────────────────────────

def logistic(x): return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

def logistic_aic(E: np.ndarray, X: np.ndarray) -> float:
    """Compute AIC for logistic regression."""
    if not SCIPY_AVAILABLE:
        raise RuntimeError("scipy required")
    
    def nll(params):
        p = logistic(X @ params)
        p = np.clip(p, 1e-9, 1-1e-9)
        return -np.sum(E * np.log(p) + (1-E)*np.log(1-p))
    
    x0 = np.zeros(X.shape[1])
    res = minimize(nll, x0, method='L-BFGS-B',
                   options={'maxiter': 1000, 'ftol': 1e-12})
    return 2*res.fun + 2*X.shape[1]

def add_const(x: np.ndarray) -> np.ndarray:
    return np.column_stack([np.ones(len(x)), x])


# ── GITHUB API CLIENT ─────────────────────────────────────────────────────────

class GitHubClient:
    BASE = "https://api.github.com"
    
    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        })
        self._check_rate_limit()
    
    def _check_rate_limit(self):
        r = self.session.get(f"{self.BASE}/rate_limit")
        data = r.json()
        remaining = data['resources']['core']['remaining']
        print(f"  GitHub API: {remaining} requests remaining")
        if remaining < 100:
            reset_time = data['resources']['core']['reset']
            print(f"  WARNING: Low rate limit. Resets at {datetime.datetime.fromtimestamp(reset_time)}")
    
    def _get(self, url: str, params: dict = None) -> dict:
        """Rate-limited GET with retry."""
        for attempt in range(3):
            r = self.session.get(url, params=params)
            if r.status_code == 403:
                # Rate limited
                reset = int(r.headers.get('X-RateLimit-Reset', time.time() + 60))
                wait = max(0, reset - time.time()) + 5
                print(f"  Rate limited. Waiting {wait:.0f}s...")
                time.sleep(wait)
                continue
            if r.status_code == 200:
                return r.json()
            time.sleep(2 ** attempt)
        return {}
    
    def search_repos(self, query: str, n: int = 200) -> List[dict]:
        """Search repositories, return up to n results."""
        repos = []
        page = 1
        while len(repos) < n:
            data = self._get(f"{self.BASE}/search/repositories", {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": min(30, n - len(repos)),
                "page": page,
            })
            items = data.get("items", [])
            if not items:
                break
            repos.extend(items)
            page += 1
            time.sleep(2)  # Be respectful
        return repos[:n]
    
    def get_commits(self, owner: str, repo: str, n: int = 50) -> List[dict]:
        data = self._get(f"{self.BASE}/repos/{owner}/{repo}/commits",
                         {"per_page": min(n, 100)})
        return data if isinstance(data, list) else []
    
    def get_pulls(self, owner: str, repo: str) -> List[dict]:
        all_prs = []
        for state in ["open", "closed"]:
            data = self._get(f"{self.BASE}/repos/{owner}/{repo}/pulls",
                            {"state": state, "per_page": 100})
            if isinstance(data, list):
                all_prs.extend(data)
        return all_prs
    
    def get_issues(self, owner: str, repo: str) -> List[dict]:
        data = self._get(f"{self.BASE}/repos/{owner}/{repo}/issues",
                         {"state": "closed", "per_page": 100})
        return data if isinstance(data, list) else []
    
    def get_contributors(self, owner: str, repo: str) -> int:
        data = self._get(f"{self.BASE}/repos/{owner}/{repo}/contributors",
                         {"per_page": 1, "anon": "true"})
        # Use X-Total count if available
        return len(data) if isinstance(data, list) else 0


# ── D PROXY COMPUTATION ───────────────────────────────────────────────────────

class ProxyComputer:
    
    def __init__(self):
        self._model = None
        self._ref_vec = None
        if EMBEDDINGS_AVAILABLE:
            print("  Loading sentence-transformers model...")
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
            ref_embs = self._model.encode(OQM_REFERENCE, convert_to_numpy=True,
                                          show_progress_bar=False)
            weights = np.array(OQM_WEIGHTS)
            self._ref_vec = np.sum(ref_embs * weights[:,None], axis=0)
            self._ref_vec /= np.linalg.norm(self._ref_vec) + 1e-9
            print("  Embedding model ready.")
    
    # ── HARDWARE PROXIES ──────────────────────────────────────────────────
    
    def D_enc_hardware(self, commit_messages: List[str]) -> float:
        """D_enc hardware proxy: mean commit message length ratio.
        Measures text volume (As-Sidq), not semantic direction."""
        if not commit_messages:
            return 0.0
        lengths = [len(m.strip()) for m in commit_messages]
        return min(1.0, np.mean(lengths) / 100.0)
    
    def D_dec_hardware(self, pulls: List[dict]) -> float:
        """D_dec hardware proxy: merged PR / total PR ratio.
        Measures delivery compliance (As-Sidq), not review quality."""
        if not pulls:
            return 0.0
        total = len(pulls)
        merged = sum(1 for p in pulls if p.get("merged_at") is not None)
        return merged / total
    
    # ── OS-LAYER PROXIES ──────────────────────────────────────────────────
    
    def D_enc_os(self, commit_messages: List[str]) -> float:
        """D_enc OS proxy: cosine similarity in embedding space vs OQM reference.
        Measures semantic alignment with governance protocol (Al-Haqq)."""
        if not commit_messages:
            return 0.0
        if self._model is None:
            # Fallback to enhanced TF-IDF (Phase 1.5)
            return self._D_enc_tfidf_enhanced(commit_messages)
        
        texts = [m[:500] for m in commit_messages[:50]]  # limit tokens
        embs = self._model.encode(texts, convert_to_numpy=True,
                                  show_progress_bar=False)
        sims = []
        for emb in embs:
            norm = np.linalg.norm(emb)
            if norm > 0:
                sim = np.dot(emb / norm, self._ref_vec)
                sims.append(float(sim))
        return float(np.clip(np.mean(sims), 0.0, 1.0)) if sims else 0.0
    
    def _D_enc_tfidf_enhanced(self, messages: List[str]) -> float:
        """Phase 1.5 fallback: enhanced TF-IDF with governance patterns."""
        import re
        high_d = [r'\bmethodology\b', r'\bverif\w+\b', r'\bdocument\w+\b',
                  r'\bfalsif\w+\b', r'\btraceable\b', r'\breplicable\b',
                  r'\bprocedure\b', r'\bprotocol\b', r'\banalysis\b',
                  r'\balternative\b', r'\btransparent\b']
        low_d  = [r'\bfix\b', r'\bwip\b', r'\bminor\b', r'\bstuff\b',
                  r'\bupdate\b', r'\btest\b$', r'\btodo\b']
        
        hd_patterns = [re.compile(p, re.IGNORECASE) for p in high_d]
        ld_patterns = [re.compile(p, re.IGNORECASE) for p in low_d]
        
        scores = []
        for msg in messages:
            hd = sum(1 for p in hd_patterns if p.search(msg))
            ld = sum(1 for p in ld_patterns if p.search(msg))
            raw = (hd - ld * 1.5) / (hd + ld * 1.5 + 1.0)
            scores.append(float(np.clip((raw + 1.0) / 2.0, 0.0, 1.0)))
        return float(np.mean(scores)) if scores else 0.5
    
    def D_dec_os(self, pulls: List[dict]) -> float:
        """D_dec OS proxy: fraction of PRs with at least 1 review comment.
        Measures actual verification engagement (Al-Haqq)."""
        if not pulls:
            return 0.0
        reviewed = sum(1 for p in pulls 
                       if (p.get("review_comments", 0) or 0) >= 1)
        return reviewed / len(pulls)
    
    def compute_tau_v(self, issues: List[dict]) -> float:
        """τ_v: mean issue close latency in days (capped at 365)."""
        latencies = []
        for iss in issues:
            created = iss.get("created_at")
            closed  = iss.get("closed_at")
            if created and closed and iss.get("state") == "closed":
                try:
                    t_open  = datetime.datetime.fromisoformat(created.replace("Z","+00:00"))
                    t_close = datetime.datetime.fromisoformat(closed.replace("Z","+00:00"))
                    days = (t_close - t_open).total_seconds() / 86400
                    latencies.append(min(365.0, max(0.0, days)))
                except:
                    pass
        return float(np.mean(latencies)) if latencies else 30.0  # default 30 days
    
    def compute_U(self, repo: dict, n_contributors: int, n_commits: int) -> float:
        """U = log(1+contributors) × log(1+commits) = transactional utility."""
        return math.log1p(max(n_contributors, 1)) * math.log1p(max(n_commits, 1))


# ── FAILURE CRITERION (pre-registered, do not alter) ──────────────────────────

def is_failed(repo: dict) -> int:
    """
    E=0 (failed) if:
      (a) archived = True, OR
      (b) pushed_at > 2 years ago AND stars < 10
    E=1 (survived) otherwise.
    
    PRE-REGISTERED: do not modify this function after seeing data.
    """
    if repo.get("archived", False):
        return 0
    
    pushed_at = repo.get("pushed_at", "")
    stars = repo.get("stargazers_count", 0)
    
    if pushed_at:
        try:
            pushed = datetime.datetime.fromisoformat(pushed_at.replace("Z","+00:00"))
            age_years = (datetime.datetime.now(datetime.timezone.utc) - pushed).days / 365
            if age_years > 2.0 and stars < 10:
                return 0
        except:
            pass
    
    return 1


# ── MAIN TEST ─────────────────────────────────────────────────────────────────

def run_gradient_prediction_test(
    github_token: str,
    n_repos: int = 200,
    min_failures: int = 30,
    output_csv: str = "govphys_results.csv"
) -> dict:
    """
    Run the pre-registered Gradient Prediction Test on real GitHub data.
    
    Parameters
    ----------
    github_token: str
        GitHub personal access token (read:public_repo scope sufficient)
    n_repos: int
        Number of repositories to query (default 200)
    min_failures: int
        Minimum E=0 cases required (default 30, per pre-registration)
    output_csv: str
        CSV file to write results to for audit trail
    
    Returns
    -------
    dict with all results, hypothesis decisions, and certificate
    """
    print("=" * 65)
    print("GovPhys PHASE 2 GRADIENT PREDICTION TEST")
    print("PRE-REGISTERED | PROSPECTIVE | REAL GITHUB DATA")
    print("=" * 65)
    print()
    print("PRE-REGISTERED SPECIFICATIONS:")
    print(f"  Failure criterion: archived=True OR (age>2yr AND stars<10)")
    print(f"  Hardware D_enc:    commit message length ratio")
    print(f"  Hardware D_dec:    merged PR fraction")
    print(f"  OS D_enc:          {'sentence embedding cosine vs OQM' if EMBEDDINGS_AVAILABLE else 'enhanced TF-IDF (embedding not available)'}")
    print(f"  OS D_dec:          PR review engagement rate")
    print(f"  U:                 log(1+contributors) × log(1+commits)")
    print(f"  τ_v:               mean issue close latency (days, capped 365)")
    print(f"  Repos to query:    {n_repos}")
    print(f"  Min failures:      {min_failures}")
    print(f"  Confirmation:      hardware ΔAIC(lin-quad)<0, OS ΔAIC(quad-lin)>3")
    print()
    
    client = GitHubClient(github_token)
    proxy  = ProxyComputer()
    
    # ── Fetch repositories ──
    print("Fetching repositories...")
    query = "language:python stars:>50 created:<2021-01-01"
    repos = client.search_repos(query, n=n_repos)
    print(f"  Fetched: {len(repos)} repositories")
    
    # ── Extract metrics ──
    print("\nExtracting metrics (this takes several minutes)...")
    records = []
    
    for i, repo in enumerate(repos):
        owner = repo["owner"]["login"]
        name  = repo["name"]
        
        if i % 20 == 0:
            print(f"  Progress: {i}/{len(repos)} ({len(records)} valid records)")
        
        try:
            commits   = client.get_commits(owner, name, n=50)
            pulls     = client.get_pulls(owner, name)
            issues    = client.get_issues(owner, name)
            n_contrib = client.get_contributors(owner, name)
            
            n_commits = repo.get("size", 100)  # commits not in repo meta, use size as proxy
            commit_messages = [c.get("commit", {}).get("message", "") 
                               for c in commits if c.get("commit")]
            
            E = is_failed(repo)
            U = proxy.compute_U(repo, n_contrib, len(commits))
            
            # Hardware proxies
            D_enc_hw = proxy.D_enc_hardware(commit_messages)
            D_dec_hw = proxy.D_dec_hardware(pulls)
            D_hw = D_enc_hw * D_dec_hw
            
            # OS proxies
            D_enc_os = proxy.D_enc_os(commit_messages)
            D_dec_os = proxy.D_dec_os(pulls)
            D_os = D_enc_os * D_dec_os
            
            tau_v = proxy.compute_tau_v(issues)
            
            records.append({
                "repo":      f"{owner}/{name}",
                "E":         E,
                "U":         U,
                "D_enc_hw":  D_enc_hw,
                "D_dec_hw":  D_dec_hw,
                "D_hw":      D_hw,
                "D_enc_os":  D_enc_os,
                "D_dec_os":  D_dec_os,
                "D_os":      D_os,
                "tau_v":     tau_v,
                "stars":     repo.get("stargazers_count", 0),
                "archived":  repo.get("archived", False),
            })
            
        except Exception as e:
            pass  # Skip repos with API errors
        
        time.sleep(1.5)  # Respectful API usage
    
    print(f"\n  Extraction complete: {len(records)} valid records")
    
    # ── Check sample size ──
    E_arr = np.array([r["E"] for r in records])
    n_fail = int((1 - E_arr).sum())
    n_surv = int(E_arr.sum())
    print(f"  E=0 (failed): {n_fail}, E=1 (survived): {n_surv}")
    
    if n_fail < min_failures:
        print(f"\n  INSUFFICIENT FAILURES: {n_fail} < {min_failures} required.")
        print(f"  Increase n_repos or broaden failure criterion.")
        return {"status": "INSUFFICIENT_SAMPLE", "n_fail": n_fail}
    
    # ── Save CSV for audit ──
    import csv
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    print(f"  Raw data saved: {output_csv}")
    
    # ── Run null model ──
    print("\nRunning null model (1000 permutations)...")
    U_arr     = np.array([r["U"] for r in records])
    D_hw_arr  = np.array([r["D_hw"] for r in records])
    D_os_arr  = np.array([r["D_os"] for r in records])
    
    np.random.seed(42)
    null_dAIC_hw = []
    null_dAIC_os = []
    for _ in range(1000):
        D_r = np.random.permutation(D_hw_arr)
        try:
            aL = logistic_aic(E_arr, add_const(U_arr * D_r))
            aQ = logistic_aic(E_arr, add_const(U_arr * D_r**2))
            null_dAIC_hw.append(aL - aQ)
        except: pass
        D_r = np.random.permutation(D_os_arr)
        try:
            aL = logistic_aic(E_arr, add_const(U_arr * D_r))
            aQ = logistic_aic(E_arr, add_const(U_arr * D_r**2))
            null_dAIC_os.append(aL - aQ)
        except: pass
    
    # ── P1 AIC comparison ──
    print("\nComputing AIC comparisons...")
    aic_hw_lin  = logistic_aic(E_arr, add_const(U_arr * D_hw_arr))
    aic_hw_quad = logistic_aic(E_arr, add_const(U_arr * D_hw_arr**2))
    aic_os_lin  = logistic_aic(E_arr, add_const(U_arr * D_os_arr))
    aic_os_quad = logistic_aic(E_arr, add_const(U_arr * D_os_arr**2))
    
    dAIC_hw = aic_hw_lin - aic_hw_quad   # negative = linear wins
    dAIC_os = aic_os_lin - aic_os_quad   # positive = quadratic wins
    
    hw_null_z = ((dAIC_hw - np.mean(null_dAIC_hw)) / 
                 max(np.std(null_dAIC_hw), 0.001)) if null_dAIC_hw else 0
    os_null_z = ((dAIC_os - np.mean(null_dAIC_os)) / 
                 max(np.std(null_dAIC_os), 0.001)) if null_dAIC_os else 0
    
    # ── Third Law: τ_v comparison ──
    tau_fail = [r["tau_v"] for r in records if r["E"] == 0]
    tau_surv = [r["tau_v"] for r in records if r["E"] == 1]
    tau_fail_mean = np.mean(tau_fail) if tau_fail else 0
    tau_surv_mean = np.mean(tau_surv) if tau_surv else 0
    
    from scipy.stats import mannwhitneyu
    try:
        stat, p_tau = mannwhitneyu(tau_fail, tau_surv, alternative='greater')
    except:
        p_tau = 1.0
    
    # ── Gradient Prediction Verdict ──
    hw_prediction = dAIC_hw < 0       # linear superior at hardware layer
    os_prediction = dAIC_os > 3.0     # quadratic decisive at OS layer
    os_null_cleared = os_null_z > 3.0 # above null at z>3
    gradient_confirmed = hw_prediction and os_prediction and os_null_cleared
    third_law = tau_fail_mean > tau_surv_mean and p_tau < 0.05
    
    # ── Report ──
    print()
    print("=" * 65)
    print("RESULTS — REAL GITHUB DATA")
    print("=" * 65)
    print(f"\nSample: {len(records)} repositories, {n_fail} failures, {n_surv} survived")
    print()
    print("GRADIENT PREDICTION TEST (P1):")
    print(f"  Hardware layer:")
    print(f"    Linear AIC:    {aic_hw_lin:.2f}")
    print(f"    Quadratic AIC: {aic_hw_quad:.2f}")
    print(f"    ΔAIC(lin-quad): {dAIC_hw:+.2f}  {'LINEAR WINS ✓' if dAIC_hw < 0 else 'QUADRATIC WINS ✗ (unexpected)'}")
    print(f"    Null model Z:  {hw_null_z:.2f}")
    print()
    print(f"  OS layer:")
    print(f"    Linear AIC:    {aic_os_lin:.2f}")
    print(f"    Quadratic AIC: {aic_os_quad:.2f}")
    print(f"    ΔAIC(quad-lin): {dAIC_os:+.2f}  {'QUADRATIC WINS ✓' if dAIC_os > 3 else 'QUADRATIC NOT DECISIVE ✗'}")
    print(f"    Null model Z:  {os_null_z:.2f}")
    print()
    print("THIRD LAW TEST (τ_v):")
    print(f"  Failed projects τ_v mean:   {tau_fail_mean:.1f} days")
    print(f"  Survived projects τ_v mean: {tau_surv_mean:.1f} days")
    print(f"  Mann-Whitney p (one-tailed): {p_tau:.4f}")
    print(f"  Third Law: {'SUPPORTED ✓' if third_law else 'NOT SUPPORTED ✗'}")
    print()
    print("OVERALL GRADIENT PREDICTION:")
    if gradient_confirmed:
        print("  ✓✓ GRADIENT PREDICTION CONFIRMED")
        print("  Hardware layer → linear; OS layer → quadratic > 3 ΔAIC; z>3")
        print("  This constitutes prospective validation of the layer detection")
        print("  hypothesis as pre-registered in Preprint v8.")
    else:
        print("  GRADIENT PREDICTION NOT CONFIRMED")
        conditions = [
            ("hw_linear_wins", hw_prediction),
            ("os_quadratic_decisive_>3", os_prediction),
            ("os_null_cleared_z>3", os_null_cleared),
        ]
        for name, cond in conditions:
            print(f"    {'✓' if cond else '✗'}  {name}")
        print()
        print("  Proceed with three-hypothesis analysis:")
        print("  A) Proxy still insufficiently OS-layer (upgrade D_dec)")
        print("  B) Domain functional form genuinely domain-variable (physics)")
        print("  C) Sample size insufficient (increase n_repos)")
    
    # ── Certificate ──
    cert_payload = (f"N={len(records)}|fail={n_fail}|dAIC_hw={dAIC_hw:.4f}|"
                    f"dAIC_os={dAIC_os:.4f}|tau_p={p_tau:.4f}|"
                    f"confirmed={gradient_confirmed}")
    cert_hash = hashlib.sha256(cert_payload.encode()).hexdigest()
    cert_id = "GOVPHYS-P2-" + cert_hash[:12].upper()
    print()
    print(f"Certificate: {cert_id}")
    print(f"Payload: {cert_payload}")
    
    return {
        "status": "COMPLETE",
        "n_total": len(records),
        "n_fail": n_fail,
        "n_surv": n_surv,
        "dAIC_hw": dAIC_hw,
        "dAIC_os": dAIC_os,
        "hw_null_z": hw_null_z,
        "os_null_z": os_null_z,
        "tau_fail_mean": tau_fail_mean,
        "tau_surv_mean": tau_surv_mean,
        "p_tau": p_tau,
        "gradient_confirmed": gradient_confirmed,
        "third_law_supported": third_law,
        "certificate_id": cert_id,
        "certificate_hash": cert_hash,
    }


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("GovPhys Phase 2 Gradient Prediction Test")
    print()
    
    TOKEN = os.environ.get("GITHUB_TOKEN", "")
    if not TOKEN:
        print("Set GITHUB_TOKEN environment variable:")
        print("  export GITHUB_TOKEN=ghp_your_token_here")
        print("  python3 govphys_github_test.py")
        print()
        print("Or in Colab:")
        print("  from google.colab import userdata")
        print("  token = userdata.get('GITHUB_TOKEN')")
        print("  from govphys_github_test import run_gradient_prediction_test")
        print("  results = run_gradient_prediction_test(token)")
    else:
        results = run_gradient_prediction_test(TOKEN)

