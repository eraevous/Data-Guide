# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: etl-data_from_pdf
- @ai-source-files: [etl-data_from_pdf.py]
- @ai-role: etl
- @ai-intent: "Extract structured data from PDFs for later profiling"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: high
- @ai-risk-performance: low
- @ai-risk-drift: "Regex based extraction may fail on different PDF formats"
- @ai-used-by: developer
- @ai-downstream: csv,json

# Module: etl-data_from_pdf
> Utility script converting PDF invoices into structured JSON/CSV for inclusion in the EDA pipeline.

---

### 🎯 Intent & Responsibility
- Open PDFs and extract raw text via `pdfplumber`
- Parse text with regex to capture fields and line items
- Save extracted data as JSON or CSV

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | pdf_path | `str` | path to source PDF file |
| 📥 In | file_format | `str` | desired output format ('json' or 'csv') |
| 📤 Out | parsed_data | `dict` | structured representation of invoice |
| 📤 Out | output_file | `str` | path to saved JSON or CSV |

---

### 🔗 Dependencies
- pdfplumber
- pandas
- json, re

---

### 🗣 Dialogic Notes
- Intended as an example; regex patterns must be adjusted per PDF layout

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Run manually before pipeline to generate CSVs for profiling

#### Integration Points
- Upstream: raw PDF invoices
- Downstream: pipeline scripts reading the generated CSV

#### Risks
- Parsing errors may silently drop fields

---

### 🧠 Tags
@ai-role: etl
@ai-intent: pdf extraction
@ai-cadence: run-preferred
@ai-risk-recall: high
@ai-semantic-scope: invoice
@ai-coordination: preprocessing
