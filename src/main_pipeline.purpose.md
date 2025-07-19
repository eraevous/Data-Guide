# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: main_pipeline
- @ai-source-files: [main_pipeline.py]
- @ai-role: orchestrator
- @ai-intent: "Example pipeline demonstrating profiling and transformation"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: low
- @ai-risk-performance: low
- @ai-risk-drift: "Demonstration script; not production ready"
- @ai-used-by: developer
- @ai-downstream: data_profiler,data_transform

# Module: main_pipeline
> Example script using seaborn's Titanic dataset to showcase profiling workflow.

---

### 🎯 Intent & Responsibility
- Load a sample dataset (Titanic via seaborn)
- Profile raw data using DataProfiler
- Apply transformations via DataTransform
- Profile transformed data and write markdown reports

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | none | | uses builtin dataset |
| 📤 Out | reports | `List[str]` | generated markdown summaries |

---

### 🔗 Dependencies
- pandas, seaborn
- DataProfiler
- DataTransform

---

### 🗣 Dialogic Notes
- Serves as a template for customizing the pipeline

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Runs sequential steps: profile -> transform -> profile again

#### Integration Points
- Upstream: builtin dataset or user-supplied dataset
- Downstream: Markdown reports for manual review

#### Risks
- None significant; demonstration only

---

### 🧠 Tags
@ai-role: orchestrator
@ai-intent: demonstration pipeline
@ai-cadence: run-preferred
@ai-risk-recall: low
@ai-semantic-scope: tutorial
@ai-coordination: sequential execution
