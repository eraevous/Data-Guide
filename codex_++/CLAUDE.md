# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Governing Framework

This repo uses a cognitive-coupled coding protocol. Read these before making structural changes:

| File | Role |
|------|------|
| `AGENTS.md` | Operational protocol — Run/Drift cadence, memory capture, governance rules |
| `CHARTER.md` | Engineering rules — metrics contract, output paths, connection conventions |
| `codex_++/purpose_files/*.purpose.md` | Per-module design contracts (IO schemas, risks) |
| `purpose_schema.md` | Template for creating new `.purpose.md` files |

**Precedence:** CHARTER > AGENTS > module contracts. If a change would violate the Charter, stop and propose a compliant alternative.

---

## Commands

**Install dependencies** (`uv` is the package manager):
```bash
uv sync
```

**Run the Streamlit dashboard:**
```bash
streamlit run Predictions/streamlit_app.py
```

**Run CLI tools:**
```bash
# AST dependency graph extractor
python ast_dependency_cli.py analyze --source-dir . --recursive

# Combine Python scripts into a monolith
python combine_scripts.py /path/to/root

# Interactive transition diagram from a CSV
python transitions.py --csv_file data.csv --from_state <col> --to_state <col>
```

**Lint** (Ruff is present but not enforced via config):
```bash
ruff check .
```

There are no automated tests.

---

## Architecture

### Data source

Scripts may read from external data sources (e.g., a data warehouse) via credentials from environment variables — never hardcoded.

**Exception**: `performance_investigation.py` reads from a local CSV and an EDA features CSV. It no longer queries the data warehouse at runtime.

### Domain concepts

- **Granular** — predictions broken down by a category identifier
- **Rollup** — predictions aggregated across categories
- **Champion model** — model with lowest Hybrid Error Score for a given combination of strata, granularity, and features
- **Canonical metrics** — AE, APE, Hybrid Error Score. Formulas are defined once in `granularity_performance.py` and must be replicated identically in segment scripts.
- **MESH** — the segment-level error metric. One value per `feature_segment` (constant across all rows for that segment). Never average it across rows; deduplicate to one row per segment before any threshold comparison.
- **feature_segment** — concatenated key identifying one prediction series. The join key across all performance and monitoring DataFrames.

### `Predictions/` — analytics scripts

Standalone scripts, not imported by each other. Each reads from the data source and writes to `Predictions/outputs/` or `Predictions/acf_outputs/`.

| Script | Role |
|--------|------|
| `granularity_performance.py` | Core error metrics across daily/monthly granularities; champion model selection; threshold accuracy (3%/5%/10%) |
| `performance_investigation.py` | STARS framework diagnostics: segment classification (Normal/Atypical), ACF structure divergence, Monte Carlo threshold search, SHAP, binary correlogram |
| `patient_type_performance.py` | Per-patient-type accuracy breakdown — **structural twin** of `service_line_performance.py` |
| `service_line_performance.py` | Per-service-line accuracy breakdown — **structural twin** of `patient_type_performance.py` |
| `streamlit_app.py` | Interactive dashboard: filters, actuals-vs-predicted plots, CV metrics, ZIP export |

`patient_type_performance.py` and `service_line_performance.py` must remain structurally symmetric (CHARTER Rule #9).

### Top-level utility scripts

| Script | Role |
|--------|------|
| `ast_dependency_cli.py` | AST-based function call graph extractor; outputs CSV edge list or adjacency matrix; configurable via `.graphconfig.json` |
| `combine_scripts.py` | Concatenates `.py` files across subdirectories into a monolith with docstring headers |
| `transitions.py` | Circular state-transition diagrams with Bezier edges via Plotly; `create_transition_diagram()` is importable |

---

### Key pattern: compute/classify decoupling in `performance_investigation.py`

`run_monitoring()` runs all per-series statistical tests (expensive). `apply_thresholds_to_stats()` re-applies threshold comparisons to the resulting stats DataFrame (vectorized, no loops). Monte Carlo search calls the latter N times — the expensive step runs exactly once.

**MESH is constant per segment** — `segment_df` (one row per `feature_segment`, deduped) is the single source of truth for threshold flags. All aggregate and Normal/Abnormal performance splits derive from it to guarantee `aggregate = Normal + Abnormal`.

---

## Run/Drift Cadence

When working in this repo, adapt cognitive mode based on task type:

- **Run** — implementation, debugging, metric changes, data source query fixes
- **Drift** — updating `.purpose.md`, reviewing metric formula consistency, architecture review, schema changes

When touching a module, check its `.purpose.md` in `codex_++/purpose_files/` first. If the IO or metric contract has changed, update the `.purpose.md` as part of the work.
