# Architecture Overview

This document captures a high level view of the data profiling pipeline based on the available modules and their `.purpose.md` descriptions.

## Core Components

| Module | Role | Key Purpose |
|-------|------|-------------|
| `data_profiler.py` | profiler | Provide dataset and column level summaries and reports |
| `data_transform.py` | transformer | Utility functions for cleaning and joining DataFrames |
| `profiler.py` | profiler | Advanced plotting and profiling utilities |
| `pipeline.py` / `data_pipeline/pipeline.py` | orchestrator | CLI pipelines for running the profiler over many CSVs |
| `main_pipeline.py` | orchestrator | Example end‑to‑end workflow using seaborn sample data |
| `run_profiler.py` | cli | Minimal entry point for profiling a folder of CSVs |
| `data_pipeline/*` | etl / helpers | API client, HTML conversion, and additional pipeline pieces |

## Flow of Data

1. **ETL and Data Pull** – Optional scripts under `data_pipeline/` fetch or extract CSVs (e.g., from PDFs or APIs).
2. **Profiling** – The `DataProfiler` class (either `data_profiler.py` or the extended `profiler.py`) profiles DataFrames, generates visual plots, and writes markdown summaries.
3. **Transformation** – `DataTransform` offers cleaning helpers and joins for further analysis.
4. **Orchestration** – Pipeline scripts (`pipeline.py`, `main_pipeline.py`, etc.) load CSVs, invoke the profiler, optionally run transformations, and output reports.

## Integration Notes

- Results are primarily written to disk as markdown reports and PNG plots.
- Purpose files specify upstream inputs (raw CSVs, API downloads) and downstream artifacts (reports, plots).
- CLI entry points accept an input directory of CSVs and an output directory for results.

This overview will evolve as modules are refined and coordinated into a cohesive package.
