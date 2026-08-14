"""Index behaviour: fold-in fidelity, scripts, persistence, and honest limits."""

from __future__ import annotations

import os
import sys
import tempfile

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prox
from prox.core import exact_resistance_matrix
from prox.text import FeatureSpace

# Topic structure is present *in the corpus* -- documents within a topic actually
# share terms. This is the regime PROX is for, and it is what real collections look
# like: files repeat vocabulary, link to each other and get opened together.
CATS = [
    "the cat sat on the mat and purred",
    "the cat drank milk and purred softly",
    "a mat where the cat sleeps in sun",
    "milk and a warm mat suit the cat",
]
ENGINES = [
    "diesel engine cylinder compression ignites fuel",
    "the engine cylinder and piston compression",
    "piston and crankshaft drive the engine",
    "fuel injection feeds the diesel engine cylinder",
]
CORPUS = CATS + ENGINES


def test_search_separates_topics():
    ix = prox.build(CORPUS, dim=128, reach=1e-3, seed=0)
    assert int(ix.search("milk purred", top_k=1)[0][0]) < len(CATS)
    assert int(ix.search("cylinder compression", top_k=1)[0][0]) >= len(CATS)


def test_neighbors_stay_within_topic():
    """'More like this' with no query text at all -- pure geometry."""
    ix = prox.build(CORPUS, dim=256, reach=1e-3, seed=0)
    for i in range(len(CORPUS)):
        same = (i < len(CATS)) == (int(ix.neighbors(i, top_k=1)[0][0]) < len(CATS))
        assert same, f"doc {i} left its topic"


def test_topics_survive_wildly_varied_document_lengths():
    """Effective resistance is degree-biased, so long documents drift toward the
    centre of the space and appear as neighbours more often than short ones. This
    pins down that the bias does not overwhelm topical structure across a 32x
    length range."""
    rng = np.random.default_rng(0)
    va = ["cat", "mat", "milk", "purr", "whisker", "paw"]
    ve = ["engine", "piston", "cylinder", "fuel", "crank", "valve"]
    texts, lab = [], []
    for t, v in ((0, va), (1, ve)):
        for L in (4, 8, 16, 32, 64, 128):
            for _ in range(4):
                texts.append(" ".join(rng.choice(v, size=L)))
                lab.append(t)
    lab = np.array(lab)
    ix = prox.build(texts, dim=256, reach=1e-3, seed=0)
    nn = np.array([int(ix.neighbors(i, top_k=1)[0][0]) for i in range(len(texts))])
    assert (lab[nn] == lab).mean() > 0.95


def test_prox_does_not_invent_world_knowledge():
    """A documented limit, asserted so it cannot be quietly forgotten.

    'cat' and 'feline' are synonyms in the world but share no character n-gram and,
    in a corpus this small, no connecting path. A trained embedding model knows they
    are related because someone paid to show it a billion sentences. PROX derives
    association from the structure of the collection it is given and claims nothing
    beyond it. On a real collection that structure exists in abundance; on eight
    unconnected sentences it does not, and PROX should not pretend otherwise.
    """
    disjoint = [
        "the cat sat quietly",            # 0
        "feline companions groom",        # 1  synonym of 0, zero shared substring
        "diesel compression ignites",     # 2
    ]
    ix = prox.build(disjoint, dim=256, reach=1e-3, seed=0)
    d = np.linalg.norm(ix.X_items[0] - ix.X_items[1])
    d_unrelated = np.linalg.norm(ix.X_items[0] - ix.X_items[2])
    # No claim that the synonym is nearer; the corpus contains no evidence for it.
    assert abs(d - d_unrelated) / max(d, d_unrelated) < 0.35


