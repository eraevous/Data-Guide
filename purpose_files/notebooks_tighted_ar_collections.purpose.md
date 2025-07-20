# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: notebooks.tighted_ar_and_collections
- @ai-source-files: [src/notebooks/Tighted_AR_and_Collections.ipynb]
- @ai-role: analysis
- @ai-intent: "Refined AR analysis notebook with preliminary class structure"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: high
- @ai-risk-performance: medium
- @ai-risk-drift: "Subset of AR notebook, still exploratory"
- @ai-used-by: developer
- @ai-downstream: csv_reports,plots

# Module: notebooks.tighted_ar_and_collections
> Streamlined version of the AR investigations focusing on visualizing aging buckets.

---

### 🎯 Intent & Responsibility
- Load AR datasets and display first looks at the data
- Provide `AgedARVisualizer` class to reshape buckets
- Mirror steps from the broader AR notebook but in a more organized manner

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | csv_files | `Dict[str,str]` | file paths to aged AR and payments |
| 📤 Out | aged_ar_visuals | `List[str]` | histograms and heatmaps of AR status |

---

### 🔗 Dependencies
- pandas, numpy, matplotlib

---

### 🗣 Dialogic Notes
- Serves as a starting point for turning AR analysis into a library module

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Manual notebook execution with environment-specific path setup

#### Integration Points
- Upstream: transformed AR datasets from ETL
- Downstream: potential inclusion in CLI tools

#### Risks
- Shares same path issues as original notebook
- Duplicated logic needs consolidation

---

### 🧠 Tags
@ai-role: analysis
@ai-intent: ar visualizer prototype
@ai-cadence: drift-preferred
@ai-risk-recall: medium
@ai-semantic-scope: notebook
@ai-coordination: manual execution
