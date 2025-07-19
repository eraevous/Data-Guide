# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_transform
- @ai-source-files: [data_transform.py]
- @ai-role: transformer
- @ai-intent: "Utility functions for cleaning and joining data"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: low
- @ai-risk-drift: "Data types may shift depending on upstream CSV formats"
- @ai-used-by: pipeline,main_pipeline
- @ai-downstream: transformed_datasets

# Module: data_transform
> Provides static methods to sanitize, convert and merge DataFrames.

---

### 🎯 Intent & Responsibility
- Validate required columns before transformations
- Handle null values globally or per-column
- Convert date strings or unix timestamps to datetime
- Join datasets on a key and maintain suffixes
- Optionally log operations for auditing

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | df1/df2 | `pd.DataFrame` | input dataframes |
| 📥 In | columns | `List[str]` | column names used for transformations |
| 📥 In | strategy | `str` | null-handling strategy ('drop','fill','median') |
| 📤 Out | df | `pd.DataFrame` | transformed dataframe |

---

### 🔗 Dependencies
- pandas
- datetime

---

### 🗣 Dialogic Notes
- Designed as static-only; no internal state
- Expects moderate dataset size

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Used by pipelines after profiling to clean or merge data
- Functions can append to a log list for step tracking

#### Integration Points
- Upstream: raw DataFrames from CSVs or API pull
- Downstream: DataProfiler for transformed datasets

#### Risks
- Incorrect column mapping may raise errors

---

### 🧠 Tags
@ai-role: transformer
@ai-intent: cleanup utilities
@ai-cadence: run-preferred
@ai-risk-recall: low
@ai-semantic-scope: DataFrame
@ai-coordination: preprocessing