def test_fold_in_costs_nothing_against_a_full_resolve():
    """The O(1) query path must track true resistance as well as a full rebuild.

    Ground truth is the exact resistance from a query node that is genuinely part
    of the graph, via a dense inverse. Two things are checked: fold-in correlates
    strongly with that truth, and it is no worse than paying for `dim` fresh solves
    with the query included. The residual gap is the JL dimension, not the
    approximation -- both curves rise together as dim grows.
    """
    from scipy.stats import spearmanr

    rng = np.random.default_rng(0)
    topics = [[f"t{t}v{i}" for i in range(6)] for t in range(8)]
    texts = [" ".join(rng.choice(topics[t], size=6)) for t in range(8) for _ in range(6)]
    query = " ".join(rng.choice(topics[3], size=3))
    NB, MDF, DIM = 1 << 12, 2, 1024

    # Exact resistance on the graph that includes the query as a real node.
    fs = FeatureSpace(n_buckets=NB, seed=0)
    docs = fs.fit(texts + [query])
    df = np.zeros(NB, dtype=np.int32)
    for c in docs:
        df[np.fromiter(c.keys(), dtype=np.int64, count=len(c))] += 1
    active = np.flatnonzero(df >= MDF)
    lookup = np.full(NB, -1, dtype=np.int64)
    lookup[active] = np.arange(active.size)
    ei, ej, ew = [], [], []
    for d, c in enumerate(docs):
        b, w = fs.weights(c)
        f = lookup[b]
        k = f >= 0
        ei.append(np.full(int(k.sum()), d))
        ej.append(f[k] + len(docs))
        ew.append(w[k])
    edges = np.column_stack([np.concatenate(ei), np.concatenate(ej)])
    R = exact_resistance_matrix(edges, np.concatenate(ew), len(docs) + active.size, reach=1e-3)
    truth = np.sqrt(np.maximum(R[len(texts), : len(texts)], 0.0))

    fold, _ = prox.build(
        texts, dim=DIM, reach=1e-3, seed=0, n_buckets=NB, min_df=MDF
    ).distances_from(query)
    full = prox.build(texts + [query], dim=DIM, reach=1e-3, seed=0, n_buckets=NB, min_df=MDF)
    resolved = np.linalg.norm(full.X_items[:-1] - full.X_items[-1], axis=1)

    rho_fold = spearmanr(fold, truth).statistic
    rho_full = spearmanr(resolved, truth).statistic
    assert rho_fold > 0.85, f"fold-in vs truth rho={rho_fold:.3f}"
    assert rho_fold > 0.9 * rho_full, f"fold-in {rho_fold:.3f} << resolve {rho_full:.3f}"


@pytest.mark.parametrize(
    "docs,query,expect",
    [
        (["mtoto ana homa kali", "gari langu limeharibika injini"], "homa ya mtoto", 0),
        (["الطفل يعاني من الحمى الشديدة", "السيارة تحتاج إلى إصلاح المحرك"], "حمى الطفل", 0),
        (["शिशु को तेज़ बुखार है", "गाड़ी का इंजन खराब है"], "बुखार", 0),
        (["def parse_header(buf): return buf[:4]", "SELECT name FROM users"], "parse_header buffer", 0),
    ],
    ids=["swahili", "arabic", "hindi", "code"],
)
def test_works_in_any_script_without_configuration(docs, query, expect):
    """No tokenizer, no vocabulary file, no language flag -- character n-grams only."""
    ix = prox.build(docs, dim=64, reach=1e-3, seed=0)
    assert int(ix.search(query, top_k=1)[0][0]) == expect


def test_roundtrip_preserves_results_exactly():
    ix = prox.build(CORPUS, dim=64, seed=0)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "t.prox.npz")
        ix.save(p)
        back = prox.ProxIndex.load(p)
    assert back.meta["format"] == prox.FORMAT
    a, b = ix.search("milk purred", top_k=4), back.search("milk purred", top_k=4)
    assert [x[0] for x in a] == [x[0] for x in b]
    assert np.allclose([x[1] for x in a], [x[1] for x in b])


def test_query_with_no_shared_features_is_reported_not_faked():
    """An honest empty answer beats a confident wrong one."""
    ix = prox.build(CORPUS, dim=32, seed=0)
    assert ix.search("龍龍龍龍龍", top_k=3) == []


def test_empty_corpus_rejected():
    with pytest.raises(ValueError):
        prox.build([])
