# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: profiler_cli
- @ai-source-files: [profiler_cli.py]
- @ai-role: cli
- @ai-intent: "Typer-based interface for running DataProfiler using config files"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: medium
- @ai-risk-performance: low
- @ai-risk-drift: "Config schema may evolve with GUI integration"
- @ai-used-by: developer
- @ai-downstream: reports,plots

# Module: profiler_cli
> Command line entrypoint using Typer to profile datasets defined in JSON/YAML configs.

---

### 🎯 Intent & Responsibility
- Parse configuration files providing dataset paths, field selections and type hints
- Invoke `DataProfiler` for univariate analysis and optional `BivariateProfiler`
- Write markdown or HTML reports to a specified output directory

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | config | `List[Path]` | paths to JSON/YAML configuration files |
| 📥 In | analyses | `List[str]` | names of analyses to run (`univariate`, `bivariate`) |
| 📤 Out | reports | `List[str]` | generated report file paths |
| 📤 Out | plots | `List[str]` | images from bivariate analysis |

---

### 🔗 Dependencies
- Typer
- pandas
- DataProfiler, BivariateProfiler
- optional `PyYAML` for YAML configs

---

### 🗣 Dialogic Notes
- Designed for CLI usage ahead of planned GUI
- Accepts absolute or relative paths for flexible integration

---

### 9 Pipeline Integration
#### Coordination Mechanics
- Executed by developers to profile datasets via config-driven inputs
- Loops through datasets and pair definitions from config

#### Integration Points
- Upstream: configuration files created manually or by other tools
- Downstream: profiling reports and bivariate plots for further analysis

#### Risks
- Config schema not yet finalized
- Large datasets may slow execution

---

### 🧠 Tags
@ai-role: cli
@ai-intent: config-driven profiler
@ai-cadence: run
@ai-risk-recall: medium
@ai-semantic-scope: CLI
@ai-coordination: sequential execution
