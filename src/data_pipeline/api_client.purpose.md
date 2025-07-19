# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.api_client
- @ai-source-files: [api_client.py]
- @ai-role: client
- @ai-intent: "Session based API client for Dentrix Ascend endpoints"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: high
- @ai-risk-performance: medium
- @ai-risk-drift: "Endpoints or authentication may change"
- @ai-used-by: data_pull
- @ai-downstream: csv_files

# Module: api_client
> Handles authentication and HTTP requests, caching cookies to persist sessions.

---

### 🎯 Intent & Responsibility
- Authenticate with Dentrix Ascend using username and password
- Store session cookies for reuse
- Provide GET and POST helper `make_request`

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | username | `str` | login credential |
| 📥 In | password | `str` | login credential |
| 📥 In | url | `str` | endpoint URL |
| 📥 In | params/payload | `dict` | request data |
| 📤 Out | response_json | `dict` | parsed JSON response |

---

### 🔗 Dependencies
- requests
- pickle, os, json, sys

---

### 🗣 Dialogic Notes
- Exposes debugging output to `debug_output.txt`
- Auto-relogin logic is commented out

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Utilized by data pulling scripts to fetch reports

#### Integration Points
- Upstream: user credentials
- Downstream: `data_pull.py` storing CSVs

#### Risks
- Credentials stored in plain text in scripts

---

### 🧠 Tags
@ai-role: client
@ai-intent: session API access
@ai-cadence: run-preferred
@ai-risk-recall: medium
@ai-semantic-scope: http
@ai-coordination: polling
