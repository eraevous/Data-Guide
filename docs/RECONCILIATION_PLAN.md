# Refactoring & Reconciliation Plan

This document outlines how to consolidate overlapping modules and remove dead code.

## Issues Identified
- Duplicate profilers (`profiler.py`, `profiler_update.py`, `data_profiler.py`).
- Two versions of `DataTransform` in `src/` and `src/data_pipeline/`.
- Example scripts (`run_profiler.py`, `test_profiler.py`, `main_pipeline.py`) contain hard-coded file paths and terminal artifacts.
- Limited CLI functionality and inconsistent configuration handling.

## Proposed Steps
1. **Profiler consolidation**
   - Keep `data_profiler.py` as the canonical implementation.
   - Merge useful features from `profiler.py` and `profiler_update.py` then delete those modules.
   - Update import paths throughout the pipeline.
2. **Transformation utilities**
   - Merge `data_transform.py` and `data_pipeline/data_transform.py` into a single module.
3. **Script cleanup**
   - Replace hard‑coded paths with argparse based CLIs (see updated `run_profiler.py`).
   - Remove terminal prompts from files and add basic error handling.
4. **Package structure**
   - Expose pipeline entry points via `python -m data_pipeline` or console scripts.
   - Document these commands in `docs/USAGE_GUIDE.md`.

Following this plan will reduce redundancy and make the codebase easier to maintain.
