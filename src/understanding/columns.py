"""Column-level statistics, routed by semantic type (requirement F: type routing)."""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from understanding.semantics import CATEGORICAL, NUMERIC, numeric_view, temporal_view


def _r(x, nd=4):
    if x is None:
        return None
    try:
        if isinstance(x, (np.integer,)):
            return int(x)
        x = float(x)
    except (TypeError, ValueError):
        return x
    if math.isnan(x) or math.isinf(x):
        return None
    return round(x, nd)


def _examples(s: pd.Series, k: int = 5) -> list[str]:
    vc = s.dropna().astype(str).value_counts()
    return [str(v) for v in vc.index[:k]]


def numeric_stats(s: pd.Series) -> dict[str, Any]:
    v = numeric_view(s).dropna()
    if v.empty:
        return {}
    q1, q3 = v.quantile([0.25, 0.75])
    iqr = q3 - q1
    far = ((v < q1 - 3 * iqr) | (v > q3 + 3 * iqr)) if iqr > 0 else pd.Series(False, index=v.index)
    counts, edges = np.histogram(v, bins=min(30, max(5, int(v.nunique()))) if v.nunique() < 30 else 30)
    return {
        "histogram": {"counts": [int(c) for c in counts], "edges": [_r(e) for e in edges]},
        "mean": _r(v.mean()), "median": _r(v.median()), "std": _r(v.std()),
        "min": _r(v.min()), "p01": _r(v.quantile(0.01)), "p25": _r(q1), "p75": _r(q3),
        "p99": _r(v.quantile(0.99)), "max": _r(v.max()),
        "skew": _r(v.skew()) if len(v) > 2 else None,
        "kurtosis": _r(v.kurt()) if len(v) > 3 else None,
        "zero_rate": _r((v == 0).mean()), "negative_rate": _r((v < 0).mean()),
        "far_outlier_rate": _r(far.mean()), "far_outlier_count": int(far.sum()),
    }


def categorical_stats(s: pd.Series) -> dict[str, Any]:
    nn = s.dropna().astype(str)
    if nn.empty:
        return {}
    vc = nn.value_counts()
    p = vc / vc.sum()
    entropy = float(-(p * np.log2(p)).sum())
    max_entropy = math.log2(len(vc)) if len(vc) > 1 else 0.0
    rare = vc[p < 0.01]
    return {
        "levels": int(len(vc)),
        "top": [{"value": str(k), "count": int(c), "rate": _r(c / vc.sum())} for k, c in vc.head(10).items()],
        "top_rate": _r(p.iloc[0]), "entropy_bits": _r(entropy),
        "normalized_entropy": _r(entropy / max_entropy) if max_entropy else 0.0,
        "rare_levels": int(len(rare)), "rare_level_rows": int(rare.sum()),
    }


def temporal_stats(s: pd.Series) -> dict[str, Any]:
    t = temporal_view(s).dropna().sort_values()
    if t.empty:
        return {}
    diffs = t.diff().dropna()
    diffs = diffs[diffs > pd.Timedelta(0)]
    per_month = t.dt.to_period("M").value_counts().sort_index()
    full = pd.period_range(per_month.index.min(), per_month.index.max(), freq="M") if len(per_month) else []
    empty_months = [str(m) for m in full if m not in per_month.index]
    return {
        "min": str(t.iloc[0]), "max": str(t.iloc[-1]),
        "span_days": _r((t.iloc[-1] - t.iloc[0]).total_seconds() / 86400, 2),
        "median_step_days": _r(diffs.median().total_seconds() / 86400, 4) if len(diffs) else None,
        "largest_gap_days": _r(diffs.max().total_seconds() / 86400, 2) if len(diffs) else None,
        "largest_gap_after": str(t.loc[diffs.idxmax()] - diffs.max()) if len(diffs) else None,
        "months_covered": int(len(per_month)), "empty_months": empty_months[:24],
        "rows_per_month_min": int(per_month.min()) if len(per_month) else None,
        "rows_per_month_max": int(per_month.max()) if len(per_month) else None,
        "monthly_counts": {str(k): int(v) for k, v in per_month.items()},
    }


def text_stats(s: pd.Series) -> dict[str, Any]:
    nn = s.dropna().astype(str)
    if nn.empty:
        return {}
    lens = nn.str.len()
    return {"mean_length": _r(lens.mean(), 1), "max_length": int(lens.max()),
            "blank_rate": _r((nn.str.strip() == "").mean())}


def profile_column(s: pd.Series, semantic: dict[str, Any]) -> dict[str, Any]:
    n = len(s)
    nulls = int(s.isna().sum())
    base = {
        "dtype": str(s.dtype), "count": n, "nulls": nulls, "null_rate": _r(nulls / n if n else 0),
        "distinct": int(s.nunique(dropna=True)),
        "distinct_rate": _r(s.nunique(dropna=True) / max(n - nulls, 1)),
        "examples": _examples(s),
    }
    t = semantic["type"]
    stats: dict[str, Any] = {}
    if t in NUMERIC or (t == "numeric_coded"):
        stats["numeric"] = numeric_stats(s)
    if t in CATEGORICAL or t in ("identifier",):
        stats["categorical"] = categorical_stats(s) if t != "identifier" else {}
    if t == "temporal":
        stats["temporal"] = temporal_stats(s)
    if t in ("free_text", "identifier", "email", "phone", "url") and not pd.api.types.is_numeric_dtype(s):
        stats["text"] = text_stats(s)
    base["stats"] = {k: v for k, v in stats.items() if v}
    return base
