# AGENTS.md · Operating Protocol

*Behavioral rules for AI coding agents operating in this repository.*

---

## 1 Run/Drift Cadence

**Run** — execute, implement, debug, fix.
**Drift** — reflect, validate, update `.purpose.md`, check metric consistency.

When uncertain, default to **Drift**.

| Trigger | Cadence | Rationale |
|---------|---------|-----------|
| Error trace, broken query, or script failure | Run | Rapid iteration needed |
| Prompt contains "ask", "explore", "why", or is reflective | Drift | User is seeking structural insight |
| `.purpose.md` update or reconciliation requested | Drift | Requires semantic reflection |
| User requests metric formula changes or new segment analysis | Run | Implement and verify |
| User pauses, talks abstractly about design | Drift | Time for alignment and memory capture |
| Output deviates from expected values, user requests comparison | Drift | Check `.purpose.md` contract vs. code |
| User switches between Predictions scripts and top-level tools | Drift | Sync context before shifting |
| New Snowflake table or column introduced | Drift | Validate column contract in `.purpose.md` first |
| User prompts "proceed", "implement", or gives concrete task | Run | User satisfied with planning |
| User asks about threshold values, segment counts, or MC search results | Drift | Distinguish stat parameters from threshold parameters; `outlier_z_threshold` requires full re-run, others do not |

---

## 2 Glossary

| Term | Meaning |
|------|---------|
| `Run` | Execution phase — speed, completeness, implementation |
| `Drift` | Reflection phase — validation, structure, coherence |
| `.purpose.md` | Canonical module design contract (IO, role, risk, dependencies) |
| `Granular` | Predictions broken down by `service_line_id` |
| `Rollup` | Predictions aggregated across service lines (represented by `-1`) |
| `Champion Model` | The model with lowest Hybrid Error Score for a given feature combination |
| `STARS` | Diagnostic framework: Stability, Truthfulness, Abundance, Regularity, Structure — the five assumptions a segment must satisfy to be classified Normal |
| `MESH` | Segment-level error metric; one constant value per `feature_segment`. Never aggregate across rows — always deduplicate to one row per segment first |
| `feature_segment` | Concatenated key `strata_id\|entity_id\|patient_type_rollup\|service_line`; the join key across all performance and monitoring DataFrames |
| `segment_df` | Canonical one-row-per-`feature_segment` DataFrame with MESH and within_10/5/3 flags; the single source of truth for all performance metrics |
| `MonitorConfig` | Dataclass holding all STARS test parameters, split into **stat parameters** (affect raw computation: `outlier_z_threshold`, `recent_days`, `train_days`) and **threshold parameters** (gate pre-computed stats: everything else) |
| `apply_thresholds_to_stats` | Vectorized function that re-applies threshold comparisons to pre-computed stats; enables Monte Carlo search without re-running expensive per-series tests |

---

## 3 `.purpose.md` Enrichment Protocol

When writing or updating a `.purpose.md` file:

- **Outputs**: list precise DataFrame column schemas; annotate downstream consumers
- **Coordination**: describe how the module coordinates with Snowflake, upstream scripts, and the dashboard
- **Integration points**: list modules consuming or producing this module's output; name Snowflake tables explicitly
- **Risks**: distinguish stat parameters from threshold parameters for any module with a config dataclass
- **Anchor in ecosystem**: note whether the module is standalone or part of the Predictions/ workflow

Governing hierarchy: **CHARTER.md > AGENTS.md > module contracts**. If a change would violate the Charter, stop and propose a compliant alternative.
