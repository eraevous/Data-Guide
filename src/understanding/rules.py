"""Deterministic rules that turn statistics into typed findings.

Each rule names its kind honestly:
- what is measured is an *observation*;
- a reading of a measurement is an *interpretation*;
- a possible cause is a *hypothesis*;
- a suggestion is an *action*;
- anything the table cannot settle is a *question*.

Rules never state domain meaning.
"""
from __future__ import annotations

import itertools
import re
from typing import Any

import pandas as pd

from understanding.findings import Finding

SENTINEL_NUMBERS = (-1, -9, -99, -999, -9999, 99, 999, 9999, 99999)
SENTINEL_TEXT = {"n/a", "na", "null", "none", "nil", "-", "--", "?", "unknown", "missing", "nan", "#n/a", ""}
AGGREGATE = re.compile(r"\b(total|subtotal|grand total|all|overall|world|average|sum|aggregate|income levels?|region|"
                       r"members|classification|countries|small states|union|area)\b|&", re.I)
TEST_TEXT = {"test", "dummy", "sample", "xxx", "asdf", "tbd", "placeholder", "do not use", "lorem ipsum"}


PERIOD_NAME = re.compile(r"^(1[89]\d{2}|20\d{2})([-_/ ]?(0?[1-9]|1[0-2]|q[1-4]))?$", re.I)
COLLAPSIBLE = {"missing", "missing-high", "skew", "near-duplicate", "association", "co-missing", "far-outliers",
               "zero-inflated", "sentinel-number"}


def period_columns(df: pd.DataFrame, semantics: dict) -> list[str]:
    """Columns named like periods (years, year-months, quarters) holding the same kind of value: a wide time series."""
    cols = [c for c in df.columns if PERIOD_NAME.match(str(c).strip())]
    types = {semantics[c]["type"] for c in cols} - {"empty", "constant"}
    if len(cols) >= 5 and len(types) <= 2:
        return cols
    return []


def shape_rules(df: pd.DataFrame, periods: list[str]) -> tuple[list[Finding], dict]:
    if not periods:
        return [], {"form": "rows-as-records"}
    rates = {c: round(float(df[c].isna().mean()), 4) for c in periods}
    first, last = periods[0], periods[-1]
    worst = max(rates, key=lambda c: (rates[c], c))
    others = [c for c in df.columns if c not in periods]
    out = [
        Finding("observation", "wide-by-period", f"{len(periods)} columns are named like periods ({first} to {last}), and their inferred types match.",
                subjects=periods, evidence={"period_columns": len(periods), "first": first, "last": last}),
        Finding("observation", "missing-by-period", f"Missing values by period: {rates[first]:.0%} in {first}, {rates[last]:.0%} in {last}, "
                f"highest {rates[worst]:.0%} in {worst}.", subjects=periods, evidence={"null_rate_by_period": rates}),
        Finding("interpretation", "wide-by-period", f"This is probably a wide table, one column per period; the other columns "
                f"({', '.join(map(str, others[:4])) or 'none'}) would identify each row. "
                "Treating each period column as a separate variable makes neighbouring periods look like "
                "near-duplicates and splits one measure into many; per-column findings for these columns are summarised instead.",
                subjects=periods, based_on=["wide-by-period"]),
        Finding("action", "wide-by-period", f"Reshape to one row per {(others[0] if others else 'entity')} and period, re-profile, and compare.",
                subjects=periods, based_on=["wide-by-period"]),
    ]
    if rates[last] > rates[first] + 0.1:
        out.append(Finding("question", "missing-by-period", f"Are the later periods missing because data had not been published yet when "
                           f"this was extracted, or because collection stopped?", subjects=periods, based_on=["missing-by-period"]))
    return out, {"form": "wide-by-period", "period_columns": periods}


