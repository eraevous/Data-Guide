# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.pipeline
- @ai-source-files: [pipeline.py]
- @ai-role: orchestrator
- @ai-intent: "Run profiling on raw CSV reports"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: low
- @ai-risk-drift: "Hard-coded dataset paths"
- @ai-used-by: developer
- @ai-downstream: profiling_reports

# Module: data_pipeline.pipeline
> Entry script used to iterate over various raw data exports and generate profiles via DataProfiler.

---

### 🎯 Intent & Responsibility
- Map dataset names to CSV paths and custom type hints
- Load each dataset and instantiate DataProfiler
- Generate markdown reports for each dataset

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | input_dir | `str` | base folder containing csv files |
| 📤 Out | report_files | `List[str]` | generated markdown reports |

---

### 🔗 Dependencies
- pandas
- DataProfiler
- DataTransform (commented out)
- os, sys

---

### 🗣 Dialogic Notes
- Many dataset definitions are commented; script requires cleanup

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Designed for manual CLI execution
- Profiles each dataset sequentially

#### Integration Points
- Upstream: csv files from API downloads
- Downstream: analysis and visualization modules

#### Risks
- Fails if expected CSVs are missing

---

### 🧠 Tags
@ai-role: orchestrator
@ai-intent: raw data pipeline
@ai-cadence: run-preferred
@ai-risk-recall: medium
@ai-semantic-scope: CLI
@ai-coordination: sequential
