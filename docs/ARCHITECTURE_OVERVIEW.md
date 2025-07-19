# Architecture Overview

This document captures a high level view of the data profiling pipeline based on the available modules and their `.purpose.md` descriptions.

## Core Components

| Module | Role | Key Purpose |
|-------|------|-------------|
| `data_profiler.py` | profiler | Provide dataset and column level summaries and reports |
| `data_transform.py` | transformer | Utility functions for cleaning and joining DataFrames |
| `profiler.py` | profiler | Advanced plotting and profiling utilities |
| `bivariate_profiler.py` | analysis | Pairwise correlations and advanced EDA |
| `pipeline.py` | orchestrator | Config‑driven CLI pipeline for profiling |
| `data_pipeline/config.py` | config | Central dataset mapping and type hints |
| `main_pipeline.py` | orchestrator | Example end‑to‑end workflow using seaborn sample data |
| `run_profiler.py` | cli | Minimal entry point for profiling a folder of CSVs |
| `data_pipeline/*` | etl / helpers | API client, HTML conversion, and additional pipeline pieces |
| `main_pipeline.py` | orchestrator | Example end‑to‑end workflow using seaborn sample data |
| `run_profiler.py` | cli | Minimal entry point for profiling a folder of CSVs |
| `data_pipeline/*` | etl / helpers | API client, HTML conversion, and additional pipeline pieces |

## Flow of Data

1. **ETL and Data Pull** – Optional scripts under `data_pipeline/` fetch or extract CSVs (e.g., from PDFs or APIs).
2. **Configuration** – `data_pipeline.config` defines dataset file names and column types.
3. **Profiling** – `DataProfiler` generates column summaries and plots while `BivariateProfiler` adds correlation heatmaps.
4. **Transformation** – `DataTransform` offers cleaning helpers and joins for further analysis.
5. **Orchestration** – `pipeline.py` resolves paths via config, runs profiling modules, and writes reports.

## Integration Notes

- Results are primarily written to disk as markdown reports and PNG plots.
- Purpose files specify upstream inputs (raw CSVs, API downloads) and downstream artifacts (reports, plots).
- CLI entry points accept an input directory of CSVs and an output directory for results.
- Templates in `templates/` provide reusable Data Guide scaffolds.

This overview will evolve as modules are refined and coordinated into a cohesive package.