def dataset_rules(df: pd.DataFrame, semantics: dict, declared: dict) -> tuple[list[Finding], dict]:
    out: list[Finding] = []
    n = len(df)
    dups = int(df.duplicated().sum())
    if dups:
        out.append(Finding("observation", "duplicate-rows", f"{dups} rows ({dups / n:.1%}) are exact duplicates of another row.",
                           evidence={"duplicate_rows": dups, "rate": round(dups / n, 4)}, confidence="high"))
        out.append(Finding("question", "duplicate-rows", "Are duplicate rows real repeated events, or artifacts of extraction or joins?",
                           based_on=["duplicate-rows"]))

    # Candidate keys and row unit.
    key_types = ("identifier", "categorical", "temporal", "numeric_count", "numeric_coded", "email", "phone", "url")
    keys = [c for c in df.columns if semantics[c]["type"] in key_types and df[c].notna().all() and df[c].is_unique]
    pair_keys: list[list[str]] = []
    if not keys:
        cand = [c for c in df.columns if semantics[c]["type"] in ("identifier", "categorical", "temporal", "numeric_coded", "binary")
                and df[c].notna().all()][:12]
        for a, b in itertools.combinations(cand, 2):
            if not df.duplicated([a, b]).any():
                pair_keys.append([a, b])
            if len(pair_keys) >= 3:
                break
    register: dict[str, Any] = {"candidate_keys": keys, "candidate_compound_keys": pair_keys}
    row_unit = declared.get("row_unit")
    if row_unit:
        register["row_unit"] = {"value": row_unit, "source": "human"}
    elif keys:
        register["row_unit"] = {"value": None, "source": "unknown"}
        out.append(Finding("hypothesis", "row-unit", f"Each row may be one '{keys[0]}' (unique and never null)"
                           + (f"; other candidate keys: {', '.join(keys[1:4])}" if len(keys) > 1 else "") + ".",
                           subjects=keys[:4], evidence={"candidate_keys": keys}, confidence="medium"))
    else:
        register["row_unit"] = {"value": None, "source": "unknown"}
        detail = f" Unique column pairs: {', '.join('+'.join(p) for p in pair_keys)}." if pair_keys else " No single column or simple pair is unique."
        out.append(Finding("question", "row-unit", "What does one row represent?" + detail,
                           evidence={"candidate_compound_keys": pair_keys}, confidence="high"))
    if not row_unit:
        out.append(Finding("question", "row-unit-unstated", "The row unit (what one row represents) is not stated; counts and rates depend on it.",
                           confidence="high"))

    if not declared.get("generating_process"):
        out.append(Finding("question", "generating-process",
                           "How were these rows produced: which system, which filters, and what is excluded? This table cannot say.",
                           confidence="high"))

    # Shared missingness patterns.
    masks: dict[tuple, list[str]] = {}
    for c in df.columns:
        m = df[c].isna()
        if 0 < m.sum() < n:
            masks.setdefault(tuple(m.to_numpy()), []).append(c)
    for cols in sorted((v for v in masks.values() if len(v) > 1), key=lambda v: (-len(v), v)):
        rate = float(df[cols[0]].isna().mean())
        out.append(Finding("observation", "co-missing", f"{len(cols)} columns are missing on exactly the same {rate:.1%} of rows: {', '.join(cols)}.",
                           subjects=cols, evidence={"null_rate": round(rate, 4)}, confidence="high"))
        out.append(Finding("hypothesis", "co-missing", f"These {len(cols)} columns may come from one collection step or join that sometimes did not happen; "
                           "if so, the missingness is structural rather than random.", subjects=cols, based_on=["co-missing"], confidence="medium"))
    out += missing_by_group(df, semantics)
    return out, register


