# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.data_pull
- @ai-source-files: [data_pull.py]
- @ai-role: etl
- @ai-intent: "Download reports from Dentrix Ascend API and save to CSV"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: high
- @ai-risk-performance: medium
- @ai-risk-drift: "Endpoints and parameters may change"
- @ai-used-by: pipeline
- @ai-downstream: csv_files

# Module: data_pull
> Contains helper functions for fetching various reports and saving them locally.

---

### 🎯 Intent & Responsibility
- Use `APIClient` to authenticate and fetch aged AR, statement submission, integrated payments and other reports
- Normalize JSON responses into DataFrames
- Write CSV files for later profiling and analysis

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | client | `APIClient` | authenticated session object |
| 📥 In | output_dir | `str` | path to output folder |
| 📤 Out | csv_paths | `List[str]` | saved CSV file names |

---

### 🔗 Dependencies
- pandas
- os
- `APIClient` from same package

---

### 🗣 Dialogic Notes
- Many parameters (dates, location IDs) are hard-coded
- Should add error handling for API failures

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Called by orchestrator scripts to refresh datasets before profiling

#### Integration Points
- Upstream: credentials provided to `APIClient`
- Downstream: Pipeline reading the saved CSVs

#### Risks
- Rate limits or authentication errors may interrupt ETL

---

### 🧠 Tags
@ai-role: etl
@ai-intent: report download
@ai-cadence: run-preferred
@ai-risk-recall: medium
@ai-semantic-scope: csv
@ai-coordination: scheduled
