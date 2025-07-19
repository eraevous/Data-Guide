# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: pipeline
- @ai-source-files: [pipeline.py]
- @ai-role: orchestrator
- @ai-intent: "CLI orchestration using config-driven dataset definitions and bivariate profiling"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: low
- @ai-risk-drift: "Depends on external config for paths; must match environment"
- @ai-used-by: developer
- @ai-downstream: data_profiler

# Module: pipeline
> Orchestrates DataProfiler over predefined datasets and writes reports.

---

### 🎯 Intent & Responsibility
- Load dataset paths and type hints from `data_pipeline.config`
- Invoke `DataProfiler` for univariate analysis
- Run `BivariateProfiler` for correlation heatmaps
- Write resulting reports and plots to an output directory

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | input_dir | `str` | folder containing CSV files |
| 📥 In | output_dir | `str` | folder for report output |
| 📤 Out | reports | `List[str]` | file paths to generated reports |
| 📤 Out | bivariate_plots | `List[str]` | correlation heatmaps |

---

### 🔗 Dependencies
- pandas
- os, sys
- `data_pipeline.config` for dataset mappings
- `DataProfiler` from `data_profiler`
- `BivariateProfiler` for pairwise analysis

---

### 🗣 Dialogic Notes
- Uses configuration module to avoid hard-coded paths
- Bivariate step currently limited to correlation heatmaps

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Acts as entry script when executed directly
- Resolves dataset paths via config
- Runs DataProfiler then BivariateProfiler sequentially

#### Integration Points
- Upstream: CSV data prepared by ETL scripts
- Downstream: DataProfiler reports and bivariate plots

#### Risks
- Execution may be slow for large numbers of files
- Correlation matrices may consume memory on wide datasets

---

### 🧠 Tags
@ai-role: orchestrator
@ai-intent: dataset profiling pipeline
@ai-cadence: run-preferred
@ai-risk-recall: medium
@ai-semantic-scope: CLI
@ai-coordination: sequential execution
