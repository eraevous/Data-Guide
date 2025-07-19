# 🧭 **Codex++: Data Guide Project Description**

_(Unified Vision for Agentic, Narrative, and Modular Development)_

- @ai-path: data_guide/
- @ai-role: profiler, narrator, architect, reporter
- @ai-intent: "Create a modular, agentic framework for automated data profiling, analysis, and reporting that transforms raw tabular data into high-context, multi-format Data Guides for decision-making, quality control, and downstream development."
- @ai-version: 0.4.2
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: moderate
- @ai-risk-drift: "Highly sensitive to dataset complexity, bivariate modeling scope, and markdown/reporting schema. Recommend `.intent.md` triggers for metric conflicts, report overload, or ambiguity in output priority."
- @ai-used-by: core.reporting, data_cleanser, markdown_exporter, guide_exporter, archiver_agent
- @ai-downstream: feature_selector, EDA_generator, modeling_pipeline, client-facing_exporter

---

# Module: `data_guide/`
> Transforms tabular datasets into structured, insightful, and narrative-driven Data Guides—profiling metadata, quality, distributions, relationships, and story-relevant insights for technical and non-technical stakeholders alike.

---

## 🎯 Project Purpose

The **Data Guide** project serves as a **cognitive scaffold + agentic profiler** for evolving datasets. It converts raw or semi-cleaned tabular inputs into **explorable, exportable artifacts** that encode:

- **Profiling outputs** (numeric, categorical, temporal, string, special formats)
- **Quality metrics** (completeness, consistency, suspicious patterns, scoring)
- **Univariate and bivariate analyses**
- **Contextual guidance** (narratives, anomalies, feature alerts)
- **Business-aligned insight maps** (summaries, transformations, questions raised)
- **Export pipelines** (Markdown, HTML, PDF, PowerPoint)

---

## 🧠 Project Philosophy

Inspired by **multi-layered metaphors** (Data Journey, Factory, Atlas, Garden), the project is a modular system of intelligent, cooperating agents—each responsible for a different dimension of exploratory insight or data transformation. The guide is both a **product** (human-readable, shareable report) and a **process** (repeatable pipeline for cognitive automation).

---

## 🧩 Core Components

### 1. `ProfilerAgent` (Run)
- Calculates per-column summaries (counts, types, blanks, duplicates, entropy, skew, kurtosis, pattern detection)
- Handles numeric, string, datetime, boolean, phone/email/URL types
- Supports configurable quality scoring weights (via config file or schema block)
- Runs **temporal and spatial profiling** if patterns detected

### 2. `RelationalAnalyzer` (Run)
- Bivariate + multivariate correlation matrices
- Flagged relational anomalies (e.g., inverse dependence, duplicates in joins)
- Handles pairwise visualizations and entropy differentials

### 3. `MarkdownNarrator` (Drift)
- Generates human-readable reports with TOC, per-column blocks, summary callouts
- Flags schema drift, ambiguous metrics, outlier-heavy fields
- Embeds story-ready phrasing, e.g., “Column ‘Region’ is dominated by 3 values, limiting predictive power…”

### 4. `ConfigExtractor`
- Moves hardcoded logic into declarative YAML/JSON configs:
    - Quality scoring
    - Report preferences (verbosity, language)
    - Suppression or elevation of metric groups

### 5. `ExporterAgent`
- Converts Markdown → HTML, PDF, PPT
- Supports metaphoric overlays: Journey (sections), Factory (pipeline steps), Atlas (navigational frames)

---

## 🔄 Run/Drift Cadence

- **Run**: Triggered when data is profiled, joined, or summarized. Prioritize implementation logic and interim `.intent.md` capture.
- **Drift**: Triggered when:
    - Output complexity exceeds readable scale
    - Reporting conflicts arise (e.g., duplicated columns, merged semantics)
    - New metaphor framing is desired
    - `.purpose.md` changes are warranted

---

## ⚙️ Coordination & Integration

### Coordination Roles:
| Agent | Function |
|-------|----------|
| ProfilerAgent | Measures, validates, and scores |
| NarratorAgent | Interprets and frames outputs |
| ConfigAgent | Externalizes hardcoded logic |
| ExporterAgent | Formats and routes outputs |
| GuideOrchestrator | Oversees multi-agent collaboration, pipelines output |

### Integration Points:
- `data_cleanser/` for pre-profiling transformations
- `model_selector/` for downstream ML readiness scoring
- `archiver/` for output versioning, artifact timestamping
- `core.cli.kairos` for pipeline invocations via `kairos profile run --input ./data/raw.csv`

---

## 📘 Governance Triggers

- Missing `@ai-role` → Block commit
- `.purpose.md` outdated or generic → Fork into Drift
- `@ai-risk-performance: high` without test coverage → Flag in `.intent.md`
- Multiple conflicting profiling reports detected → Auto-fork guide into “clarify intent” thread

---

## 🧱 File Structure (Recommended)

data_guide/  
├── profiler/  
│ ├── string_metrics.py  
│ ├── numeric_metrics.py  
│ ├── datetime_metrics.py  
├── relationships/  
│ ├── bivariate_analysis.py  
│ ├── correlation_matrix.py  
├── reporting/  
│ ├── markdown_generator.py  
│ ├── export_html.py  
│ ├── export_ppt.py  
├── configs/  
│ ├── quality_weights.yaml  
│ ├── report_schema.json  
├── orchestrator.py  
├── guide_exporter.py  
└── README.md

---

## 🔮 Future Enhancements

- `IntentClassifier`: Uses prompts + schema + file diffs to auto-generate `.intent.md`
- `NarrativeRefiner`: Rewrite Markdown reports into domain-specific storytelling styles
- `TemplateRegistry`: Register and switch report formats per metaphor (e.g., Factory vs. Garden mode)
- `InsightSummarizer`: Learn from past guides to pre-prioritize suspicious patterns or business value
