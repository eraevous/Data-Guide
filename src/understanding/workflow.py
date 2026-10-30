"""Workflows behind the CLI (thin CLI, fat workflow)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from understanding import annotations as ann
from understanding.artifact import build_artifact, dumps
from understanding.compare import compare_artifacts


def to_profiling_result(gdf, artifact: dict):
    """Attach the artifact to the approved ProfilingResult contract (April 2026 design)."""
    from core.models import ProfilingResult
    return ProfilingResult(source=gdf, dataset_stats=artifact["dataset"], column_stats=artifact["columns"],
                           bivariate_stats=artifact["relations"], understanding=artifact)


def understand(df: pd.DataFrame, *, source: str, out_dir: Path, annotations_path: Path | None = None,
               top_k: int = 10, formats: tuple[str, ...] = ("json", "md", "html")) -> dict[str, Path]:
    from outputs.understanding_report import to_html, to_markdown

    annots = ann.load(annotations_path, [str(c) for c in df.columns]) if annotations_path else ann.empty()
    art = build_artifact(df, source=source, annotations=annots, top_k=top_k)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    if "json" in formats:
        paths["json"] = out_dir / "guide-profile.json"
        paths["json"].write_text(dumps(art), encoding="utf-8")
    if "md" in formats:
        paths["md"] = out_dir / "guide-report.md"
        paths["md"].write_text(to_markdown(art), encoding="utf-8")
    if "html" in formats:
        paths["html"] = out_dir / "guide-report.html"
        paths["html"].write_text(to_html(art), encoding="utf-8")
    return paths


def compare(before: Path, after: Path) -> dict:
    a = json.loads(before.read_text(encoding="utf-8"))
    b = json.loads(after.read_text(encoding="utf-8"))
    return compare_artifacts(a, b)


def render_compare(d: dict) -> str:
    L = [f"# Data Guide compare: {d['before']['source']} → {d['after']['source']}", "",
         f"Rows {d['rows']['before']:,} → {d['rows']['after']:,} ({d['rows']['delta']:+,}) · same data: {d['same_data']}", ""]
    if d["columns_added"] or d["columns_removed"]:
        L += [f"- Added: {', '.join(d['columns_added']) or 'none'}", f"- Removed: {', '.join(d['columns_removed']) or 'none'}", ""]
    if d["columns_changed"]:
        L += ["## Column changes", ""]
        for c in d["columns_changed"]:
            parts = []
            for k, v in c["changes"].items():
                parts.append(f"{k}: {v[0]} → {v[1]}" if isinstance(v, list) else f"{k}: {v['before']} → {v['after']}")
            L.append(f"- `{c['column']}`: " + "; ".join(parts))
        L.append("")
    if d.get("missingness_warnings"):
        L += ["## Missing values that were filled", ""] + [f"- {w['statement']}" for w in d["missingness_warnings"]] + [""]
    for key, title in (("findings_resolved", "No longer found"), ("findings_new", "New findings")):
        if d[key]:
            L += [f"## {title}", ""] + [f"- [{f['kind']} · {f.get('generator') or 'rule'}] {f['statement']}" for f in d[key]] + [""]
    L.append(d["note"])
    return "\n".join(L) + "\n"
