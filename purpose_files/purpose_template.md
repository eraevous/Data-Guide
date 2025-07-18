- @ai-path: <module.path.here>                     # e.g. core.memory
- @ai-source-files: [<file1.py>, <file2.py>]       # List of related Python source files
- @ai-role: <role>                                 # One-word functional role (e.g. memory, parser, summarizer)
- @ai-intent: "<brief role-specific purpose>"      # Short mission statement, e.g. "Store and simulate memory..."
- @ai-version: <semver>                            # e.g. 0.1.0
- @ai-generated: <true|false>                      # Whether AI generated the bulk of the file
- @ai-verified: <true|false>                       # Whether a human verified the content
- @schema-version: <version>                       # Purpose schema version (e.g. 0.3)
- @ai-risk-pii: <low|medium|high>                  # Risk of handling personal identifiable info
- @ai-risk-performance: <low|medium|high>          # Performance sensitivity (memory, compute, etc.)
- @ai-risk-drift: "<risk summary>"                 # Risk of drift/conflict from outdated data or references
- @ai-used-by: <comma-separated callers>           # e.g. core.retriever, core.orchestrator
- @ai-downstream: <comma-separated downstream>     # e.g. core.analysis.scanner

# Module: <module.name>
> <One-liner summary of module function>  
> _e.g., Provides simulated memory scaffolding for LLMs or contextual prompt injection._

---

### 🎯 Intent & Responsibility

- List key responsibilities in bullet form
- Start with verbs: “Extract…”, “Inject…”, “Summarize…”, “Route…”
- Include main functional units or modes if applicable

_Example:_
```markdown
- Persist short text frames for prompt augmentation
- Inject memory content into active LLM prompts
- Surface `.intent.md` fragments based on user query context
```

---

### 📥 Inputs & 📤 Outputs

| Direction | Name         | Type             | Description |
|-----------|--------------|------------------|-------------|
| 📥 In     | <input_name> | <type>           | <What it represents> |
| 📤 Out    | <output_name>| <type>           | <What it delivers>   |

📝 _Add entries for every key I/O of public methods. Types should match docstrings._

---

### 🔗 Dependencies

- List of imports or module calls outside this module
- Include internal (`core.config`) and external (`openai`, `json`) packages
- Prefer full path names for internal dependencies

---

### 🗣 Dialogic Notes

Freeform commentary for human readers and AI co-authors:

- Notes on assumptions, caveats, known limitations
- Suggested use patterns or things to avoid
- Meta commentary: _“not a full search system,”_ _“Codex-facing only,”_ etc.
- Future ideas or stability notes

---

### 9 Pipeline Integration

#### Coordination Mechanics:
- Describe how components in this module interact with one another.
- Mention phases like "before prompt send," "post-drift," "as fallback," etc.

#### Integration Points:
- Upstream: Components that call into this module
- Downstream: Components that depend on this module’s outputs

#### Risks:
- Note reuse, performance, statefulness, or outdated data hazards
- Any risk from caching, injection, or inferred memory structures

---

### 🧠 Tags

Custom AI metadata tags to assist in indexing, retrieval, or reasoning:

```markdown
@ai-role: <e.g. memory, parser>
@ai-intent: <reworded or supporting statement>
@ai-cadence: <run-preferred | drift-preferred | reactive | continuous>
@ai-risk-recall: <low|medium|high> 
@ai-semantic-scope: <e.g. .intent.md, raw prompt>
@ai-coordination: <e.g. proxy injection, drift reconciliation>
```

---

📌 **Tips for Using this Template**

- Treat `🎯 Intent & Responsibility` as the “What” and “Why”
- Treat `Inputs & Outputs` and `Pipeline Integration` as the “How”
- Treat `Tags`, `Dialogic Notes`, and `Dependencies` as the “Meta”
- Use this format for `.purpose.md` documentation across all modules for consistency and AI-augmented traceability
