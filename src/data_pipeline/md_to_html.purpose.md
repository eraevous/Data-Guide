# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.md_to_html
- @ai-source-files: [md_to_html.py]
- @ai-role: utility
- @ai-intent: "Convert Markdown files to HTML recursively"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: low
- @ai-risk-performance: low
- @ai-risk-drift: "Encoding assumptions may fail on exotic characters"
- @ai-used-by: developer
- @ai-downstream: html_reports

# Module: md_to_html
> Walks a directory tree converting all `.md` files to `.html` using Python markdown library.

---

### 🎯 Intent & Responsibility
- Accept directory path via CLI
- Read each Markdown file with UTF-8 or fallback encoding
- Write corresponding HTML files in place

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | directory | `str` | root folder to scan |
| 📤 Out | html_files | `List[Path]` | created HTML file paths |

---

### 🔗 Dependencies
- markdown
- pathlib, sys

---

### 🗣 Dialogic Notes
- Ignores asset references; use `inline_html` afterwards to embed images

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Optional post-processing step after report generation

#### Integration Points
- Upstream: Markdown reports from profiler
- Downstream: shareable HTML files

#### Risks
- None significant

---

### 🧠 Tags
@ai-role: utility
@ai-intent: markdown conversion
@ai-cadence: run-preferred
@ai-risk-recall: low
@ai-semantic-scope: docs
@ai-coordination: postprocess