def missing_by_group(df: pd.DataFrame, semantics: dict, max_levels: int = 60, min_group: int = 30,
                     min_v: float = 0.15, alpha: float = 0.01, max_groupers: int = 15, max_rows: int = 50_000) -> list[Finding]:
    """Where a column's missingness varies with another column (for example a period), test it before saying so.

    For each missing-value column and each candidate grouping column, a chi-square test is run on the
    missing x group table, using only groups of at least `min_group` rows. The alpha level is
    Bonferroni-adjusted for every test run. The effect size is Cramer's V, and only effects of
    at least `min_v` are reported.
    """
    from scipy.stats import chi2_contingency

    if len(df) > max_rows:
        df = df.sample(max_rows, random_state=0)
    groupers = [c for c in df.columns if semantics[c]["type"] in ("categorical", "binary", "numeric_coded", "numeric_count", "temporal")
                and 2 <= df[c].nunique() <= max_levels and df[c].notna().all()][:max_groupers]
    targets = [c for c in df.columns if 0.02 <= df[c].isna().mean() <= 0.98]
    tests = []
    for c in targets:
        m = df[c].isna()
        for g in groupers:
            if g == c:
                continue
            sizes = df[g].value_counts()
            keep = sizes[sizes >= min_group].index
            if len(keep) < 2:
                continue
            sel = df[g].isin(keep)
            table = pd.crosstab(df.loc[sel, g], m[sel])
            if table.shape[1] < 2:
                continue
            chi2, pval, dof, _ = chi2_contingency(table, correction=False)
            v = (chi2 / (table.to_numpy().sum() * (min(table.shape) - 1))) ** 0.5
            tests.append((c, g, float(pval), float(v), m[sel].groupby(df.loc[sel, g]).mean()))
    out = []
    threshold = alpha / max(len(tests), 1)
    best: dict[str, tuple] = {}
    for c, g, pval, v, rates in tests:
        if pval < threshold and v >= min_v and (c not in best or v > best[c][3]):
            best[c] = (c, g, pval, v, rates)
    for c, g, pval, v, rates in best.values():
        hi, lo = rates.idxmax(), rates.idxmin()
        ev = {"cramers_v": round(v, 4), "p_value": float(f"{pval:.3g}"), "bonferroni_threshold": float(f"{threshold:.3g}"),
              "tests_run": len(tests), "min_group_size": min_group, "highest": [str(hi), round(float(rates.max()), 4)],
              "lowest": [str(lo), round(float(rates.min()), 4)], "by_group": {str(k): round(float(x), 4) for k, x in rates.items()}}
        out.append(Finding("observation", "missing-by-group", f"Missingness in '{c}' varies with '{g}': {rates.max():.0%} missing when "
                           f"{g} = {hi}, {rates.min():.0%} when {g} = {lo} (chi-square p {'< 0.001' if pval < 0.001 else '= ' + str(ev['p_value'])}, Cramer's V {ev['cramers_v']}; "
                           f"{len(tests)} tests, Bonferroni-adjusted).", subjects=[c, g], evidence=ev))
        out.append(Finding("interpretation", "missing-by-group", f"Missingness in '{c}' is associated with '{g}', so it is unlikely to be missing "
                           f"completely at random: dropping or imputing its missing rows changes the mix of '{g}'.", subjects=[c, g],
                           based_on=["missing-by-group"]))
        out.append(Finding("question", "missing-by-group", f"Why is '{c}' missing more often for some values of '{g}'?",
                           subjects=[c, g], based_on=["missing-by-group"]))
    return out


