"""Human annotations (``guide.yml``): the only place domain meaning enters (requirement B).

Example::

    dataset:
      row_unit: one row per hospital encounter
      question: Which discharges are at risk of 30-day readmission?
      decision: Who gets a follow-up call
      target: readmitted_30d
      generating_process: Exported from the EHR; transfers excluded
    columns:
      dx_group:
        meaning: Primary diagnosis group
        semantic_type: categorical
        note: '"Surgery" is a service, not a diagnosis'
    interpretations:
      - kind: hypothesis
        statement: Diagnosis groups follow different readmission processes
        columns: [dx_group, readmitted_30d]

Everything read from this file is labelled ``generator: human`` in the artifact.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from understanding.semantics import SEMANTIC_TYPES

DATASET_KEYS = ("row_unit", "question", "decision", "target", "generating_process", "description")


class AnnotationError(ValueError):
    pass


def empty() -> dict[str, Any]:
    return {"dataset": {}, "columns": {}, "interpretations": [], "sha256": None, "path": None}


def load(path: str | Path | None, columns: list[str]) -> dict[str, Any]:
    if path is None:
        return empty()
    p = Path(path)
    raw = p.read_bytes()
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise AnnotationError("annotations must be a mapping")
    ds = data.get("dataset") or {}
    unknown = set(ds) - set(DATASET_KEYS)
    if unknown:
        raise AnnotationError(f"unknown dataset keys: {sorted(unknown)}; allowed: {list(DATASET_KEYS)}")
    target = ds.get("target")
    if target is not None and target not in columns:
        raise AnnotationError(f"target {target!r} is not a column")
    cols = data.get("columns") or {}
    for c, spec in cols.items():
        if c not in columns:
            raise AnnotationError(f"annotated column {c!r} is not in the data")
        st = (spec or {}).get("semantic_type")
        if st is not None and st not in SEMANTIC_TYPES:
            raise AnnotationError(f"{c}: semantic_type {st!r} not one of {list(SEMANTIC_TYPES)}")
    interps = data.get("interpretations") or []
    for i in interps:
        if i.get("kind", "interpretation") not in ("interpretation", "hypothesis", "action", "question"):
            raise AnnotationError("interpretation kind must be interpretation, hypothesis, action or question")
        if not i.get("statement"):
            raise AnnotationError("each interpretation needs a statement")
    return {"dataset": ds, "columns": cols, "interpretations": interps,
            "sha256": hashlib.sha256(raw).hexdigest(), "path": p.name}
