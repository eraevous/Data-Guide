from __future__ import annotations

from data_profiler import DataProfiler
from core.models import GuideDataFrame, ProfilingResult


def profile(
    gdf: GuideDataFrame,
    analyses: list[str] | None = None,
    output_dir: str = ".",
) -> ProfilingResult:
    """Run univariate profiling on a GuideDataFrame, return a ProfilingResult."""
    if analyses is None:
        analyses = ["dataset", "columns"]

    custom_types: dict[str, str] = {}
    if (
        gdf.schema.mode == "long"
        and gdf.schema.type_col
        and gdf.schema.type_col in gdf.df.columns
        and gdf.schema.metric_col in gdf.df.columns
    ):
        for _, row in gdf.df[[gdf.schema.metric_col, gdf.schema.type_col]].dropna().iterrows():
            custom_types[str(row[gdf.schema.metric_col])] = str(row[gdf.schema.type_col])

    profiler = DataProfiler(gdf.df, custom_types=custom_types, output_dir=output_dir)

    if "dataset" in analyses:
        # profile_dataset() internally calls profile_columns(), so skip the explicit call
        profiler.profile_dataset()
    elif "columns" in analyses:
        profiler.profile_columns()

    dataset_stats = {
        k: profiler.results[k]
        for k in ("metadata", "column_types")
        if k in profiler.results
    }
    column_stats = {
        k: profiler.results[k]
        for k in ("numeric_profiles", "string_profiles", "temporal_analyses", "phone_profiles")
        if k in profiler.results
    }

    return ProfilingResult(
        source=gdf,
        dataset_stats=dataset_stats,
        column_stats=column_stats,
    )
