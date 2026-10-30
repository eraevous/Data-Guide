"""Screen every eligible pair with a type-appropriate measure; report only the strongest (requirement C).

Measures (all reported as an absolute effect between 0 and 1):
- numeric × numeric: Spearman's rho;
- categorical × numeric: correlation ratio eta (for a binary category, the same ordering as point-biserial);
- categorical × categorical: bias-corrected Cramér's V.

Association is not causation, and screening many pairs produces some strong-looking pairs by chance.
The report says how many pairs were screened.
"""
from __future__ import annotations

import itertools
import math
from typing import Any

import numpy as np
import pandas as pd

from understanding.semantics import CATEGORICAL, NUMERIC, numeric_view

MAX_ROWS = 50_000
MAX_LEVELS = 50


def _cat(s: pd.Series) -> pd.Series:
    return s.astype("string")


def spearman(x: pd.Series, y: pd.Series) -> tuple[float | None, int]:
    m = x.notna() & y.notna()
    if m.sum() < 10 or x[m].nunique() < 2 or y[m].nunique() < 2:
        return None, int(m.sum())
    return float(x[m].rank().corr(y[m].rank())), int(m.sum())


def correlation_ratio(cat: pd.Series, num: pd.Series) -> tuple[float | None, int]:
    m = cat.notna() & num.notna()
    if m.sum() < 10:
        return None, int(m.sum())
    c, v = cat[m], num[m]
    if c.nunique() < 2 or c.nunique() > MAX_LEVELS or v.var() == 0:
        return None, int(m.sum())
    grand = v.mean()
    groups = v.groupby(c, observed=True)
    ss_between = float((groups.count() * (groups.mean() - grand) ** 2).sum())
    ss_total = float(((v - grand) ** 2).sum())
    return (math.sqrt(ss_between / ss_total) if ss_total > 0 else None), int(m.sum())


def cramers_v(a: pd.Series, b: pd.Series) -> tuple[float | None, int]:
    m = a.notna() & b.notna()
    n = int(m.sum())
    if n < 10 or a[m].nunique() < 2 or b[m].nunique() < 2:
        return None, n
    if a[m].nunique() > MAX_LEVELS or b[m].nunique() > MAX_LEVELS:
        return None, n
    table = pd.crosstab(a[m], b[m]).to_numpy(dtype=float)
    expected = table.sum(1, keepdims=True) * table.sum(0, keepdims=True) / n
    chi2 = float(((table - expected) ** 2 / np.where(expected == 0, 1, expected)).sum())
    r, k = table.shape
    phi2 = chi2 / n
    phi2c = max(0.0, phi2 - (k - 1) * (r - 1) / (n - 1))
    rc, kc = r - (r - 1) ** 2 / (n - 1), k - (k - 1) ** 2 / (n - 1)
    denom = min(kc - 1, rc - 1)
    return (math.sqrt(phi2c / denom) if denom > 0 else None), n


def _groups(views, semantics, cols, target):
    """Small per-group summary so reports can show the relation without the raw data."""
    a, b = cols
    na, nb = semantics[a]["type"] in NUMERIC, semantics[b]["type"] in NUMERIC
    if na and nb:
        return None
    if target in cols and not (na and nb):
        outcome = target
        group = b if a == target else a
    elif na or nb:
        outcome, group = (a, b) if na else (b, a)
    else:
        outcome, group = b, a
    g, y = views[group], views[outcome]
    if semantics[group]["type"] in NUMERIC:
        g = pd.qcut(g, 5, duplicates="drop").astype("string")
    if semantics[outcome]["type"] not in NUMERIC:
        levels = y.dropna().value_counts()
        if len(levels) != 2:
            return None
        pos = sorted(levels.index)[-1]
        y = (y == pos).astype(float).where(y.notna())
        label = f"share {outcome} = {pos}"
    else:
        label = f"mean {outcome}"
    m = g.notna() & y.notna()
    s = y[m].groupby(g[m], observed=True).agg(["mean", "count"]).sort_values("count", ascending=False).head(12)
    return {"by": group, "measure": label,
            "rows": [{"group": str(k), "value": round(float(r["mean"]), 4), "n": int(r["count"])} for k, r in s.iterrows()]}


