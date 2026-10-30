"""Build the versioned understanding artifact: the stable interface (requirement E).

The artifact is deterministic: the same data, annotations and options give byte-identical JSON.
Reports are derived from it and never add claims of their own.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import pandas as pd

from understanding import annotations as ann
from understanding import columns as colmod
from understanding import relations as relmod
from understanding import rules
from understanding.findings import CONFIDENCE_MEANING, KIND_MEANING, KINDS, Finding, sort_findings
from understanding.semantics import apply_override, infer

SCHEMA = "data-guide/understanding@0.1"
TOOL_VERSION = "0.1.0"


def fingerprint(df: pd.DataFrame) -> str:
    h = hashlib.sha256()
    h.update(json.dumps([str(c) for c in df.columns]).encode())
    h.update(json.dumps([str(t) for t in df.dtypes]).encode())
    h.update(pd.util.hash_pandas_object(df.astype(str), index=False).to_numpy().tobytes())
    return h.hexdigest()


def _human_findings(annots: dict) -> list[Finding]:
    out = []
    for i in annots.get("interpretations", []):
        out.append(Finding(i.get("kind", "interpretation"), "annotation", i["statement"],
                           subjects=list(i.get("columns", [])), generator="human",
                           confidence=i.get("confidence", "medium")))
    return out


def _usefulness(declared: dict, findings: list[Finding], rel: dict) -> dict[str, Any]:
    q, d, t = declared.get("question"), declared.get("decision"), declared.get("target")
    if not (q or d or t):
        return {"status": "unassessed",
                "reason": "Decision-specific usefulness is unassessed: no question, decision or target was declared. "
                          "Exploratory findings are still reported; whether they matter for a decision is open. "
                          "Declare the decision under 'dataset' in the annotations file to rank findings against it.",
                "question": None, "decision": None, "target": None}
    tf = [f.id for f in findings if f.relevance == "target"]
    return {"status": "declared", "question": q, "decision": d, "target": t,
            "target_findings": tf,
            "note": "Findings marked 'target' bear on the declared target. Whether they change the decision is for the analyst to judge."}


def build_artifact(df: pd.DataFrame, *, source: str, annotations: dict | None = None, top_k: int = 10,
                   budget: int = 300) -> dict[str, Any]:
    annots = annotations or ann.empty()
    declared = dict(annots.get("dataset", {}))
    target = declared.get("target")
    n_rows = len(df)
    semantics, profiles = {}, {}
    findings: list[Finding] = []
    col_annots = annots.get("columns", {})
    for c in df.columns:
        a = col_annots.get(c) or {}
        inferred = infer(str(c), df[c], n_rows)
        sem = apply_override(inferred, a.get("semantic_type"))
        if a.get("semantic_type") and a["semantic_type"] != inferred["type"] and inferred["type"] not in a.get("accept_types", []):
            findings.append(Finding("question", "annotation-disagrees",
                                    f"The annotations call '{c}' {a['semantic_type'].replace('_', ' ')}, but its values look "
                                    f"{inferred['type'].replace('_', ' ')} ({'; '.join(inferred['reasons'])}). Which is right?",
                                    subjects=[str(c)], evidence={"declared": a["semantic_type"], "inferred": inferred["type"]}))
        semantics[c] = sem
        profiles[c] = colmod.profile_column(df[c], sem)
        findings += rules.column_rules(str(c), df[c], sem, profiles[c], a)

    ds_findings, register = rules.dataset_rules(df, semantics, declared)
    findings += ds_findings
    periods = rules.period_columns(df, semantics)
    shape_findings, shape = rules.shape_rules(df, periods)
    register["shape"] = shape
    rel = relmod.screen(df, semantics, target=target, top_k=top_k, budget=budget, exclude=set(periods))
    findings += rules.relation_rules(rel, target)
    if periods:
        pset = set(map(str, periods))
        kept = [f for f in findings if not (f.rule in rules.COLLAPSIBLE and f.subjects and set(f.subjects) <= pset)]
        shape_findings[0].evidence["per_column_findings_summarised"] = len(findings) - len(kept)
        findings = kept
    findings += shape_findings
    findings += _human_findings(annots)

    # Meaning register: which columns have human-stated meaning.
    unstated = [c for c in df.columns if not (col_annots.get(c) or {}).get("meaning")]
    if unstated:
        findings.append(Finding("question", "meaning-unstated",
                                f"{len(unstated)} of {len(df.columns)} columns have no stated meaning; their names and inferred types are guesses.",
                                subjects=unstated if len(unstated) <= 20 else [], evidence={"count": len(unstated)}, confidence="high"))
    findings = sort_findings(findings)
    # De-duplicate by id (two rules can produce the same question).
    seen, unique = set(), []
    for f in findings:
        if f.id not in seen:
            seen.add(f.id)
            unique.append(f)
    findings = unique

    cols_out = {}
    for c in df.columns:
        a = col_annots.get(c) or {}
        cols_out[str(c)] = {
            "meaning": a.get("meaning"), "meaning_source": "human" if a.get("meaning") else "unknown",
            "semantic": semantics[c], **profiles[c],
            "findings": [f.id for f in findings if str(c) in f.subjects],
        }

    counts = {k: sum(1 for f in findings if f.kind == k) for k in KINDS}
    gens = {g: sum(1 for f in findings if f.generator == g) for g in ("rule", "human")}
    artifact = {
        "schema": SCHEMA,
        "dataset": {"source": source, "rows": n_rows, "columns": len(df.columns), "fingerprint": fingerprint(df),
                    "memory_bytes": int(df.memory_usage(deep=True).sum())},
        "declared": {k: declared.get(k) for k in ann.DATASET_KEYS if declared.get(k)},
        "register": {
            **register,
            "missingness_mechanism": "unknown: missing-value patterns are reported; why values are missing is not inferred",
            "generating_process": {"value": declared.get("generating_process"),
                                   "source": "human" if declared.get("generating_process") else "unknown"},
            "open_questions": [f.id for f in findings if f.kind == "question"],
        },
        "usefulness": _usefulness(declared, findings, rel),
        "summary": {"findings_by_kind": counts, "findings_by_generator": gens},
        "kind_meaning": KIND_MEANING,
        "confidence_meaning": CONFIDENCE_MEANING,
        "findings": [f.to_dict() for f in findings],
        "columns": cols_out,
        "relations": rel,
        "provenance": {"tool": "data-guide understand", "tool_version": TOOL_VERSION, "schema": SCHEMA,
                       "annotations": {"file": annots.get("path"), "sha256": annots.get("sha256")},
                       "options": {"top_k": top_k, "pair_budget": budget}, "deterministic": True,
                       "generators": "rule = deterministic rules in understanding.rules; human = the annotations file. No AI-generated text."},
    }
    return json.loads(json.dumps(artifact, default=str, sort_keys=False))


def dumps(artifact: dict) -> str:
    return json.dumps(artifact, indent=2, ensure_ascii=False) + "\n"
