# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.config
- @ai-source-files: [config.py]
- @ai-role: config
- @ai-intent: "Provide dataset file mappings and type hints for the pipeline"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: low
- @ai-risk-performance: low
- @ai-risk-drift: "Paths may require environment adjustments"
- @ai-used-by: pipeline
- @ai-downstream: 

# Module: config
> Holds configuration variables used by data pulling and transformation modules.

---

### 🎯 Intent & Responsibility
- Centralize dataset paths and custom type hints
- Provide helper to resolve CSV paths given an input directory
- Define default input and output folders

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | input_dir | `str` | base folder for datasets |
| 📤 Out | csv_paths | `Dict[str,str]` | resolved CSV paths |
| 📤 Out | custom_types | `Dict[str,Dict[str,str]]` | type hints per dataset |

---

### 🔗 Dependencies
- None

---

### 🗣 Dialogic Notes
- Used by `pipeline.py` to avoid hard-coded paths

---

### 9 Pipeline Integration
#### Coordination Mechanics
- To be imported by ETL and pipeline scripts for shared constants

#### Integration Points
- Upstream: environment variables or config files
- Downstream: modules referencing these constants

#### Risks
- Without content, modules may hard-code paths elsewhere

---

### 🧠 Tags
@ai-role: config
@ai-intent: dataset configuration
@ai-cadence: drift-preferred
@ai-risk-recall: low
@ai-semantic-scope: configuration
@ai-coordination: setup
