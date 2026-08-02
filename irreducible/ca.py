"""
ca.py -- the elementary cellular automaton engine, the feature extractor and the AUC
pipeline. Shared verbatim by probe.py and irr.py so the feasibility probe and the scored
run cannot silently diverge.

WHY A CELLULAR AUTOMATON. Q5 asks whether a system's future can be read off its present or
whether it has to be run. For real institutions that question is unanswerable, because we
never know whether a shortcut exists or whether we merely failed to find one. Elementary
cellular automata are the one place where the answer is not in doubt: rule 110 is proven
Turing-complete, so no general shortcut to its state at step T can exist. That makes them a
testbed where a NULL result means something, because "no shortcut was found" can be
compared against rules where a shortcut demonstrably does exist.

WHAT THIS IS NOT. A CA is a mathematical object, not an institution. Nothing measured here
transfers to a real organisation without a separate argument that is not made anywhere in
this repository.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

WIDTH = 101
HORIZON = 60           # T. The outcome is the centre cell at this step.
PARTIAL = 30           # k. The "monitor instead of predict" arm sees steps 1..k.
N_INIT = 800           # random initial conditions per rule
WINDOW = 21            # cells of raw initial state, centred, given to the static predictor
FOLDS = 5
SEED = 20260802
CENTRE = WIDTH // 2


def evolve(rule, state, steps):
    """Elementary CA, periodic boundary. Returns the centre column over `steps` steps."""
    table = np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)
    s = state.copy()
    col = np.empty(steps, dtype=np.uint8)
    for t in range(steps):
        idx = (np.roll(s, 1) << 2) | (s << 1) | np.roll(s, -1)
        s = table[idx]
        col[t] = s[CENTRE]
    return col


def initial_conditions(n, rng):
    return rng.integers(0, 2, size=(n, WIDTH), dtype=np.uint8)


def static_features(states):
    """Features of the INITIAL CONDITION only. No step of the CA is run to build these."""
    x = states.astype(np.float64)
    n = x.shape[0]
    d = x.mean(axis=1)
    transitions = (states[:, 1:] != states[:, :-1]).sum(axis=1)
    # longest run of identical cells
    longest = np.empty(n)
    meanrun = np.empty(n)
    for i in range(n):
        runs, cur = [], 1
        row = states[i]
        for j in range(1, WIDTH):
            if row[j] == row[j - 1]:
                cur += 1
            else:
                runs.append(cur)
                cur = 1
        runs.append(cur)
        longest[i] = max(runs)
        meanrun[i] = float(np.mean(runs))
    ac = [np.array([np.corrcoef(x[i, :-l], x[i, l:])[0, 1] if x[i].std() > 0 else 0.0
                    for i in range(n)]) for l in (1, 2, 3)]
    win = x[:, CENTRE - WINDOW // 2: CENTRE + WINDOW // 2 + 1]
    return np.column_stack([d, transitions, longest, meanrun, *ac, win])


def cv_auc(X, y, seed=SEED):
    """Mean out-of-fold AUC. Returns (mean_auc, per_fold list). None if y is degenerate."""
    if len(np.unique(y)) < 2:
        return None, []
    skf = StratifiedKFold(n_splits=FOLDS, shuffle=True, random_state=seed)
    aucs = []
    for tr, te in skf.split(X, y):
        if len(np.unique(y[tr])) < 2 or len(np.unique(y[te])) < 2:
            continue
        m = make_pipeline(StandardScaler(),
                          LogisticRegression(max_iter=2000, C=1.0))
        m.fit(X[tr], y[tr])
        aucs.append(float(roc_auc_score(y[te], m.predict_proba(X[te])[:, 1])))
    if not aucs:
        return None, []
    return float(np.mean(aucs)), aucs


def run_rule(rule, seed=SEED, shuffle_labels=False):
    """Everything measured for one rule. Real CA evolution, no surrogate model anywhere."""
    rng = np.random.default_rng(seed + rule)
    states = initial_conditions(N_INIT, rng)
    cols = np.array([evolve(rule, states[i], HORIZON) for i in range(N_INIT)])
    y = cols[:, HORIZON - 1].astype(int)
    if shuffle_labels:
        y = rng.permutation(y)
    Xs = static_features(states)
    Xp = np.column_stack([Xs, cols[:, :PARTIAL].astype(np.float64)])
    static_auc, static_folds = cv_auc(Xs, y, seed)
    partial_auc, partial_folds = cv_auc(Xp, y, seed)
    return {
        "rule": rule,
        "base_rate": float(y.mean()),
        "static_auc": static_auc, "static_folds": static_folds,
        "partial_auc": partial_auc, "partial_folds": partial_folds,
        "n": int(N_INIT), "horizon": HORIZON, "partial_steps": PARTIAL,
    }
