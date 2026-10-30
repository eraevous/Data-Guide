"""Before/after comparison of two understanding artifacts (requirement D)."""
from __future__ import annotations

from typing import Any

WATCH = ("mean", "median", "std", "min", "max", "skew", "zero_rate", "far_outlier_count")


def _delta(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return round(b - a, 4)
    return None


def compare_artifacts(before: dict, after: dict) -> dict[str, Any]:
    ca, cb = before["columns"], after["columns"]
    added, removed = sorted(set(cb) - set(ca)), sorted(set(ca) - set(cb))
    changed = []
    for c in sorted(set(ca) & set(cb)):
        a, b = ca[c], cb[c]
        ch: dict[str, Any] = {}
        if a["semantic"]["type"] != b["semantic"]["type"]:
            ch["semantic_type"] = [a["semantic"]["type"], b["semantic"]["type"]]
        for k in ("null_rate", "distinct"):
            if a.get(k) != b.get(k):
                ch[k] = {"before": a.get(k), "after": b.get(k), "delta": _delta(a.get(k), b.get(k))}
        na, nb = a.get("stats", {}).get("numeric", {}), b.get("stats", {}).get("numeric", {})
        for k in WATCH:
            if na.get(k) != nb.get(k) and (k in na or k in nb):
                ch[k] = {"before": na.get(k), "after": nb.get(k), "delta": _delta(na.get(k), nb.get(k))}
        if ch:
            changed.append({"column": c, "changes": ch})
    warnings = []
    for c in sorted(set(ca) & set(cb)):
        a, b = ca[c], cb[c]
        filled = (a.get("nulls") or 0) - (b.get("nulls") or 0)
        if filled <= 0 or a.get("count") != b.get("count"):
            continue
        w = {"column": c, "missing_before": a.get("nulls"), "missing_after": b.get("nulls"), "missing_decrease": filled,
             "row_lineage": "unavailable: profiles hold aggregates, so which rows changed cannot be known",
             "statement": f"Suspected filling: '{c}' had {a.get('nulls')} missing values before and {b.get('nulls')} after, with the same row count. "
                          "Profiles hold aggregates, so which rows changed, and whether they were imputed, cannot be established here. "
                          "If they were filled, the new profile alone would read them as recorded data."}
        za = (a.get("stats", {}).get("numeric") or {}).get("zero_rate") or 0
        zb = (b.get("stats", {}).get("numeric") or {}).get("zero_rate") or 0
        zeros_a = za * (a["count"] - (a.get("nulls") or 0))   # zero_rate is over non-null values
        zeros_b = zb * (b["count"] - (b.get("nulls") or 0))
        if abs((zeros_b - zeros_a) - filled) <= max(1, 0.05 * filled):
            w["likely_fill"] = 0
            w["statement"] += f" The number of zeros rose by about {filled}, consistent with filling with 0."
        else:
            ta = {x["value"]: x["count"] for x in (a.get("stats", {}).get("categorical") or {}).get("top", [])}
            for x in (b.get("stats", {}).get("categorical") or {}).get("top", []):
                if abs(x["count"] - ta.get(x["value"], 0) - filled) <= max(1, 0.05 * filled):
                    w["likely_fill"] = x["value"]
                    w["statement"] += f" The count of {x['value']!r} rose by about {filled}, consistent with filling with it."
                    break
        w["statement"] += " If filling was intended, keep a missing-indicator or the original column so later analysis can tell filled values from observed ones."
        warnings.append(w)
    fa = {f["id"]: f for f in before["findings"]}
    fb = {f["id"]: f for f in after["findings"]}
    resolved = [fa[i] for i in sorted(set(fa) - set(fb))]
    new = [fb[i] for i in sorted(set(fb) - set(fa))]
    return {
        "schema": "data-guide/compare@0.1",
        "before": {"source": before["dataset"]["source"], "fingerprint": before["dataset"]["fingerprint"]},
        "after": {"source": after["dataset"]["source"], "fingerprint": after["dataset"]["fingerprint"]},
        "same_data": before["dataset"]["fingerprint"] == after["dataset"]["fingerprint"],
        "rows": {"before": before["dataset"]["rows"], "after": after["dataset"]["rows"],
                 "delta": after["dataset"]["rows"] - before["dataset"]["rows"]},
        "columns_added": added, "columns_removed": removed, "columns_changed": changed,
        "missingness_warnings": warnings,
        "findings_resolved": [{k: f.get(k) for k in ("id", "kind", "generator", "relevance", "statement")} for f in resolved],
        "findings_new": [{k: f.get(k) for k in ("id", "kind", "generator", "relevance", "statement")} for f in new],
        "note": "A resolved finding no longer fires on the new data. That is not proof the change was correct.",
    }
