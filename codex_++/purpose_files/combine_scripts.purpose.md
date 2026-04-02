@ai-path: combine_scripts
@ai-source-file: combine_scripts.py
@ai-role: tool
@ai-intent: "Concatenate Python files from a directory tree into a single monolithic script with module docstring headers and a summary log"
@ai-version: 0.1.0
@ai-risk-performance: "Low — pure file I/O; output size scales with source files"
@ai-risk-drift: "Stable utility; risk is encoding issues with non-UTF8 source files"
@ai-snowflake-tables: none
@ai-used-by: developer
@ai-downstream: combined .py file, summary CSV log

# Module: combine_scripts
> CLI utility that walks a directory tree, collects `.py` files from specified subdirectories, extracts module-level docstrings, and concatenates them into a single output file with docstring headers prepended. Generates a summary CSV log with per-file line counts. Useful for producing monolithic scripts for environments without package support or for prompt-injection into LLM contexts.

---

### 🎯 Intent & Responsibility
- Accept a root directory and optional subdirectory filter via CLI
- Walk matching subdirectories and collect `.py` files
- Extract module-level docstrings from each file
- Concatenate all files into a single output `.py` with docstring sections prepended
- Write a summary CSV log: (filename, line_count, docstring_present)

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | root directory | `str` (CLI arg) | Top-level directory to search |
| 📥 In | subdirectory filter | `List[str]` (optional CLI arg) | Which subdirectories to include |
| 📤 Out | combined script | `.py` file | All matched files concatenated with docstring headers |
| 📤 Out | summary log | `summary.csv` | Columns: filename, line_count, has_docstring |

---

### 🔗 Dependencies
- Python: csv, pathlib, typer, os
- Internal: none
- Snowflake: none

---

### 🤝 Integration & Coordination
- Upstream: Python source files in target directories
- Downstream: Combined `.py` output — typically fed into LLM prompts or used for distribution
- Coordination mechanics: Standalone CLI; no inter-script dependencies

---

### ⚠️ Risks & Edge Cases
- Non-UTF-8 encoded files will raise on read — add encoding handling if non-ASCII sources are included
- Concatenation order is filesystem-dependent — if ordering matters, an explicit sort or manifest should be added
- Name collisions between functions across files are invisible in the combined output

---

### 🗣️ Notes
- Primary use case is combining Predictions/ scripts for LLM context injection or sharing
- The summary CSV log is intentionally lightweight — it records what was combined, not what was skipped

---

### 📌 Pipeline Integration
- @ai-pipeline-order: standalone
- Source files → concatenation → combined output + summary CSV

---

### 🧠 Tags
@ai-role: tool
@ai-intent: script consolidation utility
@ai-cadence: run-preferred
@ai-semantic-scope: developer tooling
@ai-coordination: standalone CLI
