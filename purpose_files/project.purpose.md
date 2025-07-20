# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: project
- @ai-source-files: [README.md, pyproject.toml, requirements.txt]
- @ai-role: documentation
- @ai-intent: "Describe overall project setup and dependencies"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: low
- @ai-risk-performance: low
- @ai-risk-drift: "Dependencies may change as modules evolve"
- @ai-used-by: developers
- @ai-downstream: package_install

# Module: project
> Top-level project files providing installation instructions and dependency list.

---

### 🎯 Intent & Responsibility
- Document how to install and run the Data Guide package
- Maintain dependency lists for local development

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | N/A | N/A | Project documentation files |
| 📤 Out | requirements | `List[str]` | Python package requirements |

---

### 🔗 Dependencies
- `pyproject.toml` defines dependencies and build metadata
- `requirements.txt` mirrors dependencies for quick setup

---

### 🗣 Dialogic Notes
- Referenced by README and developer onboarding guides

---

### 🧠 Tags
@ai-role: documentation
@ai-intent: setup guide
@ai-cadence: drift
@ai-semantic-scope: repo
@ai-coordination: onboarding
