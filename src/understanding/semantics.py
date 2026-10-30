"""Semantic type inference with confidence, reasons and alternatives (requirement B).

An inferred type is a guess about meaning made from values and names. It is reported as
``source: inferred``, with the reasons behind it. A human annotation replaces it and is
reported as ``source: human``. Nothing here is a domain fact.
"""
from __future__ import annotations

import re
import warnings
from typing import Any

import numpy as np
import pandas as pd

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PHONE = re.compile(r"^\+?[\d\s().-]{7,}$")
URL = re.compile(r"^https?://\S+$", re.I)
ID_NAME = re.compile(r"(^id$|_id$|^id_|uuid|guid|_key$|^key$|_no$|number$|_code$)", re.I)
DATE_NAME = re.compile(r"(date|time|_at$|_on$|dt$|day|month|year)", re.I)

SEMANTIC_TYPES = ("constant", "identifier", "binary", "boolean", "temporal", "numeric_continuous",
                  "numeric_count", "numeric_coded", "categorical", "free_text", "email", "phone",
                  "url", "numeric_as_text", "empty", "nested")
ANALYZABLE = {"binary", "boolean", "numeric_continuous", "numeric_count", "numeric_coded",
              "categorical", "numeric_as_text"}
NUMERIC = {"numeric_continuous", "numeric_count", "numeric_as_text"}
CATEGORICAL = {"binary", "boolean", "categorical", "numeric_coded"}


def _rate(values: pd.Series, pattern: re.Pattern) -> float:
    if values.empty:
        return 0.0
    return float(values.astype(str).str.strip().str.match(pattern).mean())


def _parse_dates(values: pd.Series) -> pd.Series:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for kw in ({"format": "mixed"}, {"format": "mixed", "utc": True}, {"utc": True}):
            try:
                return pd.to_datetime(values, errors="coerce", **kw)
            except (TypeError, ValueError):
                continue
        return pd.Series(pd.NaT, index=values.index)


def numeric_view(s: pd.Series) -> pd.Series:
    """Numeric values of a column, parsing text where needed (NaN where not numeric)."""
    if pd.api.types.is_bool_dtype(s):
        return s.astype(float)
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)
    return pd.to_numeric(s.astype(str).str.replace(",", "", regex=False).str.strip(), errors="coerce")


def temporal_view(s: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(s):
        return s.dt.tz_convert("UTC") if getattr(s.dt, "tz", None) is not None else s
    return _parse_dates(s.astype(str).where(s.notna()))


def infer(name: str, s: pd.Series, n_rows: int) -> dict[str, Any]:
    """Return {type, confidence, reasons, alternatives, source}."""
    nn = s.dropna()
    n = len(nn)
    reasons: list[str] = []
    alts: list[str] = []

    def out(t, conf):
        return {"type": t, "confidence": conf, "reasons": reasons, "alternatives": alts,
                "source": "inferred"}

    if n == 0:
        reasons.append("no non-null values")
        return out("empty", "high")
    if nn.map(lambda v: isinstance(v, (list, dict, set, tuple))).any():
        reasons.append("cells hold nested values (lists or mappings)")
        return out("nested", "high")
    if pd.api.types.is_datetime64_any_dtype(s):
        reasons.append("datetime dtype")
        return out("temporal", "high")
    nunique = int(nn.nunique())
    uniq_ratio = nunique / n
    if nunique == 1:
        reasons.append(f"a single distinct value ({nn.iloc[0]!r})")
        return out("constant", "high")
    if pd.api.types.is_bool_dtype(s):
        reasons.append("boolean dtype")
        return out("boolean", "high")
    if nunique == 2:
        reasons.append("exactly two distinct values")
        alts.append("categorical")
        return out("binary", "high")
    if pd.api.types.is_numeric_dtype(s):
        vals = nn.astype(float)
        is_int = bool(np.all(np.isclose(vals, np.round(vals))))
        if ID_NAME.search(name) and uniq_ratio > 0.95:
            reasons.append(f"name looks like an identifier and {uniq_ratio:.0%} of values are unique")
            alts.append("numeric_count")
            return out("identifier", "medium")
        if is_int and uniq_ratio > 0.99 and n > 50 and vals.is_monotonic_increasing:
            reasons.append("unique, increasing integers (row number or sequence id)")
            return out("identifier", "medium")
        if is_int and nunique <= 10 and n >= 30:
            reasons.append(f"integers with only {nunique} distinct values: could be codes or small counts")
            alts.append("numeric_count")
            return out("numeric_coded", "low")
        if is_int and vals.min() >= 0:
            reasons.append("non-negative integers")
            alts.append("numeric_continuous")
            return out("numeric_count", "medium")
        reasons.append("numeric dtype with fractional or negative values")
        return out("numeric_continuous", "high")

    text = nn.astype(str).str.strip()
    sample = text.sample(min(len(text), 2000), random_state=0) if len(text) > 2000 else text
    for t, pat in (("email", EMAIL), ("url", URL)):
        r = _rate(sample, pat)
        if r >= 0.8:
            reasons.append(f"{r:.0%} of values match the {t} pattern")
            return out(t, "high" if r > 0.95 else "medium")
    num_rate = float(numeric_view(sample).notna().mean())
    if num_rate >= 0.95:
        reasons.append(f"{num_rate:.0%} of text values parse as numbers")
        alts.append("categorical")
        return out("numeric_as_text", "medium")
    date_rate = float(_parse_dates(sample).notna().mean()) if (DATE_NAME.search(name) or sample.str.contains(r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}").mean() > 0.5) else 0.0
    if date_rate >= 0.9:
        reasons.append(f"{date_rate:.0%} of values parse as dates")
        return out("temporal", "high" if date_rate > 0.98 else "medium")
    phone_rate = _rate(sample, PHONE)
    if phone_rate >= 0.8 and not sample.str.match(r"^\d{4}-\d{2}-\d{2}").mean() > 0.5 and sample.str.count(r"\d").mean() >= 7:
        reasons.append(f"{phone_rate:.0%} of values look like phone numbers")
        return out("phone", "medium")
    if uniq_ratio > 0.95 and n > 20:
        mean_len = float(sample.str.len().mean())
        spaces = float(sample.str.contains(r"\s").mean())
        if mean_len > 30 or spaces > 0.5:
            reasons.append(f"mostly unique text, mean length {mean_len:.0f} characters")
            return out("free_text", "medium")
        reasons.append(f"{uniq_ratio:.0%} of values are unique short strings")
        alts.append("free_text")
        return out("identifier", "medium" if ID_NAME.search(name) else "low")
    limit = max(20, int(0.05 * n_rows))
    if nunique <= limit:
        reasons.append(f"{nunique} distinct values")
        return out("categorical", "high" if nunique <= 20 else "medium")
    mean_len = float(sample.str.len().mean())
    if mean_len > 30:
        reasons.append(f"many distinct values, mean length {mean_len:.0f} characters")
        return out("free_text", "medium")
    reasons.append(f"{nunique} distinct values: too many to treat as ordinary categories")
    alts.extend(["identifier", "free_text"])
    return out("categorical", "low")


def apply_override(inferred: dict[str, Any], declared: str | None) -> dict[str, Any]:
    if not declared:
        return inferred
    return {"type": declared, "confidence": "declared", "reasons": ["stated in annotations"],
            "alternatives": [], "source": "human", "inferred": inferred}
