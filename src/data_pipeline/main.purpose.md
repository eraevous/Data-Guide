# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.main
- @ai-source-files: [main.py]
- @ai-role: orchestrator
- @ai-intent: "Command line entry for pulling reports via APIClient"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: high
- @ai-risk-performance: medium
- @ai-risk-drift: "Depends on API endpoints"
- @ai-used-by: developer
- @ai-downstream: csv_files

# Module: data_pipeline.main
> Authenticates with Dentrix Ascend and downloads multiple reports to a local directory.

---

### 🎯 Intent & Responsibility
- Parse CLI arguments for username, password and output directory
- Create an `APIClient`, login and load cookies
- Call data_pull functions to fetch several reports

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | username | `str` | credential for login |
| 📥 In | password | `str` | credential for login |
| 📥 In | output_dir | `str` | where CSVs will be saved |
| 📤 Out | csv_files | `List[str]` | generated CSV file paths |

---

### 🔗 Dependencies
- APIClient
- data_pull module
- sys, os

---

### 🗣 Dialogic Notes
- Credentials are passed via command line; consider environment variables

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Intended to be run manually prior to EDA pipeline

#### Integration Points
- Upstream: user credentials
- Downstream: pipeline that profiles resulting CSVs

#### Risks
- Network or authentication failures stop the process

---

### 🧠 Tags
@ai-role: orchestrator
@ai-intent: fetch data
@ai-cadence: run-preferred
@ai-risk-recall: medium
@ai-semantic-scope: CLI
@ai-coordination: sequential
