# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: run_profiler
- @ai-source-files: [run_profiler.py]
- @ai-role: cli
- @ai-intent: "Simple entry script to profile local CSVs"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: low
- @ai-risk-performance: low
- @ai-risk-drift: "Assumes hard-coded paths to data"
- @ai-used-by: developer
- @ai-downstream: markdown_reports

# Module: run_profiler
> Lightweight wrapper for DataProfiler to profile predefined CSV files.

---

### 🎯 Intent & Responsibility
- Load user provided CSVs from local directories
- Invoke `DataProfiler` on each dataset
- Save resulting markdown reports to disk

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | data_path | `str` | directory containing csv files |
| 📤 Out | report_files | `List[str]` | paths to markdown outputs |

---

### 🔗 Dependencies
- pandas
- DataProfiler
- os

---

### 🗣 Dialogic Notes
- Minimal script; duplicates functionality of `pipeline.py`

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Executed directly by developer for quick profiling

#### Integration Points
- Upstream: CSVs pulled from external sources
- Downstream: Markdown reports for review

#### Risks
- Hard-coded output directories may fail if not existent

---

### 🧠 Tags
@ai-role: cli
@ai-intent: quick profiling
@ai-cadence: run-preferred
@ai-risk-recall: low
@ai-semantic-scope: CLI
@ai-coordination: ephemeral