def column_rules(name: str, s: pd.Series, sem: dict, prof: dict, annot: dict) -> list[Finding]:
    out: list[Finding] = []
    t = sem["type"]
    st = prof.get("stats", {})
    nr = prof["null_rate"] or 0
    subj = [name]

    if nr > 0:
        level = "high" if nr >= 0.5 else "medium" if nr >= 0.1 else "low"
        out.append(Finding("observation", "missing", f"{nr:.1%} of '{name}' is missing ({prof['nulls']} rows).",
                           subjects=subj, evidence={"null_rate": nr, "nulls": prof["nulls"], "level": level}, confidence="high"))
        if nr >= 0.5:
            out.append(Finding("action", "missing-high", f"Before using '{name}', find out why it is mostly empty; imputing it would mostly invent values.",
                               subjects=subj, based_on=["missing"]))
    if t == "constant":
        out.append(Finding("observation", "constant", f"'{name}' has a single value ({prof['examples'][0] if prof['examples'] else ''!s}).",
                           subjects=subj, confidence="high"))
        out.append(Finding("action", "constant", f"'{name}' carries no information in this extract; check whether a filter fixed it before dropping it.",
                           subjects=subj, based_on=["constant"]))
    if t == "empty":
        out.append(Finding("observation", "empty", f"'{name}' has no values.", subjects=subj, confidence="high"))

    if sem.get("source") == "inferred" and sem.get("confidence") == "low":
        out.append(Finding("question", "semantic-uncertain",
                           f"'{name}' was read as {t.replace('_', ' ')} with low confidence ({'; '.join(sem['reasons'])}). "
                           f"Alternatives: {', '.join(sem['alternatives']) or 'none'}. What is it?", subjects=subj))
    if t == "numeric_as_text":
        out.append(Finding("observation", "numeric-as-text", f"'{name}' is stored as text but its values are numbers.",
                           subjects=subj, evidence={"dtype": prof["dtype"]}, confidence="high"))

    num = st.get("numeric") or {}
    if num.get("inf_count"):
        out.append(Finding("observation", "infinite-values", f"{num['inf_count']} values of '{name}' are infinite; they are excluded from "
                           "the statistics above.", subjects=subj, evidence={"inf_count": num["inf_count"]}))
    if num.get("median") is not None:
        skew = num.get("skew")
        if skew is not None and abs(skew) >= 1:
            side = "right" if skew > 0 else "left"
            out.append(Finding("observation", "skew", f"'{name}' is strongly {side}-skewed (skew {skew}); median {num['median']} vs mean {num['mean']}.",
                               subjects=subj, evidence={"skew": skew, "mean": num["mean"], "median": num["median"]}, confidence="high"))
            pull = "a few large values pull it up" if skew > 0 else "a few small values pull it down"
            out.append(Finding("interpretation", "skew", f"The mean of '{name}' is a misleading summary; {pull}. "
                               "Medians, quantiles or a log scale describe it better.", subjects=subj, based_on=["skew"]))
        if (num.get("zero_rate") or 0) >= 0.3:
            out.append(Finding("observation", "zero-inflated", f"{num['zero_rate']:.0%} of '{name}' values are exactly zero.",
                               subjects=subj, evidence={"zero_rate": num["zero_rate"]}, confidence="high"))
            out.append(Finding("question", "zero-inflated", f"Does a zero in '{name}' mean 'none', 'not recorded', or 'not applicable'?",
                               subjects=subj, based_on=["zero-inflated"]))
        if (num.get("far_outlier_count") or 0) > 0:
            out.append(Finding("observation", "far-outliers", f"{num['far_outlier_count']} values of '{name}' lie beyond 3×IQR from the quartiles "
                               f"(range {num['min']} to {num['max']}).", subjects=subj,
                               evidence={"count": num["far_outlier_count"], "min": num["min"], "max": num["max"]}, confidence="high"))
        if t in ("numeric_count",) and (num.get("negative_rate") or 0) > 0:
            out.append(Finding("observation", "negative-in-count", f"'{name}' looks like a count but has negative values.", subjects=subj))
        vals = pd.to_numeric(s, errors="coerce").dropna()
        if len(vals):
            for sentinel in SENTINEL_NUMBERS:
                share = float((vals == sentinel).mean())
                extreme = sentinel in (vals.min(), vals.max())
                if share >= 0.005 and extreme:
                    out.append(Finding("observation", "sentinel-number", f"{share:.1%} of '{name}' equals {sentinel}, the column's "
                                       f"{'minimum' if sentinel == vals.min() else 'maximum'}.", subjects=subj,
                                       evidence={"value": sentinel, "rate": round(share, 4)}, confidence="high"))
                    out.append(Finding("hypothesis", "sentinel-number", f"{sentinel} in '{name}' may be a code for missing or not applicable; "
                                       "if so, it distorts the statistics for this column.", subjects=subj, based_on=["sentinel-number"]))
                    out.append(Finding("action", "sentinel-number", f"If {sentinel} means missing, recode it in '{name}', re-profile, and compare "
                                       "the two artifacts (guide compare).", subjects=subj, based_on=["sentinel-number"]))
                    break

    cat = st.get("categorical") or {}
    if cat:
        if (cat.get("top_rate") or 0) >= 0.9:
            top = cat["top"][0]
            out.append(Finding("observation", "dominant-level", f"'{name}' is {top['rate']:.0%} '{top['value']}'.", subjects=subj,
                               evidence={"value": top["value"], "rate": top["rate"]}, confidence="high"))
        if cat.get("rare_levels", 0) >= 5 and (cat.get("normalized_entropy") or 0) < 0.95:
            out.append(Finding("observation", "rare-levels", f"'{name}' has {cat['rare_levels']} levels each under 1% of rows "
                               f"({cat['rare_level_rows']} rows in total).", subjects=subj,
                               evidence={"rare_levels": cat["rare_levels"], "rows": cat["rare_level_rows"]}, confidence="high"))
    if not pd.api.types.is_numeric_dtype(s):
        text = s.dropna().astype(str).str.strip().str.lower()
        if len(text):
            sentinels = sorted(set(text.unique()) & SENTINEL_TEXT)
            if sentinels:
                rate = float(text.isin(sentinels).mean())
                out.append(Finding("observation", "missing-as-text", f"'{name}' contains text that usually means missing "
                                   f"({', '.join(repr(x) for x in sentinels)}) in {rate:.1%} of non-null rows.", subjects=subj,
                                   evidence={"values": sentinels, "rate": round(rate, 4)}, confidence="high"))
            tests = sorted(v for v in text.unique() if v in TEST_TEXT or v.startswith("test"))
            if tests:
                out.append(Finding("observation", "test-values", f"'{name}' contains test or dummy-looking values: {', '.join(repr(x) for x in tests[:5])}.",
                                   subjects=subj, evidence={"values": tests[:10]}, confidence="medium"))
                out.append(Finding("action", "test-values", f"Decide whether to exclude rows with test values in '{name}' before computing rates.",
                                   subjects=subj, based_on=["test-values"]))

    if t in ("identifier", "categorical") and not pd.api.types.is_numeric_dtype(s):
        labels = s.dropna().astype(str).unique()
        agg = sorted(v for v in labels if AGGREGATE.search(v))
        if 2 <= len(agg) and len(agg) / max(len(labels), 1) <= 0.5:
            out.append(Finding("observation", "aggregate-labels", f"{len(agg)} values of '{name}' read like totals or groupings: "
                               f"{', '.join(repr(x) for x in agg[:6])}{' …' if len(agg) > 6 else ''}.", subjects=subj,
                               evidence={"values": agg[:30], "count": len(agg)}))
            out.append(Finding("hypothesis", "aggregate-labels", f"Some rows may be aggregates of other rows (labelled in '{name}'); "
                               "if so, sums and averages over all rows count the same things twice.", subjects=subj, based_on=["aggregate-labels"]))
            out.append(Finding("question", "aggregate-labels", f"Which values of '{name}' are individual units, and which are groups of them?",
                               subjects=subj, based_on=["aggregate-labels"]))

    tem = st.get("temporal") or {}
    if tem:
        if tem.get("empty_months"):
            out.append(Finding("observation", "temporal-gap", f"'{name}' spans {tem['min'][:10]} to {tem['max'][:10]} with "
                               f"{len(tem['empty_months'])} empty month(s): {', '.join(tem['empty_months'][:6])}.", subjects=subj,
                               evidence={"empty_months": tem["empty_months"]}, confidence="high"))
            out.append(Finding("question", "temporal-gap", f"Are the empty months in '{name}' real (no activity) or missing extracts?",
                               subjects=subj, based_on=["temporal-gap"]))
        lo, hi = tem.get("rows_per_month_min"), tem.get("rows_per_month_max")
        if lo and hi and tem.get("months_covered", 0) >= 3 and hi / lo >= 3:
            out.append(Finding("observation", "volume-shift", f"Monthly volume in '{name}' ranges from {lo} to {hi} rows.", subjects=subj,
                               evidence={"min": lo, "max": hi}, confidence="high"))

    a = annot or {}
    if a.get("note"):
        out.append(Finding("interpretation", "annotation", a["note"], subjects=subj, generator="human", confidence="medium"))
    return out


