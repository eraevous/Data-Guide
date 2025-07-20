# Notebook Modularization Plan

These notebooks capture early explorations for Juniper Dentistry's Data Guide project. To integrate them into the Python codebase we will:

1. **Identify Reusable Logic**
   - Data cleaning helpers (e.g., timestamp conversion, currency parsing) from `data munging.ipynb`.
   - Aggregation and visualization routines used across AR and retention analyses.
   - Survival analysis preparation steps from `Retention.ipynb`.

2. **Create Stand‑alone Modules**
   - A `notebooks` package mirroring each analytic theme.
   - Convert exploration cells into functions with clear input DataFrames and return values.
   - Reuse `data_profiler` utilities for plotting instead of ad‑hoc matplotlib calls.

3. **Separate Juniper‑Specific Paths**
   - Replace hard coded Windows paths with config entries (`data_pipeline.config`).
   - Parameterize insurance carrier lists and plan names to allow reuse by other clinics.

4. **Testing & Documentation**
   - Unit tests for data munging helpers and AR calculation functions.
   - `.purpose.md` files for each converted module to align with repository guidance.

This migration will let us run analyses programmatically and support future clinics with minimal code changes.