def strength(effect: float) -> str:
    return "strong" if effect >= 0.5 else "moderate" if effect >= 0.3 else "weak" if effect >= 0.1 else "negligible"


def screen(df: pd.DataFrame, semantics: dict[str, dict], target: str | None = None, top_k: int = 10,
           budget: int = 300, exclude: set | None = None) -> dict[str, Any]:
    """Select candidate pairs (target first, within a budget), compute them, and say what was left out and why."""
    if len(df) > MAX_ROWS:
        df = df.sample(MAX_ROWS, random_state=0)
    excluded, cols = [], []
    for c in df.columns:
        t = semantics[c]["type"]
        if exclude and c in exclude:
            excluded.append({"column": c, "reason": "period column of a wide table: compare periods after reshaping"})
        elif t not in NUMERIC | CATEGORICAL:
            excluded.append({"column": c, "reason": f"{t.replace('_', ' ')}: no association measure applies"})
        elif t in CATEGORICAL and df[c].nunique() > MAX_LEVELS:
            excluded.append({"column": c, "reason": f"{df[c].nunique()} levels: too many for a reliable association"})
        elif df[c].notna().sum() < 10:
            excluded.append({"column": c, "reason": "fewer than 10 non-null values"})
        else:
            cols.append(c)
    views = {c: numeric_view(df[c]) if semantics[c]["type"] in NUMERIC else _cat(df[c]) for c in cols}
    candidates = list(itertools.combinations(sorted(cols), 2))
    if target in cols:
        candidates.sort(key=lambda ab: 0 if target in ab else 1)
    considered = len(candidates)
    chosen, deferred = candidates[:budget], candidates[budget:]
    pairs = []
    skipped = 0
    for a, b in chosen:
        ta, tb = semantics[a]["type"], semantics[b]["type"]
        na, nb = ta in NUMERIC, tb in NUMERIC
        if na and nb:
            eff, n = spearman(views[a], views[b])
            method, signed = "spearman_rho", eff
            eff = abs(eff) if eff is not None else None
        elif na or nb:
            cat, num = (b, a) if na else (a, b)
            eff, n = correlation_ratio(views[cat], views[num])
            method, signed = "correlation_ratio_eta", None
        else:
            eff, n = cramers_v(views[a], views[b])
            method, signed = "cramers_v_bias_corrected", None
        if eff is None or math.isnan(eff):
            skipped += 1
            continue
        levels = {c: int(views[c].nunique()) for c in (a, b) if semantics[c]["type"] in CATEGORICAL}
        pairs.append({"columns": [a, b], "method": method, "effect": round(eff, 4),
                      "signed": round(signed, 4) if signed is not None else None,
                      "strength": strength(eff), "n": n, "levels": levels,
                      "involves_target": bool(target and target in (a, b))})
    pairs.sort(key=lambda p: (-p["effect"], p["columns"]))
    top = [p for p in pairs if p["strength"] != "negligible"][:top_k]
    target_pairs = [p for p in pairs if p["involves_target"]][:top_k] if target else []
    for p in {id(x): x for x in top + target_pairs}.values():
        p["groups"] = _groups(views, semantics, p["columns"], target)
    return {"considered": considered, "screened": len(chosen), "computed": len(pairs), "skipped": skipped,
            "not_computed_budget": len(deferred), "budget": budget, "excluded_columns": excluded,
            "eligible_columns": len(cols), "rows_used": int(len(df)), "top_k": top_k, "negligible_omitted": sum(1 for p in pairs if p["strength"] == "negligible"),
            "top": top, "target": target, "target_pairs": target_pairs,
            "caution": ("Associations, not causes. Ranking by strength is a convenience: the strongest pair is not necessarily the most useful one, "
                        "and with many pairs screened some strong-looking ones arise by chance. Check group sizes for many-level categories.")}
