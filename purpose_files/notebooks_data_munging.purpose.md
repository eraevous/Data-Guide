# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: notebooks.data_munging
- @ai-source-files: [src/notebooks/data munging.ipynb]
- @ai-role: preprocessing
- @ai-intent: "Prototype utilities for cleaning exported CSVs"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: low
- @ai-risk-drift: "Functions defined interactively; not packaged"
- @ai-used-by: developer
- @ai-downstream: data_pipeline

# Module: notebooks.data_munging
> Collection of early helper functions for timestamp conversion and currency fields.

---

### 🎯 Intent & Responsibility
- Provide `convert_unix_timestamps` for millisecond to datetime conversion
- Provide `treat_currency` to sanitize string amounts
- Define `procedure_map` dictionary of dental codes

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | df | `pd.DataFrame` | dataset containing raw columns |
| 📤 Out | cleaned_df | `pd.DataFrame` | DataFrame with converted or cleaned columns |

---

### 🔗 Dependencies
- pandas, numpy

---

### 🗣 Dialogic Notes
- Intended to migrate into `data_transform` module
- Currently lacks error handling and unit tests

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Functions executed manually during exploration

#### Integration Points
- Upstream: raw CSV exports
- Downstream: transformation scripts in `data_pipeline`

#### Risks
- Partial coverage of edge cases

---

### 🧠 Tags
@ai-role: preprocessing
@ai-intent: data cleaning helpers
@ai-cadence: drift-preferred
@ai-risk-recall: low
@ai-semantic-scope: notebook
@ai-coordination: manual execution
