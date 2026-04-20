from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd


@dataclass
class SchemaContract:
    key_cols: list[str] = field(default_factory=list)
    context_cols: list[str] = field(default_factory=list)
    metric_col: str = "metric"
    value_col: str = "value"
    type_col: str | None = None
    mode: Literal["long", "wide", "unknown"] = "unknown"


@dataclass
class GuideDataFrame:
    df: pd.DataFrame
    schema: SchemaContract
    source_type: str
    origin: str


@dataclass
class Narrative:
    element_id: str
    text: str
    framework: str


@dataclass
class ProfilingResult:
    source: GuideDataFrame
    dataset_stats: dict[str, Any]
    column_stats: dict[str, Any]
    bivariate_stats: dict[str, Any] = field(default_factory=dict)
    annotations: dict[str, Narrative] | None = None
