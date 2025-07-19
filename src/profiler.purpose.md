# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: profiler
- @ai-source-files: [profiler.py]
- @ai-role: profiler
- @ai-intent: "Generate plots and advanced profiling for datasets"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: medium
- @ai-risk-drift: "Large file with experimental features"
- @ai-used-by: data_profiler,pipeline
- @ai-downstream: plots,markdown_reports

# Module: profiler
> Houses plotting utilities and specialized profilers for strings, numbers and temporal data.

---

### 🎯 Intent & Responsibility
- Produce column charts, histograms, KDE plots, box plots and missing value matrices
- Analyze temporal columns for gaps and trends
- Profile strings (entropy, dominance, suspicious patterns)
- Profile numeric columns with outlier detection
- Provide DataProfiler class combining these analyses with visualization output

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | dataframe | `pd.DataFrame` | dataset to visualize and profile |
| 📥 In | custom_types | `dict[str,str]` | optional mapping of column roles |
| 📤 Out | results | `Dict[str,Any]` | metadata and per-column profiles |
| 📤 Out | plots | `List[str]` | file paths of generated PNG images |

---

### 🔗 Dependencies
- pandas, numpy, seaborn, matplotlib, missingno, scipy
- regex, os, re

---

### 🗣 Dialogic Notes
- Many plotting functions currently save directly to disk; could be decoupled
- Temporal analysis uses heuristics for smoothing and may need tuning

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Called by `DataProfiler` to generate visual assets
- `DataProfiler` stores paths to plots in results structure

#### Integration Points
- Upstream: DataFrames loaded from ETL steps
- Downstream: markdown reports referencing generated plots

#### Risks
- Plot generation may be slow for wide datasets
- Hard-coded file names may collide when running multiple times

---

### 🧠 Tags
@ai-role: profiler
@ai-intent: visualization helper
@ai-cadence: drift-preferred
@ai-risk-recall: medium
@ai-semantic-scope: plots
@ai-coordination: analysis pipeline
