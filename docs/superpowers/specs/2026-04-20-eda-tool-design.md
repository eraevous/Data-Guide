# Data-Guide: General-Purpose EDA Tool — Design Spec
**Date:** 2026-04-20
**Status:** Approved

---

## 1. Goal

Transform Data-Guide into a general-purpose EDA tool usable by both technical users (CLI/config) and non-technical users (guided interactive UX). Primary outputs are static HTML reports (MVP), live Streamlit dashboards (Phase 2), and a dashboard constructor (Phase 3). All org-specific code is retired and replaced with generic, configurable components safe for public release.

---

## 2. Architecture

Four layers, one clean data flow:

```
Data Source → Connector → GuideDataFrame → Profiler → ProfilingResult → Renderer → Output
```

```
src/
  connectors/        # Data source adapters
  core/              # Canonical data model, type resolution, SchemaContract
  profilers/         # Univariate + bivariate analysis (migrated from existing engine)
  outputs/           # StaticReportRenderer, DashboardRenderer, DashboardConstructor
  cli.py             # Thin Typer CLI — guided + config-driven entry point
  pipeline.py        # Programmatic API — composes layers for scripted use

# RETIRED
src/data_pipeline/   # Replaced entirely by connectors/
src/notebooks/       # Gitignored — org-specific, not published
```

**Key principle:** Every connector produces a `GuideDataFrame`. Every renderer consumes a `ProfilingResult`. The profiler is the only component that touches both.

---

## 3. Canonical Data Model

The preferred intermediate format is a **long-format DataFrame** with these columns:

| Column | Required | Description |
|---|---|---|
| `key` | Soft | One or more identifier columns (e.g. patient_id, date) |
| `context` | Soft | One or more grouping/segmentation columns (e.g. location, provider) |
| `metric` | Yes | Measure name (e.g. `"balance_due"`, `"visit_count"`) |
| `value` | Yes | Measure value (numeric or string) |
| `data_type` | No — nullable | Semantic type hint; if blank, profiler infers |

**Schema modes:**
- `"long"` — matches the canonical format above; enables pivot-aware analysis
- `"wide"` — arbitrary column DataFrame; profiled column-by-column
- `"unknown"` — auto-detected at load time

**`SchemaContract` dataclass:**
```python
@dataclass
class SchemaContract:
    key_cols: list[str] = field(default_factory=list)
    context_cols: list[str] = field(default_factory=list)
    metric_col: str = "metric"
    value_col: str = "value"
    type_col: str | None = None
    mode: Literal["long", "wide", "unknown"] = "unknown"
```

**`GuideDataFrame`:** Thin wrapper around `pd.DataFrame` carrying a `SchemaContract` and source metadata (connector type, origin path/query). No forced pivoting — wide DataFrames are profiled as-is.

**`ProfilingResult`:** Output of the profiler. Carries univariate stats, bivariate results, data quality summary, and `annotations: dict[str, Narrative] | None = None` for future narrative framework integration (see Section 7).

---

## 4. Connectors Layer

All connectors implement `BaseConnector`:
```python
class BaseConnector(ABC):
    def connect(self) -> None: ...
    def load(self) -> GuideDataFrame: ...
```

**Connectors in MVP:**

| Connector | Source |
|---|---|
| `CSVConnector` | Local file path or glob |
| `ExcelConnector` | Local `.xlsx`/`.xls`, configurable sheet |
| `JSONConnector` | Local file |
| `SQLiteConnector` | Local `.db` file |
| `SQLConnector` | Any SQLAlchemy-compatible DB |
| `SnowflakeConnector` | Snowflake account |

**Credentials resolution order (first found wins):**
1. `--credentials path/to/creds.json` CLI flag
2. Env var `GUIDE_CREDENTIALS_FILE` (path to credentials file — reserved for future pipeline use)
3. Individual connector env vars (e.g. `SF_ACCOUNT`, `SF_USER`, `SF_PASSWORD`, `SF_WAREHOUSE`, `SF_DATABASE`, `SF_SCHEMA`)
4. Fail loudly with `CredentialsValidationError`

**Credentials file strict schema** (JSON or YAML):
```json
{
  "type": "snowflake",
  "account": "...",
  "user": "...",
  "password": "...",
  "warehouse": "...",
  "database": "...",
  "schema": "..."
}
```
`type` must match the connector. Missing required fields raise `CredentialsValidationError` at startup, not at query time.

