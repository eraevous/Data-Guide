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
- @ai-intent: "CLI orchestration to profile multiple CSVs"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: low
- @ai-risk-drift: "Hard-coded file paths; may break when directory layout changes"
- @ai-used-by: developer
- @ai-downstream: data_profiler

# Module: pipeline
> Orchestrates DataProfiler over predefined datasets and writes reports.

---

### 🎯 Intent & Responsibility
- Load CSV files from a user-specified directory
- Apply custom type hints per dataset
- Invoke `DataProfiler` to profile and generate markdown
- Write resulting reports to an output directory

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | input_dir | `str` | folder containing CSV files |
| 📥 In | output_dir | `str` | folder for report output |
| 📤 Out | reports | `List[str]` | file paths to generated reports |

---

### 🔗 Dependencies
- pandas
- os, sys
- `DataProfiler` from `data_profiler`

---

### 🗣 Dialogic Notes
- Contains many commented blocks and may require cleanup
- Should decouple dataset definitions from code

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Acts as entry script when executed directly
- Loops over dataset map and calls DataProfiler sequentially

#### Integration Points
- Upstream: CSV data prepared by ETL scripts
- Downstream: generated markdown or HTML reports

#### Risks
- Execution may be slow for large numbers of files

---

### 🧠 Tags
@ai-role: orchestrator
@ai-intent: dataset profiling pipeline
@ai-cadence: run-preferred
@ai-risk-recall: medium
@ai-semantic-scope: CLI
@ai-coordination: sequential execution
