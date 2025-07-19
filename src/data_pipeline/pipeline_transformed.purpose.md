# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.pipeline_transformed
- @ai-source-files: [pipeline_transformed.py]
- @ai-role: orchestrator
- @ai-intent: "Profile transformed datasets after cleaning"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: low
- @ai-risk-drift: "Relies on specific transformed CSV names"
- @ai-used-by: developer
- @ai-downstream: transformed_reports

# Module: pipeline_transformed
> Similar to `pipeline.py` but expects cleaned datasets and may generate additional metrics.

---

### 🎯 Intent & Responsibility
- Load cleaned CSV files from an input directory
- Optionally profile both raw and transformed versions
- Save markdown or HTML reports for each dataset

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | input_dir | `str` | directory of transformed CSVs |
| 📤 Out | report_files | `List[str]` | output report paths |

---

### 🔗 Dependencies
- pandas
- DataProfiler
- DataTransform
- os, sys

---

### 🗣 Dialogic Notes
- Many transformation steps are commented out; structure incomplete

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Intended for manual CLI execution after transformation

#### Integration Points
- Upstream: datasets produced by separate ETL scripts
- Downstream: bivariate analysis or report packaging

#### Risks
- Inconsistent custom_type dictionaries across datasets

---

### 🧠 Tags
@ai-role: orchestrator
@ai-intent: profiling cleaned data
@ai-cadence: run-preferred
@ai-risk-recall: medium
@ai-semantic-scope: CLI
@ai-coordination: sequential
