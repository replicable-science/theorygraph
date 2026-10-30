import math

import numpy as np
import pytest

from theorygraph.metrics import (adjusted_rand_index, bootstrap_mean_ci, krippendorff_alpha_ratio, spearman,
                                 spearman_brown)


def test_ari_identical_partitions_is_one():
    assert adjusted_rand_index(list("aabbc"), list("xxyyz")) == pytest.approx(1.0)


def test_ari_undefined_only_when_both_partitions_are_trivial():
    assert math.isnan(adjusted_rand_index(list("aaaa"), list("bbbb")))
    assert adjusted_rand_index(list("aaaa"), list("abab")) == pytest.approx(0.0)  # same as scikit-learn


def test_ari_matches_scikit_learn_on_random_partitions():
    sk = pytest.importorskip("sklearn.metrics")
    rng = np.random.default_rng(1)
    for _ in range(200):
        n = int(rng.integers(5, 15))
        a, b = rng.integers(0, 4, n).tolist(), rng.integers(0, 4, n).tolist()
        if len(set(a)) < 2 or len(set(b)) < 2:
            continue
        assert adjusted_rand_index(a, b) == pytest.approx(sk.adjusted_rand_score(a, b), abs=1e-12)


def _alpha_brute_force(x):
    """Krippendorff's alpha, ratio level, written the slow way from the definition."""
    x = np.asarray(x, float)
    n_units, m = x.shape

    def d(a, b):
        return 0.0 if a + b == 0 else ((a - b) / (a + b)) ** 2

    d_o = sum(d(x[u, i], x[u, j]) for u in range(n_units) for i in range(m) for j in range(m) if i != j) / (n_units * m * (m - 1))
    vals = x.ravel().tolist()
    n = len(vals)
    d_e = sum(d(vals[i], vals[j]) for i in range(n) for j in range(n) if i != j) / (n * (n - 1))
    return 1 - d_o / d_e


def test_alpha_perfect_agreement_is_one():
    x = np.array([[3, 3], [5, 5], [8, 8], [2, 2]])
    assert krippendorff_alpha_ratio(x) == pytest.approx(1.0)


def test_alpha_matches_brute_force():
    rng = np.random.default_rng(2)
    x = rng.integers(2, 15, size=(12, 3))
    assert krippendorff_alpha_ratio(x) == pytest.approx(_alpha_brute_force(x), abs=1e-12)


def test_spearman_brown_values():
    assert spearman_brown(0.5, 1) == pytest.approx(0.5)
    assert spearman_brown(0.805, 3) == pytest.approx(0.925, abs=1e-3)


def test_spearman_with_ties_matches_scipy_definition():
    sp = pytest.importorskip("scipy.stats")
    x, y = [1, 2, 2, 3, 5, 5, 5, 9], [2, 1, 3, 3, 4, 8, 6, 10]
    assert spearman(x, y) == pytest.approx(sp.spearmanr(x, y).statistic, abs=1e-12)


def test_bootstrap_interval_contains_the_mean():
    m, lo, hi = bootstrap_mean_ci(list(np.random.default_rng(3).normal(0.3, 0.2, 200)))
    assert lo < m < hi
