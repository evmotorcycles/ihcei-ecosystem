// lism_diagnostic.mjs — live τ_v + Dissonance (σ) on real GitHub cohorts.
// ============================================================================
// The one positive, deployable finding of the LISM manuscript is a *hazard*
// read from clean timestamps: a network's enforcement latency (τ_v — how long
// it takes to close what it itself flagged) and its DISSONANCE (σ — the gap
// between what it SAYS about its own health and what it DOES).
//
// This module computes both from the real GitHub cohorts already captured in
// this repo (live issue-close latencies fetched earlier from the public API).
// No network needed to reproduce; re-fetch the cohorts to refresh.
//
//   τ_v(repo)  = mean capped issue-close latency (days), server-computed.
//   SAY  (V)   = declared vitality: recency of the last push. A fresh push is
//                the project SIGNALLING "we are alive and maintaining this."
//   DO   (R)   = enacted responsiveness: -log(1+τ_v). Actually closing flagged
//                risk fast is the project DOING what an alive project does.
//   σ = z(V) - z(R)   (standardized WITHIN the cohort — LISM doctrine is
//                       "calibrate locally, never import a universal threshold").
//
//   σ  >>  0  ZOMBIE:         loudly alive (fresh push), but risk rots (slow close).
//   σ  <<  0  INVERSE-ZOMBIE: looks stale (old push), but resolves fast — an
//                             under-rated healthy project.
//   σ  ≈  0   HONEST:         say and do agree (a fresh, responsive project, OR a
//                             frankly-deprecated one that is stale AND slow).
//
// σ is a say-do *coherence* signal, not a quality score: an honestly-dead repo
// scores ≈ 0 precisely because it is not lying about its state. The alarming
// cell is high |σ| — the project whose posture and behaviour have diverged.

const DAY = 86400.0;

const mean = xs => xs.reduce((a, b) => a + b, 0) / xs.length;
const sd = xs => { const m = mean(xs); return Math.sqrt(mean(xs.map(x => (x - m) ** 2))) || 1; };
const daysSince = (iso, now) => (now - new Date(iso).getTime()) / (DAY * 1000);

// Normalize a captured cohort file (any of the three snapshot shapes) to
// [{repo, tau_v, pushed_at, archived, E, stargazers, n_closed}].
export function reposOf(cohort) {
  const rs = cohort.repos || cohort.response?.repos || [];
  return rs.map(r => ({
    repo: r.repo, tau_v: r.tau_v, pushed_at: r.pushed_at,
    archived: !!r.archived, E: r.E, stargazers: r.stargazers ?? null,
    n_closed: r.n_closed ?? null,
  }));
}

// Compute σ for one cohort (z-scores are cohort-relative on purpose).
// Repos with no closed issues (τ_v == null) carry no latency signal and are
// reported separately rather than imputed.
export function dissonance(repos, { now = Date.now() } = {}) {
  const scored = repos.filter(r => r.tau_v != null && r.pushed_at);
  const noSignal = repos.filter(r => r.tau_v == null || !r.pushed_at)
    .map(r => ({ repo: r.repo, reason: r.tau_v == null ? 'no closed issues (no latency signal)' : 'no push timestamp' }));
  if (scored.length < 2) return { rows: [], noSignal, note: 'need >=2 repos with signal' };

  const V = scored.map(r => -daysSince(r.pushed_at, now));        // recency: higher = fresher push = louder "alive"
  const R = scored.map(r => -Math.log1p(r.tau_v));                // responsiveness: higher = faster close
  const [mV, sV, mR, sR] = [mean(V), sd(V), mean(R), sd(R)];

  const rows = scored.map((r, i) => {
    const vz = (V[i] - mV) / sV, rz = (R[i] - mR) / sR;
    const sigma = vz - rz;
    const label = sigma > 1.0 ? 'ZOMBIE' : sigma < -1.0 ? 'INVERSE-ZOMBIE' : 'coherent';
    return {
      repo: r.repo, tau_v: r.tau_v, days_since_push: +daysSince(r.pushed_at, now).toFixed(0),
      say_z: +vz.toFixed(2), do_z: +rz.toFixed(2), sigma: +sigma.toFixed(2), label,
    };
  }).sort((a, b) => b.sigma - a.sigma);
  return { rows, noSignal };
}

// Third-Law direction check: is τ_v higher among FAILED repos (E=0: archived or
// long-stale) than SURVIVING ones (E=1)? Reproduces the manuscript's sign on
// whatever labeled repos a cohort carries. Returns null if a class is empty.
export function thirdLawDirection(repos) {
  const lat = r => r.tau_v;
  const survived = repos.filter(r => r.E === 1 && r.tau_v != null).map(lat);
  const failed = repos.filter(r => r.E === 0 && r.tau_v != null).map(lat);
  if (!survived.length || !failed.length) return null;
  return {
    survived_mean: +mean(survived).toFixed(2), survived_n: survived.length,
    failed_mean: +mean(failed).toFixed(2), failed_n: failed.length,
    direction_holds: mean(failed) > mean(survived),
  };
}
