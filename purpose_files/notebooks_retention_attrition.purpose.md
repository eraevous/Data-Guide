# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: notebooks.retention_and_attrition
- @ai-source-files: [src/notebooks/Retention_and_Attrition_Analysis.ipynb]
- @ai-role: analysis
- @ai-intent: "Segment patients by visit frequency and procedure history"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: high
- @ai-risk-performance: medium
- @ai-risk-drift: "Manual exploration with custom procedure mapping"
- @ai-used-by: developer
- @ai-downstream: segmentation_reports

# Module: notebooks.retention_and_attrition
> Notebook exploring active vs inactive patients and revenue impact.

---

### 🎯 Intent & Responsibility
- Map dental procedures into categories
- Compare active and inactive patient populations
- Estimate revenue loss from churned patients
- Outline steps for retention campaign targeting

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | csv_files | `Dict[str,str]` | patient detail and charges datasets |
| 📤 Out | churn_segments | `str` | CSV with patient segment statistics |
| 📤 Out | visualizations | `List[str]` | bar charts or scatter plots of churn drivers |

---

### 🔗 Dependencies
- pandas, numpy, seaborn, matplotlib
- profiler (local module)

---

### 🗣 Dialogic Notes
- Contains long dictionaries of procedure categories; needs deduplication
- Path handling is Windows-specific

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Notebook executed interactively to refine segments

#### Integration Points
- Upstream: patient detail exports from ETL
- Downstream: retention strategy documents

#### Risks
- Hard coded categories may not generalize

---

### 🧠 Tags
@ai-role: analysis
@ai-intent: attrition segmentation
@ai-cadence: drift-preferred
@ai-risk-recall: medium
@ai-semantic-scope: notebook
@ai-coordination: manual execution
