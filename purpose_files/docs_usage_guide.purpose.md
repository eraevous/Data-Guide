# @codex-role: architect
# @codex-objective: generate or upgrade `.purpose.md` with:
# - output schema
# - coordination logic
# - integration points
# - ecosystem anchoring
# Follow AGENTS.md G-10 and Section 9 enrichment instructions.
- @ai-path: docs.usage_guide
- @ai-source-files: [docs/USAGE_GUIDE.md]
- @ai-role: documentation
- @ai-intent: "Walk users through running the profiling pipeline"
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @schema-version: 0.3
- @ai-risk-pii: low
- @ai-risk-performance: low
- @ai-risk-drift: "May fall behind code changes"
- @ai-used-by: developers
- @ai-downstream: user_workflows

# Module: docs.usage_guide
> Provides step-by-step instructions for executing Data Guide pipelines.

---

### 🎯 Intent & Responsibility
- Outline typical setup and run commands
- Link to template reports

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | N/A | N/A | Documentation file |
| 📤 Out | guidance | `str` | Plain text walkthrough |

---

### 🔗 Dependencies
- README references this guide for more detail

---

### 🗣 Dialogic Notes
- Updated alongside CLI script changes

---

### 🧠 Tags
@ai-role: documentation
@ai-intent: tutorial
@ai-cadence: drift
@ai-semantic-scope: docs
@ai-coordination: onboarding
