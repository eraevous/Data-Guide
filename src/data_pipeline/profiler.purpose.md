# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.profiler
- @ai-source-files: [profiler.py]
- @ai-role: profiler
- @ai-intent: "Legacy copy of profiling utilities used before refactor"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: medium
- @ai-risk-drift: "Redundant with top-level profiler"
- @ai-used-by: pipeline
- @ai-downstream: plots

# Module: data_pipeline.profiler
> Duplicate of root profiler module kept for backward compatibility during reorganization.

---

### 🎯 Intent & Responsibility
- Provide plotting utilities and DataProfiler class similar to main module
- Generate visualizations and profiling metrics for each column

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | dataframe | `pd.DataFrame` | dataset to profile |
| 📤 Out | report | `str` | markdown report |

---

### 🔗 Dependencies
- pandas, numpy, seaborn, matplotlib, missingno
- os, re

---

### 🗣 Dialogic Notes
- Should be consolidated with `src/profiler.py` once the reorganization stabilizes

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Invoked by `data_pipeline/pipeline.py` to generate analyses

#### Integration Points
- Upstream: CSVs loaded into DataFrames
- Downstream: markdown or html reports

#### Risks
- Maintenance burden due to duplicated logic

---

### 🧠 Tags
@ai-role: profiler
@ai-intent: duplicated profiling module
@ai-cadence: drift-preferred
@ai-risk-recall: medium
@ai-semantic-scope: dataset
@ai-coordination: analysis
