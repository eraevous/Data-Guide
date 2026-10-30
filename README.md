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

## Understanding layer (prototype)

```bash
guide demo --out guide-demo                       # synthetic table with planted problems
guide understand data.csv --annotations guide.yml --out out/
guide compare before/guide-profile.json after/guide-profile.json
```

`guide understand` writes `guide-profile.json` (a versioned, deterministic artifact) and Markdown/HTML views derived from it. Findings are typed (observation, interpretation, hypothesis, action, question) and say who produced them: deterministic rules or the human annotations file. There is no AI-generated text. A register lists what the data cannot tell you (row unit, how rows were produced, why values are missing) as open questions. See [docs/prototype/README.md](docs/prototype/README.md) for what is built, the acceptance loop, and the known limits.

## Documentation
- [Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md)
- [Usage Guide](docs/USAGE_GUIDE.md)

The [`purpose_files/`](purpose_files) directory contains purpose statements for each module.

## License

Licensed under the [MIT License](LICENSE). Contributions are welcome under the
[Contributor License Agreement](CLA.md), which keeps them open under the same license
while letting the maintainer also offer commercial versions. See
[CONTRIBUTING.md](CONTRIBUTING.md).