def relation_rules(rel: dict, target: str | None) -> list[Finding]:
    out: list[Finding] = []
    for p in rel["top"]:
        a, b = p["columns"]
        if p["effect"] >= 0.95 and p["method"] == "spearman_rho":
            out.append(Finding("observation", "near-duplicate", f"'{a}' and '{b}' move almost in lockstep (|rho| {p['effect']}).",
                               subjects=[a, b], evidence=p, confidence="high"))
            out.append(Finding("action", "near-duplicate", f"Keep one of '{a}' and '{b}' in any model; together they double-count one signal.",
                               subjects=[a, b], based_on=["near-duplicate"]))
            out.append(Finding("question", "near-duplicate", f"Are '{a}' and '{b}' the same quantity recorded twice, or one derived from the other?",
                               subjects=[a, b], based_on=["near-duplicate"]))
        elif p["strength"] in ("strong", "moderate") and not p["involves_target"]:
            direction = ""
            if p.get("signed") is not None:
                direction = f"; higher '{a}' goes with {'higher' if p['signed'] > 0 else 'lower'} '{b}'"
            out.append(Finding("observation", "association", f"'{a}' and '{b}' are {p['strength']}ly associated ({p['method']} {p['signed'] if p.get('signed') is not None else p['effect']}, n={p['n']}{direction}).",
                               subjects=[a, b], evidence=p, confidence="medium"))
    for p in rel.get("target_pairs", []):
        if p["strength"] == "negligible":
            continue
        other = p["columns"][0] if p["columns"][1] == target else p["columns"][1]
        out.append(Finding("observation", "target-association", f"'{other}' is {p['strength']}ly associated with the target '{target}' "
                           f"({p['method']} {p['effect']}, n={p['n']}).", subjects=[other, target], evidence=p,
                           confidence="medium", relevance="target"))
        if p["effect"] >= 0.8:
            out.append(Finding("hypothesis", "possible-leakage", f"'{other}' is so strongly tied to '{target}' that it may be recorded after, "
                               "or be derived from, the outcome. Check its timing before using it as a predictor.",
                               subjects=[other, target], based_on=["target-association"], relevance="target"))
    return out
