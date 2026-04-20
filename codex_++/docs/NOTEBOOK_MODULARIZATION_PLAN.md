# Notebook Modularization Plan

These notebooks capture early explorations for a client dataset project. To integrate them into the Python codebase we will:

1. **Identify Reusable Logic**
   - Data cleaning helpers (e.g., timestamp conversion, currency parsing) from `data munging.ipynb`.
   - Aggregation and visualization routines used across AR and retention analyses.
   - Survival analysis preparation steps from `Retention.ipynb`.

2. **Create Stand‑alone Modules**
   - A `notebooks` package mirroring each analytic theme.
   - Convert exploration cells into functions with clear input DataFrames and return values.
   - Reuse `data_profiler` utilities for plotting instead of ad‑hoc matplotlib calls.

3. **Separate Dataset‑Specific Paths**
   - Replace hard coded paths with config entries.
   - Parameterize category lists and plan names to allow reuse across different datasets.

4. **Testing & Documentation**
   - Unit tests for data munging helpers and AR calculation functions.
   - `.purpose.md` files for each converted module to align with repository guidance.

This migration will let us run analyses programmatically and support future datasets with minimal code changes.
