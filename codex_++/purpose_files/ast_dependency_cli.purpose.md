@ai-path: ast_dependency_cli
@ai-source-file: ast_dependency_cli.py
@ai-role: tool
@ai-intent: "Extract function-level call graphs from Python codebases via AST parsing and export as CSV edge lists or adjacency matrices"
@ai-version: 0.1.0
@ai-risk-performance: "Low — AST parsing is fast; scales linearly with codebase size"
@ai-risk-drift: "Python AST interface is stable; output schema (caller, callee, file) unlikely to change"
@ai-snowflake-tables: none
@ai-used-by: developer
@ai-downstream: CSV edge list, adjacency matrix CSV

# Module: ast_dependency_cli
> CLI tool that walks a Python codebase using the `ast` module, extracts function-level call relationships, and exports a dependency graph as a CSV edge list or adjacency matrix. Configurable via `.graphconfig.json` for directory exclusions and output format. Useful for understanding module coupling and identifying highly-connected functions.

---

### 🎯 Intent & Responsibility
- Recursively scan a Python source directory (optional exclusion list)
- Parse each `.py` file with `ast` to identify function definitions and call sites
- Build a directed call graph: (caller_function, callee_function, source_file)
- Export as CSV edge list or square adjacency matrix
- Accept configuration from `.graphconfig.json` if present

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | `--source-dir` | `str` (CLI arg) | Root directory to scan |
| 📥 In | `--recursive` | `bool` (CLI flag) | Whether to recurse into subdirectories |
| 📥 In | `--exclude` | `List[str]` (CLI arg) | Directory names to skip |
| 📥 In | `.graphconfig.json` | JSON file | Optional; specifies source_dir, exclude_dirs, output_format |
| 📤 Out | edge list CSV | `pd.DataFrame` | Columns: caller, callee, source_file |
| 📤 Out | adjacency matrix CSV | `pd.DataFrame` | Square matrix; rows/cols are function names; values are call counts |

---

### 🔗 Dependencies
- Python: ast, pandas, typer, pathlib
- Internal: none
- Snowflake: none

---

### 🤝 Integration & Coordination
- Upstream: Python source files in the target directory
- Downstream: CSV files consumed by graph visualization tools (e.g., `transitions.py`) or manual analysis
- Coordination mechanics: Standalone CLI; `.graphconfig.json` provides default config to avoid repetitive CLI args

---

### ⚠️ Risks & Edge Cases
- Dynamic calls (e.g., `getattr(obj, fn)()`) are invisible to AST parsing — graph is conservative
- Functions with identical names across files are merged unless source_file is used as disambiguator
- Very large codebases with many functions may produce wide adjacency matrices

---

### 🗣️ Notes
- This tool is the "self-referential" utility of this repo — it can analyze its own codebase
- Edge list output is preferable for downstream graph tools; adjacency matrix is better for quick manual inspection
- The `.graphconfig.json` convention mirrors the Prior Art project's pattern of config-over-flags

---

### 📌 Pipeline Integration
- @ai-pipeline-order: standalone
- Source files → AST parsing → CSV output

---

### 🧠 Tags
@ai-role: tool
@ai-intent: Python codebase dependency graph extraction
@ai-cadence: run-preferred
@ai-semantic-scope: developer tooling
@ai-coordination: standalone CLI
