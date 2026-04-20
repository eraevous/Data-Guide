from __future__ import annotations

import html as _html
from pathlib import Path
from typing import Any

from core.models import ProfilingResult
from outputs.html_utils import wrap_html


class StaticReportRenderer:
    def render(self, result: ProfilingResult, output_path: str) -> None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        sections: list[str] = []
        sections.append(self._header(result))
        sections.append(self._dataset_overview(result))
        sections.append(self._column_stats(result))

        html = wrap_html("\n".join(sections), title="Data Guide Report")
        out.write_text(html, encoding="utf-8")

    def _header(self, result: ProfilingResult) -> str:
        origin = _html.escape(str(result.source.origin))
        source_type = _html.escape(str(result.source.source_type))
        mode = _html.escape(str(result.source.schema.mode))
        return (
            f"<h1>Data Guide Report</h1>"
            f"<p><strong>Source:</strong> {origin} "
            f"(<code>{source_type}</code>, mode: <code>{mode}</code>)</p>"
        )

    def _dataset_overview(self, result: ProfilingResult) -> str:
        stats = result.dataset_stats
        if not stats:
            df = result.source.df
            stats = {
                "row_count": len(df),
                "col_count": len(df.columns),
                "missing_pct": round(df.isnull().mean().mean() * 100, 2),
            }
        rows = "".join(
            f"<tr><td>{_html.escape(str(k))}</td><td>{_html.escape(str(v))}</td></tr>"
            for k, v in stats.items()
        )
        return (
            "<div class='section'>"
            "<h2>Dataset Overview</h2>"
            f"<table><tr><th>Metric</th><th>Value</th></tr>{rows}</table>"
            "</div>"
        )

    def _column_stats(self, result: ProfilingResult) -> str:
        stats = result.column_stats
        if not stats:
            stats = {
                col: {
                    "dtype": str(result.source.df[col].dtype),
                    "null_count": int(result.source.df[col].isnull().sum()),
                    "unique": int(result.source.df[col].nunique()),
                }
                for col in result.source.df.columns
            }
        sections = ["<div class='section'><h2>Column Profiles</h2>"]
        for col, col_stats in stats.items():
            if isinstance(col_stats, dict):
                rows = "".join(
                    f"<tr><td>{_html.escape(str(k))}</td><td>{_html.escape(str(v))}</td></tr>"
                    for k, v in col_stats.items()
                )
                sections.append(
                    f"<h3>{_html.escape(str(col))}</h3>"
                    f"<table><tr><th>Stat</th><th>Value</th></tr>{rows}</table>"
                )
        sections.append("</div>")
        return "\n".join(sections)
