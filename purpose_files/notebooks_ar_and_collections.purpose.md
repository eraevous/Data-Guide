# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: notebooks.ar_and_collections
- @ai-source-files: [src/notebooks/AR_and_Collections.ipynb]
- @ai-role: analysis
- @ai-intent: "Investigate accounts receivable aging and collection patterns"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: high
- @ai-risk-performance: medium
- @ai-risk-drift: "Placeholder code with Windows paths"
- @ai-used-by: developer
- @ai-downstream: csv_reports,plots

# Module: notebooks.ar_and_collections
> Exploratory notebook analyzing outstanding claims, payments, and AR buckets.

---

### 🎯 Intent & Responsibility
- Load aged AR, outstanding claims, payments, and statement data
- Compute AR summaries by responsible party and bucket
- Visualize collection timelines and payer delays
- Prepare features for predicting claim risk and default likelihood

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | csv_files | `Dict[str,str]` | dataset paths for AR reports and transactions |
| 📤 Out | aged_ar_plots | `List[str]` | visualizations of AR distribution |
| 📤 Out | analytic_tables | `Dict[str,str]` | CSV paths of aggregated metrics |

---

### 🔗 Dependencies
- pandas, numpy, matplotlib, seaborn
- profiler (local module)

---

### 🗣 Dialogic Notes
- Contains provisional answers dictionary; not yet wired into CLI
- Overlaps with `Tighted_AR_and_Collections.ipynb`

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Notebook runs in an ad‑hoc fashion using local directories
- Potential candidate for a command line tool to generate AR dashboards

#### Integration Points
- Upstream: transformed data from ETL pipeline
- Downstream: manual inspection and future ML models

#### Risks
- Manual data paths risk stale inputs
- Analyses may expose PHI if shared

---

### 🧠 Tags
@ai-role: analysis
@ai-intent: ar collections study
@ai-cadence: drift-preferred
@ai-risk-recall: medium
@ai-semantic-scope: notebook
@ai-coordination: manual execution
