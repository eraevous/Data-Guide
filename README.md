# Data Guide

Data Guide provides a modular pipeline for generating rich exploratory data analysis (EDA) reports. The project bundles utilities for profiling tabular datasets, performing bivariate analysis and exporting markdown summaries.

## Features
- Dataset and column level profiling via `DataProfiler`
- Bivariate correlation and visualization utilities
- Simple transformation helpers
- Config‑driven pipeline scripts

## Installation
```bash
pip install -e .
```
This installs the package in editable mode and pulls in the required dependencies listed in `pyproject.toml`.

## Usage
Run the CLI pipeline on a folder of CSV files:
```bash
python src/pipeline.py <input_dir> <output_dir>
```
Individual profiling can be executed with the Typer CLI:
```bash
python src/profiler_cli.py profile --config my_config.json --output-dir reports
```
The main pipelines now import `DataProfiler` from `data_profiler` after consolidation.
Example notebooks and templates are provided under `templates/`.

## Documentation
- [Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md)
- [Usage Guide](docs/USAGE_GUIDE.md)

The [`purpose_files/`](purpose_files) directory contains purpose statements for each module.