**Safety rules:**
- No credentials ever in YAML config or committed code
- `.gitignore` includes: `*.credentials.json`, `*.credentials.yaml`, `creds/`, `session_cookies.pkl`, `debug_output.txt`
- YAML config is always safe to commit

**Example YAML config:**
```yaml
connector: snowflake
database: ANALYTICS
schema: PUBLIC
query: "SELECT * FROM patient_metrics"
schema_contract:
  metric_col: metric
  value_col: value
  type_col: data_type
```

---

## 5. Outputs Layer

All renderers consume `ProfilingResult`.

### 5.1 StaticReportRenderer (MVP)
- Produces a single self-contained HTML file
- All charts embedded as base64 — no server, no external assets
- Structure follows `templates/data_guide_template.md`:
  - Dataset overview (shape, source, schema mode)
  - Data quality summary (missingness, type distribution)
  - Univariate profiles per column/metric
  - Bivariate analysis (correlations, VIF, chi-square) if requested
  - Embedded matplotlib/seaborn plots
- PDF export: future nice-to-have, not in MVP

### 5.2 DashboardRenderer (Phase 2)
- Generates a runnable Streamlit app, writes to temp file, launches via `streamlit run`
- Interactive Plotly charts (replaces static matplotlib for dashboard mode)
- Filters for `context` columns, metric selector

### 5.3 DashboardConstructor (Phase 3 — design deferred)
- Produces a persistent, editable Streamlit app file from `ProfilingResult` + user preferences
- Design left open — informed by Phase 2 usage

**Output config in YAML:**
```yaml
outputs:
  - type: static_report
    path: reports/output.html
  - type: dashboard
    launch: true
```

---

## 6. CLI / Guided UX

Entry point: `src/cli.py` (replaces `typer_cli.py` and `profiler_cli.py`, both retired).

**Commands:**
- `guide run` — guided interactive mode; prompts for source, schema contract, outputs, credentials
- `guide run --config config.yaml` — fully non-interactive; reads everything from YAML
- `guide profile <file>` — quick single-file profile; HTML report to `./reports/`
- `guide validate <file>` — validate schema contract without full profile
- `guide version` — show version

`pyproject.toml` entry point stays as `guide`.

---

## 7. Narrative Extension Point

`ProfilingResult` carries:
```python
@dataclass
class Narrative:
    element_id: str
    text: str
    framework: str

annotations: dict[str, Narrative] | None = None
```

All renderers check for annotations per element and inject them if present, skip if `None`. When a narrative framework is added, a `NarrativeEngine` populates `ProfilingResult.annotations` before rendering — no renderer changes required.

---

## 8. Org-Specific Code Retirement

**Files to remove:**
- `src/data_pipeline/api_client.py` — org-specific API auth
- `src/data_pipeline/data_pull.py` — hardcoded endpoints and location IDs
- `src/data_pipeline/config.py` — internal dataset mappings with org-specific names
- `src/data_pipeline/main.py` — org-specific orchestration

**Files to migrate:**
- `src/data_pipeline/bivariate_profiler.py` → `src/profilers/bivariate_profiler.py`
- `src/data_pipeline/md_to_html.py`, `inline_html.py` → `src/outputs/html_utils.py`

**Files to gitignore:**
- `src/notebooks/*.ipynb` — contain hardcoded internal paths and proprietary analysis
- `*.credentials.json`, `*.credentials.yaml`, `creds/`
- `session_cookies.pkl`, `debug_output.txt`

**Purpose files to scrub:**
- `codex_++/purpose_files/api_client.purpose.md`
- `codex_++/purpose_files/data_pull.purpose.md`
- `codex_++/purpose_files/main.purpose.md`
- `codex_++/purpose_files/notebooks_retention.purpose.md`
- `codex_++/docs/NOTEBOOK_MODULARIZATION_PLAN.md` — remove org references

---

## 9. Phased Delivery

| Phase | Deliverable |
|---|---|
| 1 (MVP) | Connectors layer, `GuideDataFrame`, `SchemaContract`, `StaticReportRenderer`, `guide profile` + `guide run` CLI, org code retired, `.gitignore` updated |
| 2 | `DashboardRenderer` (Streamlit), Plotly charts, interactive filters |
| 3 | `DashboardConstructor`, persistent app file generation |
| Future | Narrative framework integration, PDF export, pipeline/headless mode (env var credentials), UMAP/HDBSCAN optional profilers |

---

## 10. Out of Scope (This Spec)

- Narrative framework design and content
- Dashboard constructor UI design (deferred to Phase 3)
- Automated testing strategy
- Deployment / hosting
- PDF export
