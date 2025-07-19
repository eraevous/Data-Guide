# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.bivariate_profiler
- @ai-source-files: [bivariate_profiler.py]
- @ai-role: analysis
- @ai-intent: "Explore relationships between pairs of variables"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: high
- @ai-risk-drift: "Uses heavy numeric libraries; performance may vary"
- @ai-used-by: pipeline_transformed
- @ai-downstream: bivariate_plots

# Module: bivariate_profiler
> Provides correlation matrices, clustering metrics, logistic regression and other bivariate analyses.

---

### 🎯 Intent & Responsibility
- Produce correlation heatmaps for numeric data
- Calculate VIF, chi-squared and mutual information statistics
- Generate pairwise scatter plots and parallel coordinates
- Save bivariate analysis plots to a folder

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | dataframe | `pd.DataFrame` | dataset to analyze |
| 📤 Out | figures | `List[str]` | paths to generated PNG plots |
| 📤 Out | metrics | `dict` | computed statistics per pair |

---

### 🔗 Dependencies
- pandas, numpy, seaborn, matplotlib
- scipy, sklearn, statsmodels, geopandas

---

### 🗣 Dialogic Notes
- Contains advanced analytics; may require sample size reduction for speed
- Some functions may overlap with other profiling modules

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Typically invoked after basic profiling to analyze inter-feature relationships

#### Integration Points
- Upstream: cleaned dataset from DataTransform
- Downstream: visualizations for reports

#### Risks
- High memory usage when computing pairwise metrics on wide datasets

---

### 🧠 Tags
@ai-role: analysis
@ai-intent: bivariate statistics
@ai-cadence: drift-preferred
@ai-risk-recall: high
@ai-semantic-scope: analytics
@ai-coordination: offline
