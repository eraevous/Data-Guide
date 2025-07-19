# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_profiler
- @ai-source-files: [data_profiler.py]
- @ai-role: profiler
- @ai-intent: "Generate dataset and column level profiling information"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: medium
- @ai-risk-drift: "Interface may change as profiling logic evolves"
- @ai-used-by: pipeline,pipeline_transformed,main_pipeline,run_profiler
- @ai-downstream: reports,plots

# Module: data_profiler
> Provides a DataProfiler class to summarize datasets and produce Markdown reports.

---

### 🎯 Intent & Responsibility
- Profile overall dataset metadata
- Analyze each column (string or numeric) for statistics and anomalies
- Generate Markdown/HTML/CSV reports summarizing results
- Store results in a `results` dictionary for programmatic use

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | dataframe | `pd.DataFrame` | dataset to profile |
| 📥 In | custom_types | `dict[str,str]` | optional column type hints |
| 📤 Out | results | `Dict[str,Any]` | nested summary of dataset and columns |
| 📤 Out | report | `str` | Markdown/HTML/CSV text when generated |

---

### 🔗 Dependencies
- pandas, numpy, seaborn, matplotlib
- missingno
- modules within repo: `profiler` for plotting utilities

---

### 🗣 Dialogic Notes
- Current implementation mixes global helper functions and class methods.
- Assumes small to medium data size; may require sampling for large datasets.

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Called by pipeline scripts to profile raw and transformed CSVs
- Exposes `generate_report` for downstream consumption

#### Integration Points
- Upstream: `pipeline.py`, `main_pipeline.py`, `data_pipeline/pipeline.py`
- Downstream: markdown reports and visual plots stored to disk

#### Risks
- Profiling large datasets may exhaust memory
- Temporary files (plots) may accumulate

---

### 🧠 Tags
@ai-role: profiler
@ai-intent: data quality summary
@ai-cadence: drift-preferred
@ai-risk-recall: medium
@ai-semantic-scope: reports
@ai-coordination: analysis pipeline
