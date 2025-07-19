# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.data_transform
- @ai-source-files: [data_transform.py]
- @ai-role: transformer
- @ai-intent: "Data cleaning utilities for pipeline use"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: low
- @ai-risk-drift: "Duplicated with root data_transform"
- @ai-used-by: pipeline_transformed
- @ai-downstream: cleaned_datasets

# Module: data_pipeline.data_transform
> Provides static methods for null handling, date conversion, anonymization and joining.

---

### 🎯 Intent & Responsibility
- Validate required columns exist
- Offer column-specific null filling strategies
- Convert date columns to pandas datetime
- Anonymize sensitive fields by hashing
- Merge datasets on keys with suffix handling

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | df | `pd.DataFrame` | dataset to modify |
| 📥 In | column_strategies | `dict` | per-column null fill rules |
| 📤 Out | df | `pd.DataFrame` | transformed dataset |

---

### 🔗 Dependencies
- pandas
- datetime

---

### 🗣 Dialogic Notes
- Mirror of top-level DataTransform; consolidation recommended

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Called after data_pull to clean raw datasets

#### Integration Points
- Upstream: CSVs from `data_pull`
- Downstream: profilers or bivariate analysis

#### Risks
- Inconsistent logic if both transform modules diverge

---

### 🧠 Tags
@ai-role: transformer
@ai-intent: pipeline cleanup
@ai-cadence: run-preferred
@ai-risk-recall: low
@ai-semantic-scope: DataFrame
@ai-coordination: preprocessing
