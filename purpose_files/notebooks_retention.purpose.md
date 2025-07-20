# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: notebooks.retention
- @ai-source-files: [src/notebooks/Retention.ipynb]
- @ai-role: analysis
- @ai-intent: "Explore patient churn metrics and payment timing"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: high
- @ai-risk-performance: medium
- @ai-risk-drift: "Hard coded file paths and manual steps"
- @ai-used-by: developer
- @ai-downstream: csv_reports,plots

# Module: notebooks.retention
> Jupyter notebook containing survival analysis and revenue timing investigations for Juniper Dentistry.

---

### 🎯 Intent & Responsibility
- Load multiple transformed CSV datasets from `data_pipeline`
- Derive retention metrics such as patient lifespan and visit history
- Produce Kaplan–Meier curves and Cox proportional hazards models
- Join transactions and charges to calculate time to payment
- Export aggregated tables like `financial_timeline.csv` and `time_to_payments.csv`

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | csv_files | `Dict[str,str]` | file paths to transformed datasets |
| 📤 Out | financial_timeline | `str` | CSV path with sequential billing events |
| 📤 Out | time_to_payments | `str` | CSV path with payment allocation per procedure |
| 📤 Out | plots | `List[str]` | saved PNG figures for survival curves and distributions |

---

### 🔗 Dependencies
- pandas, numpy, matplotlib, seaborn, lifelines
- profiler (local module)

---

### 🗣 Dialogic Notes
- Many exploratory cells remain; conversion to functions will improve reuse
- Uses custom carriers and fee schedules unique to Juniper Dentistry

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Notebook expects local Windows directory structure for inputs/outputs
- Designed to be run manually; no parameterization yet

#### Integration Points
- Upstream: datasets from `data_pipeline` transforms
- Downstream: manual review of exported CSVs and plots

#### Risks
- Environment-specific paths hinder portability
- Computations may leak PHI if shared externally

---

### 🧠 Tags
@ai-role: analysis
@ai-intent: retention study
@ai-cadence: drift-preferred
@ai-risk-recall: medium
@ai-semantic-scope: notebook
@ai-coordination: manual execution
