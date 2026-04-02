# Module: <module.path>
> <1–3 sentences plain-English summary>

@ai-path: <module.path>
@ai-source-file: <file.py>
@ai-role: <enum: analyst | diagnostician | presenter | segment-analyst | orchestrator | tool | visualizer>
@ai-intent: "<short purpose sentence>"
@ai-version: 0.1.0
@ai-risk-performance: "<note on compute/memory sensitivity>"
@ai-risk-drift: "<note on what could cause this module to go stale>"
@ai-snowflake-tables: <comma-separated table names, or none>
@ai-stat-parameters: <config fields that affect raw statistic computation — changing these requires re-running expensive tests; omit if module has no config dataclass>
@ai-threshold-parameters: <config fields that only gate pre-computed stats — safe to vary in vectorized re-classification or Monte Carlo search; omit if not applicable>
@ai-used-by: <comma-separated modules or 'developer'>
@ai-downstream: <comma-separated outputs or modules>

---

### 🎯 Intent & Responsibility
- …

---

### 📥 Inputs & 📤 Outputs
| Direction | Name | Type | Description |
|-----------|------|------|-------------|
| 📥 In | … | … | … |
| 📤 Out | … | … | … |

> For DataFrames, list column names and types in the Description column.

---

### 🔗 Dependencies
- Python: …
- Internal: …
- Snowflake tables: …

---

### 🤝 Integration & Coordination
- Upstream: …
- Downstream: …
- Coordination mechanics: …

---

### ⚠️ Risks & Edge Cases
- …

---

### 🗣️ Notes
- …

---

### 📌 Pipeline Integration
- @ai-pipeline-order: …

---

### 🧠 Tags
@ai-role: …
@ai-intent: …
@ai-cadence: <run-preferred | drift-preferred>
@ai-semantic-scope: …
@ai-coordination: …
