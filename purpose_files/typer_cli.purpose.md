# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: typer_cli
- @ai-source-files: [src/typer_cli.py]
- @ai-role: cli
- @ai-intent: "Typer-based interface for running DataProfiler via config"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: medium
- @ai-risk-drift: "Config schema may evolve"
- @ai-used-by: developer
- @ai-downstream: data_profiler

# Module: typer_cli
> Command line entry point loading YAML/JSON configuration to orchestrate dataset profiling.

---

### 🎯 Intent & Responsibility
- Parse config containing dataset paths, field selections, and type hints
- Instantiate `DataProfiler` and `BivariateProfiler` as requested
- Write profiling reports to an output directory in chosen format
- Expose flexible options for which analyses to execute

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | config | `Path` | YAML/JSON config file |
| 📥 In | output_dir | `Path` | destination folder for reports |
| 📥 In | analyses | `List[str]` | selected analysis steps |
| 📤 Out | reports | `List[str]` | generated report file paths |

---

### 🔗 Dependencies
- `typer`, `pyyaml`
- `pandas`
- `DataProfiler`
- `BivariateProfiler`

---

### 🗣 Dialogic Notes
- API keys from config are currently unused but reserved for future features
- Bivariate analysis supports predefined column pairs

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Invoked manually via `python src/typer_cli.py profile <config>`
- For each dataset, sequentially runs profiling and optional bivariate plots

#### Integration Points
- Upstream: configuration files with dataset info
- Downstream: markdown or HTML reports written to disk

#### Risks
- Misconfigured paths cause runtime errors
- Large datasets may impact performance

---

### 🧠 Tags
@ai-role: cli
@ai-intent: config-driven profiling
@ai-cadence: run-preferred
@ai-risk-recall: medium
@ai-semantic-scope: CLI
@ai-coordination: sequential
