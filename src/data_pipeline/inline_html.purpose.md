# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: data_pipeline.inline_html
- @ai-source-files: [inline_html.py]
- @ai-role: utility
- @ai-intent: "Convert external resources in HTML to inline Base64"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: low
- @ai-risk-performance: low
- @ai-risk-drift: "Limited error handling; environment differences may break"
- @ai-used-by: developer
- @ai-downstream: html_files

# Module: inline_html
> Reads an HTML file, embeds linked images as Base64, and writes a standalone HTML file.

---

### 🎯 Intent & Responsibility
- Parse HTML using BeautifulSoup
- Convert image tags referencing files into inline data URIs
- Output a single HTML document with no external dependencies

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | input_file | `str` | path to original HTML |
| 📤 Out | output_file | `str` | path to self-contained HTML |

---

### 🔗 Dependencies
- BeautifulSoup
- os
- Python mimetypes module

---

### 🗣 Dialogic Notes
- Useful for packaging HTML reports with embedded plots

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Standalone script, can be invoked after report generation

#### Integration Points
- Upstream: markdown or HTML report
- Downstream: final deliverable for sharing

#### Risks
- Large images may significantly increase file size

---

### 🧠 Tags
@ai-role: utility
@ai-intent: embed resources
@ai-cadence: run-preferred
@ai-risk-recall: low
@ai-semantic-scope: html
@ai-coordination: postprocess
