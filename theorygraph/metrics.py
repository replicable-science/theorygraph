"""Agreement metrics used by the audit. Pure numpy, no other dependencies.

Each function is small enough to check by hand; tests/test_metrics.py compares them
with reference values (scikit-learn for ARI, hand-computed cases for alpha).
"""
from __future__ import annotations

import math
from typing import Hashable, Iterable, Sequence

import numpy as np


def _comb2(x):
    x = np.asarray(x, dtype=float)
    return x * (x - 1.0) / 2.0


def adjusted_rand_index(a: Sequence[Hashable], b: Sequence[Hashable]) -> float:
    """Adjusted Rand index between two partitions of the same items (Hubert & Arabie, 1985).

    0 means the partitions agree no more than chance; 1 means identical partitions.
    Returns NaN when the index is undefined (both partitions trivial, i.e. one cluster or all singletons).
    If only one partition is trivial the index is 0, as in scikit-learn.
    """
    a, b = list(a), list(b)
    n = len(a)
    if n != len(b):
        raise ValueError("partitions must label the same items")
    if n < 2:
        return math.nan
    _, ia = np.unique(np.asarray(a, dtype=object).astype(str), return_inverse=True)
    _, ib = np.unique(np.asarray(b, dtype=object).astype(str), return_inverse=True)
    table = np.zeros((ia.max() + 1, ib.max() + 1))
    np.add.at(table, (ia, ib), 1.0)
    sum_cells = _comb2(table).sum()
    sum_rows = _comb2(table.sum(axis=1)).sum()
    sum_cols = _comb2(table.sum(axis=0)).sum()
    expected = sum_rows * sum_cols / _comb2(n)
    maximum = (sum_rows + sum_cols) / 2.0
    if maximum == expected:
        return math.nan
    return float((sum_cells - expected) / (maximum - expected))


def _delta_ratio(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    total = a + b
    with np.errstate(divide="ignore", invalid="ignore"):
        d = np.where(total == 0, 0.0, ((a - b) / total) ** 2)
    return d


def krippendorff_alpha_ratio(units_by_raters: np.ndarray) -> float:
    """Krippendorff's alpha at ratio level for complete data (no missing values).

    `units_by_raters` has one row per unit (here: a pitch) and one column per rater
    (here: a repeated run of the same model, or a different model).
    """
    x = np.asarray(units_by_raters, dtype=float)
    n_units, m = x.shape
    if m < 2 or n_units < 2:
        raise ValueError("need at least two raters and two units")
    observed = 0.0
    for row in x:
        observed += _delta_ratio(row[:, None], row[None, :]).sum() / (m - 1)
    n_values = n_units * m
    d_o = observed / n_values
    flat = x.ravel()
    d_e = _delta_ratio(flat[:, None], flat[None, :]).sum() / (n_values * (n_values - 1))
    return float(1.0 - d_o / d_e)


def spearman_brown(single: float, k: int) -> float:
    """Reliability of the mean of k parallel measurements, given one measurement's reliability."""
    return float(k * single / (1.0 + (k - 1) * single))


def spearman(x: Iterable[float], y: Iterable[float]) -> float:
    """Spearman rank correlation with average ranks for ties."""
    xs = _rank(np.asarray(list(x), dtype=float))
    ys = _rank(np.asarray(list(y), dtype=float))
    if xs.std() == 0 or ys.std() == 0:
        return math.nan
    return float(np.corrcoef(xs, ys)[0, 1])


def _rank(v: np.ndarray) -> np.ndarray:
    order = np.argsort(v, kind="mergesort")
    ranks = np.empty(len(v), dtype=float)
    ranks[order] = np.arange(len(v), dtype=float)
    # average ranks for ties
    sorted_v = v[order]
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and sorted_v[j + 1] == sorted_v[i]:
            j += 1
        if j > i:
            ranks[order[i : j + 1]] = (i + j) / 2.0
        i = j + 1
    return ranks


def bootstrap_mean_ci(values: Sequence[float], n_boot: int = 2000, seed: int = 20261030, level: float = 0.95):
    """Percentile bootstrap interval for a mean, resampling units (pitches)."""
    v = np.asarray([x for x in values if not math.isnan(x)], dtype=float)
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, len(v), size=(n_boot, len(v)))].mean(axis=1)
    lo, hi = np.quantile(means, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(v.mean()), float(lo), float(hi)


def bootstrap_spearman_ci(x: Sequence[float], y: Sequence[float], n_boot: int = 2000, seed: int = 20261030, level: float = 0.95):
    xs, ys = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    rng = np.random.default_rng(seed)
    n = len(xs)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        vals.append(spearman(xs[idx], ys[idx]))
    vals = np.asarray([v for v in vals if not math.isnan(v)])
    lo, hi = np.quantile(vals, [(1 - level) / 2, 1 - (1 - level) / 2])
    return spearman(xs, ys), float(lo), float(hi)


def cohen_kappa(a: Sequence[Hashable], b: Sequence[Hashable]) -> float:
    """Cohen's kappa for two raters and nominal categories (unweighted)."""
    a, b = list(a), list(b)
    n = len(a)
    if n != len(b) or n == 0:
        raise ValueError("need two equally long, non-empty label lists")
    cats = sorted(set(a) | set(b), key=str)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return math.nan if pe == 1 else float((po - pe) / (1 - pe))


def bootstrap_kappa_ci(groups_a: Sequence[Sequence[Hashable]], groups_b: Sequence[Sequence[Hashable]],
                       n_boot: int = 2000, seed: int = 20261030, level: float = 0.95):
    """Kappa pooled over all items, with a bootstrap over groups (pitches), because items within a pitch are not independent."""
    rng = np.random.default_rng(seed)
    g = len(groups_a)
    point = cohen_kappa([x for grp in groups_a for x in grp], [x for grp in groups_b for x in grp])
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, g, size=g)
        a = [x for i in idx for x in groups_a[i]]
        b = [x for i in idx for x in groups_b[i]]
        v = cohen_kappa(a, b)
        if not math.isnan(v):
            vals.append(v)
    lo, hi = np.quantile(vals, [(1 - level) / 2, 1 - (1 - level) / 2])
    return point, float(lo), float(hi)
