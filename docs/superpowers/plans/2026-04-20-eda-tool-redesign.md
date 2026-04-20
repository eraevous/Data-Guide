# Data-Guide EDA Tool Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor Data-Guide into a layered, general-purpose EDA tool with pluggable connectors, a canonical long-format data model, and a static HTML report renderer — while retiring all org-specific code.

**Architecture:** Four layers: `connectors/` (data source adapters) → `core/` (GuideDataFrame + SchemaContract) → `profilers/` (migrated engine) → `outputs/` (renderers). Each task ends in a committed, working state. The existing `DataProfiler` engine is preserved and migrated, not rewritten.

**Tech Stack:** Python 3.11+, pandas, typer, pyyaml, matplotlib, seaborn, missingno, scipy, statsmodels, scikit-learn, snowflake-connector-python (optional), sqlalchemy (optional), openpyxl (optional)

---

## File Map

**Create:**
- `src/core/__init__.py`
- `src/core/models.py` — `SchemaContract`, `GuideDataFrame`, `ProfilingResult`, `Narrative`
- `src/connectors/__init__.py`
- `src/connectors/base.py` — `BaseConnector` ABC
- `src/connectors/credentials.py` — credentials file loading + validation
- `src/connectors/csv_connector.py`
- `src/connectors/excel_connector.py`
- `src/connectors/json_connector.py`
- `src/connectors/sqlite_connector.py`
- `src/connectors/sql_connector.py`
- `src/connectors/snowflake_connector.py`
- `src/profilers/__init__.py`
- `src/profilers/univariate.py` — thin wrapper delegating to migrated `DataProfiler`
- `src/outputs/__init__.py`
- `src/outputs/html_utils.py` — migrated from `inline_html.py` + `md_to_html.py`
- `src/outputs/static_report.py` — `StaticReportRenderer`
- `src/cli.py` — new Typer entry point
- `tests/__init__.py`
- `tests/test_models.py`
- `tests/test_credentials.py`
- `tests/test_connectors.py`
- `tests/test_static_report.py`
- `tests/test_cli.py`
- `tests/fixtures/sample.csv`
- `tests/fixtures/sample.xlsx`
- `tests/fixtures/sample.json`
- `tests/fixtures/sample.db`

**Modify:**
- `.gitignore` — add credentials, notebooks, session files
- `pyproject.toml` — update entry point, add optional deps, add pytest config
- `src/data_profiler.py` — no logic changes; update import path for `BivariateProfiler`
- `src/profilers/bivariate.py` — migrated from `src/data_pipeline/bivariate_profiler.py`

**Retire (delete after migration verified):**
- `src/data_pipeline/api_client.py`
- `src/data_pipeline/data_pull.py`
- `src/data_pipeline/config.py`
- `src/data_pipeline/main.py`
- `src/data_pipeline/pipeline.py`
- `src/data_pipeline/pipeline_transformed.py`
- `src/typer_cli.py`
- `src/profiler_cli.py`
- `src/pipeline.py`
- `src/main_pipeline.py`
- `src/run_profiler.py`
- `src/profiler.py`
- `codex_++/purpose_files/api_client.purpose.md`
- `codex_++/purpose_files/data_pull.purpose.md`
- `codex_++/purpose_files/main.purpose.md`
- `codex_++/purpose_files/notebooks_retention.purpose.md`

---

## Task 1: Update .gitignore and pyproject.toml

**Files:**
- Modify: `.gitignore`
- Modify: `pyproject.toml`

- [ ] **Step 1: Update .gitignore**

Replace the contents of `.gitignore` with:

```gitignore
# Datasets and large files
data/
*.csv
*.xlsx
*.gz
*.zip

# Credentials and secrets — NEVER commit these
*.credentials.json
*.credentials.yaml
creds/
session_cookies.pkl
debug_output.txt
.env

# Org-specific notebooks
src/notebooks/

# Build artifacts
*.pyc
__pycache__/
*.egg-info/
dist/
build/

# Config directory (may contain internal values)
config/

# Reports output
*.html
*.png
*.trace.*
/debug_and_traces/*
/Codex_++/docs/codex_traces

# Superpowers brainstorm sessions
.superpowers/

# Test artifacts
.pytest_cache/
.coverage

# Keep these
!requirements.txt
!ast_deps.csv
```

- [ ] **Step 2: Update pyproject.toml entry point and add deps**

Replace `pyproject.toml` with:

```toml
[project]
name = "data_guide"
version = "0.1.0"
description = "General-purpose EDA tool with pluggable connectors and multiple output formats"
authors = [{ name = "Zach" }]
requires-python = ">=3.11"
dependencies = [
  "pandas",
  "numpy",
  "scipy",
  "matplotlib",
  "seaborn",
  "missingno",
  "statsmodels",
  "scikit-learn",
  "typer",
  "pyyaml",
  "tabulate>=0.9.0",
  "markdown",
  "beautifulsoup4",
  "openpyxl",
  "sqlalchemy",
]

[project.optional-dependencies]
snowflake = ["snowflake-connector-python"]
phone = ["phonenumbers"]
geo = ["geopandas", "esda"]
pdf = ["pdfplumber"]
dev = ["pytest", "pytest-cov", "pre-commit", "ruff"]

[project.scripts]
guide = "cli:app"

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.ruff]
line-length = 88
target-version = "py311"
```

- [ ] **Step 3: Commit**

```bash
git add .gitignore pyproject.toml
git commit -m "chore: update gitignore and pyproject for redesign"
```

---

## Task 2: Create core data models

**Files:**
- Create: `src/core/__init__.py`
- Create: `src/core/models.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/__init__.py` (empty).

Create `tests/test_models.py`:

```python
import pandas as pd
import pytest
from core.models import GuideDataFrame, Narrative, ProfilingResult, SchemaContract


def test_schema_contract_defaults():
    sc = SchemaContract()
    assert sc.metric_col == "metric"
    assert sc.value_col == "value"
    assert sc.type_col is None
    assert sc.mode == "unknown"
    assert sc.key_cols == []
    assert sc.context_cols == []


def test_schema_contract_long_mode():
    sc = SchemaContract(
        key_cols=["patient_id"],
        context_cols=["location"],
        metric_col="metric",
        value_col="value",
        type_col="data_type",
        mode="long",
    )
    assert sc.mode == "long"
    assert sc.type_col == "data_type"


def test_guide_dataframe_wraps_df():
    df = pd.DataFrame({"metric": ["balance"], "value": [100.0]})
    sc = SchemaContract(mode="long", metric_col="metric", value_col="value")
    gdf = GuideDataFrame(df=df, schema=sc, source_type="csv", origin="test.csv")
    assert len(gdf.df) == 1
    assert gdf.source_type == "csv"
    assert gdf.schema.mode == "long"


def test_profiling_result_annotations_none_by_default():
    gdf = GuideDataFrame(
        df=pd.DataFrame(),
        schema=SchemaContract(),
        source_type="csv",
        origin="test.csv",
    )
    result = ProfilingResult(source=gdf, dataset_stats={}, column_stats={})
    assert result.annotations is None


def test_narrative_fields():
    n = Narrative(element_id="col_age", text="Age is right-skewed.", framework="plain")
    assert n.element_id == "col_age"
    assert n.framework == "plain"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/Users/zrhodes/Repositories/Data-Guide
python -m pytest tests/test_models.py -v
```

Expected: `ModuleNotFoundError: No module named 'core'`

- [ ] **Step 3: Create src/core/__init__.py**

Create `src/core/__init__.py` (empty).

- [ ] **Step 4: Create src/core/models.py**

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd


@dataclass
class SchemaContract:
    key_cols: list[str] = field(default_factory=list)
    context_cols: list[str] = field(default_factory=list)
    metric_col: str = "metric"
    value_col: str = "value"
    type_col: str | None = None
    mode: Literal["long", "wide", "unknown"] = "unknown"


@dataclass
class GuideDataFrame:
    df: pd.DataFrame
    schema: SchemaContract
    source_type: str
    origin: str


@dataclass
class Narrative:
    element_id: str
    text: str
    framework: str


@dataclass
class ProfilingResult:
    source: GuideDataFrame
    dataset_stats: dict[str, Any]
    column_stats: dict[str, Any]
    bivariate_stats: dict[str, Any] = field(default_factory=dict)
    annotations: dict[str, Narrative] | None = None
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_models.py -v
```

Expected: 5 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/core/ tests/__init__.py tests/test_models.py
git commit -m "feat: add core data models (SchemaContract, GuideDataFrame, ProfilingResult)"
```

---

## Task 3: Credentials loader

**Files:**
- Create: `src/connectors/__init__.py`
- Create: `src/connectors/base.py`
- Create: `src/connectors/credentials.py`
- Create: `tests/test_credentials.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_credentials.py`:

```python
import json
import os
import pytest
from pathlib import Path
from connectors.credentials import CredentialsValidationError, load_credentials


def test_load_from_file(tmp_path):
    creds_file = tmp_path / "sf.credentials.json"
    creds_file.write_text(json.dumps({
        "type": "snowflake",
        "account": "myaccount",
        "user": "myuser",
        "password": "secret",
        "warehouse": "WH",
        "database": "DB",
        "schema": "PUBLIC",
    }))
    result = load_credentials("snowflake", credentials_path=str(creds_file))
    assert result["account"] == "myaccount"
    assert result["type"] == "snowflake"


def test_load_from_env_vars(monkeypatch):
    monkeypatch.setenv("SF_ACCOUNT", "envaccount")
    monkeypatch.setenv("SF_USER", "envuser")
    monkeypatch.setenv("SF_PASSWORD", "envpass")
    monkeypatch.setenv("SF_WAREHOUSE", "WH")
    monkeypatch.setenv("SF_DATABASE", "DB")
    monkeypatch.setenv("SF_SCHEMA", "PUBLIC")
    result = load_credentials("snowflake")
    assert result["account"] == "envaccount"


def test_load_from_guide_credentials_file_env(tmp_path, monkeypatch):
    creds_file = tmp_path / "sf.credentials.json"
    creds_file.write_text(json.dumps({
        "type": "snowflake",
        "account": "fileenvaccount",
        "user": "u",
        "password": "p",
        "warehouse": "W",
        "database": "D",
        "schema": "S",
    }))
    monkeypatch.setenv("GUIDE_CREDENTIALS_FILE", str(creds_file))
    result = load_credentials("snowflake")
    assert result["account"] == "fileenvaccount"


def test_wrong_type_raises(tmp_path):
    creds_file = tmp_path / "bad.credentials.json"
    creds_file.write_text(json.dumps({"type": "csv"}))
    with pytest.raises(CredentialsValidationError, match="type mismatch"):
        load_credentials("snowflake", credentials_path=str(creds_file))


def test_missing_required_field_raises(tmp_path):
    creds_file = tmp_path / "incomplete.credentials.json"
    creds_file.write_text(json.dumps({
        "type": "snowflake",
        "account": "a",
        # missing user, password, warehouse, database, schema
    }))
    with pytest.raises(CredentialsValidationError, match="missing required field"):
        load_credentials("snowflake", credentials_path=str(creds_file))


def test_no_credentials_raises():
    with pytest.raises(CredentialsValidationError, match="No credentials"):
        load_credentials("snowflake")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_credentials.py -v
```

Expected: `ModuleNotFoundError: No module named 'connectors'`

- [ ] **Step 3: Create src/connectors/__init__.py**

Create `src/connectors/__init__.py` (empty).

- [ ] **Step 4: Create src/connectors/base.py**

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import GuideDataFrame


class BaseConnector(ABC):
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def load(self) -> GuideDataFrame: ...
```

- [ ] **Step 5: Create src/connectors/credentials.py**

```python
from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

_SNOWFLAKE_REQUIRED = {"account", "user", "password", "warehouse", "database", "schema"}

_REQUIRED_BY_TYPE: dict[str, set[str]] = {
    "snowflake": _SNOWFLAKE_REQUIRED,
}


class CredentialsValidationError(Exception):
    pass


def _load_file(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise CredentialsValidationError(f"Credentials file not found: {path}")
    with p.open() as f:
        if p.suffix in {".yaml", ".yml"}:
            return yaml.safe_load(f)
        return json.load(f)


def _validate(creds: dict, connector_type: str) -> dict:
    if creds.get("type") and creds["type"] != connector_type:
        raise CredentialsValidationError(
            f"Credentials type mismatch: file says '{creds['type']}', "
            f"connector expects '{connector_type}'"
        )
    required = _REQUIRED_BY_TYPE.get(connector_type, set())
    for field in required:
        if not creds.get(field):
            raise CredentialsValidationError(
                f"Credentials missing required field: '{field}' for connector '{connector_type}'"
            )
    return creds


def load_credentials(
    connector_type: str,
    credentials_path: str | None = None,
) -> dict:
    """Resolve credentials using priority order:
    1. credentials_path argument (from --credentials CLI flag)
    2. GUIDE_CREDENTIALS_FILE env var (path to file)
    3. Individual connector env vars (SF_ACCOUNT etc.)
    4. Raise CredentialsValidationError
    """
    if credentials_path:
        return _validate(_load_file(credentials_path), connector_type)

    env_file = os.environ.get("GUIDE_CREDENTIALS_FILE")
    if env_file:
        return _validate(_load_file(env_file), connector_type)

    if connector_type == "snowflake":
        keys = ["SF_ACCOUNT", "SF_USER", "SF_PASSWORD", "SF_WAREHOUSE", "SF_DATABASE", "SF_SCHEMA"]
        env_vals = {k: os.environ.get(k) for k in keys}
        if all(env_vals.values()):
            return {
                "type": "snowflake",
                "account": env_vals["SF_ACCOUNT"],
                "user": env_vals["SF_USER"],
                "password": env_vals["SF_PASSWORD"],
                "warehouse": env_vals["SF_WAREHOUSE"],
                "database": env_vals["SF_DATABASE"],
                "schema": env_vals["SF_SCHEMA"],
            }

    raise CredentialsValidationError(
        f"No credentials found for connector '{connector_type}'. "
        "Provide --credentials <file>, set GUIDE_CREDENTIALS_FILE, "
        "or set connector-specific env vars."
    )
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
python -m pytest tests/test_credentials.py -v
```

Expected: 6 tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/connectors/ tests/test_credentials.py
git commit -m "feat: add connectors base and credentials loader"
```

---

## Task 4: Flat-file connectors (CSV, Excel, JSON, SQLite)

**Files:**
- Create: `src/connectors/csv_connector.py`
- Create: `src/connectors/excel_connector.py`
- Create: `src/connectors/json_connector.py`
- Create: `src/connectors/sqlite_connector.py`
- Create: `tests/fixtures/sample.csv`
- Create: `tests/fixtures/sample.xlsx` (generated in test setup)
- Create: `tests/fixtures/sample.json`
- Create: `tests/fixtures/sample.db` (generated in test setup)
- Create: `tests/test_connectors.py`

- [ ] **Step 1: Create test fixtures**

Create `tests/fixtures/sample.csv`:

```csv
patient_id,location,metric,value,data_type
P001,North,balance_due,150.00,currency
P001,North,visit_count,3,numeric
P002,South,balance_due,0.00,currency
P002,South,visit_count,1,numeric
```

Create `tests/fixtures/sample.json`:

```json
[
  {"patient_id": "P001", "location": "North", "metric": "balance_due", "value": 150.0, "data_type": "currency"},
  {"patient_id": "P001", "location": "North", "metric": "visit_count", "value": 3, "data_type": "numeric"},
  {"patient_id": "P002", "location": "South", "metric": "balance_due", "value": 0.0, "data_type": "currency"},
  {"patient_id": "P002", "location": "South", "metric": "visit_count", "value": 1, "data_type": "numeric"}
]
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_connectors.py`:

```python
import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from connectors.csv_connector import CSVConnector
from connectors.excel_connector import ExcelConnector
from connectors.json_connector import JSONConnector
from connectors.sqlite_connector import SQLiteConnector
from core.models import SchemaContract

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_xlsx(tmp_path):
    df = pd.DataFrame({
        "patient_id": ["P001", "P002"],
        "metric": ["balance_due", "visit_count"],
        "value": [150.0, 3],
        "data_type": ["currency", "numeric"],
    })
    path = tmp_path / "sample.xlsx"
    df.to_excel(path, index=False)
    return path


@pytest.fixture
def sample_db(tmp_path):
    path = tmp_path / "sample.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE metrics (patient_id TEXT, metric TEXT, value REAL, data_type TEXT)"
    )
    conn.execute("INSERT INTO metrics VALUES ('P001', 'balance_due', 150.0, 'currency')")
    conn.execute("INSERT INTO metrics VALUES ('P002', 'visit_count', 3, 'numeric')")
    conn.commit()
    conn.close()
    return path


def test_csv_connector_loads(tmp_path):
    sc = SchemaContract(metric_col="metric", value_col="value", type_col="data_type", mode="long")
    connector = CSVConnector(path=str(FIXTURES / "sample.csv"), schema=sc)
    connector.connect()
    gdf = connector.load()
    assert len(gdf.df) == 4
    assert gdf.source_type == "csv"
    assert gdf.schema.mode == "long"


def test_excel_connector_loads(sample_xlsx):
    sc = SchemaContract(metric_col="metric", value_col="value", mode="long")
    connector = ExcelConnector(path=str(sample_xlsx), schema=sc)
    connector.connect()
    gdf = connector.load()
    assert len(gdf.df) == 2
    assert gdf.source_type == "excel"


def test_json_connector_loads():
    sc = SchemaContract(metric_col="metric", value_col="value", mode="long")
    connector = JSONConnector(path=str(FIXTURES / "sample.json"), schema=sc)
    connector.connect()
    gdf = connector.load()
    assert len(gdf.df) == 4
    assert gdf.source_type == "json"


def test_sqlite_connector_loads(sample_db):
    sc = SchemaContract(metric_col="metric", value_col="value", mode="wide")
    connector = SQLiteConnector(
        path=str(sample_db),
        query="SELECT * FROM metrics",
        schema=sc,
    )
    connector.connect()
    gdf = connector.load()
    assert len(gdf.df) == 2
    assert gdf.source_type == "sqlite"


def test_csv_connector_missing_file_raises():
    sc = SchemaContract()
    connector = CSVConnector(path="/nonexistent/file.csv", schema=sc)
    with pytest.raises(FileNotFoundError):
        connector.connect()
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
python -m pytest tests/test_connectors.py -v
```

Expected: `ModuleNotFoundError: No module named 'connectors.csv_connector'`

- [ ] **Step 4: Create src/connectors/csv_connector.py**

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd

from connectors.base import BaseConnector
from core.models import GuideDataFrame, SchemaContract


class CSVConnector(BaseConnector):
    def __init__(self, path: str, schema: SchemaContract) -> None:
        self._path = Path(path)
        self._schema = schema
        self._df: pd.DataFrame | None = None

    def connect(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(f"CSV file not found: {self._path}")

    def load(self) -> GuideDataFrame:
        self._df = pd.read_csv(self._path)
        return GuideDataFrame(
            df=self._df,
            schema=self._schema,
            source_type="csv",
            origin=str(self._path),
        )
```

- [ ] **Step 5: Create src/connectors/excel_connector.py**

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd

from connectors.base import BaseConnector
from core.models import GuideDataFrame, SchemaContract


class ExcelConnector(BaseConnector):
    def __init__(self, path: str, schema: SchemaContract, sheet: str | int = 0) -> None:
        self._path = Path(path)
        self._schema = schema
        self._sheet = sheet

    def connect(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(f"Excel file not found: {self._path}")

    def load(self) -> GuideDataFrame:
        df = pd.read_excel(self._path, sheet_name=self._sheet)
        return GuideDataFrame(
            df=df,
            schema=self._schema,
            source_type="excel",
            origin=str(self._path),
        )
```

- [ ] **Step 6: Create src/connectors/json_connector.py**

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd

from connectors.base import BaseConnector
from core.models import GuideDataFrame, SchemaContract


class JSONConnector(BaseConnector):
    def __init__(self, path: str, schema: SchemaContract) -> None:
        self._path = Path(path)
        self._schema = schema

    def connect(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(f"JSON file not found: {self._path}")

    def load(self) -> GuideDataFrame:
        df = pd.read_json(self._path)
        return GuideDataFrame(
            df=df,
            schema=self._schema,
            source_type="json",
            origin=str(self._path),
        )
```

- [ ] **Step 7: Create src/connectors/sqlite_connector.py**

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd

from connectors.base import BaseConnector
from core.models import GuideDataFrame, SchemaContract


class SQLiteConnector(BaseConnector):
    def __init__(self, path: str, query: str, schema: SchemaContract) -> None:
        self._path = Path(path)
        self._query = query
        self._schema = schema

    def connect(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(f"SQLite file not found: {self._path}")

    def load(self) -> GuideDataFrame:
        import sqlite3
        conn = sqlite3.connect(self._path)
        df = pd.read_sql_query(self._query, conn)
        conn.close()
        return GuideDataFrame(
            df=df,
            schema=self._schema,
            source_type="sqlite",
            origin=str(self._path),
        )
```

- [ ] **Step 8: Run tests to verify they pass**

```bash
python -m pytest tests/test_connectors.py -v
```

Expected: 5 tests PASS

- [ ] **Step 9: Commit**

```bash
git add src/connectors/ tests/test_connectors.py tests/fixtures/
git commit -m "feat: add CSV, Excel, JSON, SQLite connectors"
```

---

## Task 5: SQL and Snowflake connectors

**Files:**
- Create: `src/connectors/sql_connector.py`
- Create: `src/connectors/snowflake_connector.py`

These connectors require optional dependencies and are tested with lightweight mocking. No new fixture files needed.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_connectors.py`:

```python
from unittest.mock import MagicMock, patch

from connectors.sql_connector import SQLConnector
from connectors.snowflake_connector import SnowflakeConnector


def test_sql_connector_loads():
    sc = SchemaContract(metric_col="metric", value_col="value", mode="wide")
    mock_df = pd.DataFrame({"metric": ["balance_due"], "value": [100.0]})

    with patch("connectors.sql_connector.create_engine") as mock_engine_fn:
        mock_engine = MagicMock()
        mock_engine_fn.return_value = mock_engine
        with patch("connectors.sql_connector.pd.read_sql", return_value=mock_df):
            connector = SQLConnector(
                connection_string="sqlite:///:memory:",
                query="SELECT * FROM metrics",
                schema=sc,
            )
            connector.connect()
            gdf = connector.load()
    assert len(gdf.df) == 1
    assert gdf.source_type == "sql"


def test_snowflake_connector_loads():
    sc = SchemaContract(metric_col="metric", value_col="value", mode="long")
    mock_df = pd.DataFrame({"metric": ["balance_due"], "value": [100.0]})

    with patch("connectors.snowflake_connector.snowflake") as mock_sf:
        mock_conn = MagicMock()
        mock_sf.connector.connect.return_value = mock_conn
        with patch("connectors.snowflake_connector.pd.read_sql", return_value=mock_df):
            connector = SnowflakeConnector(
                credentials={
                    "account": "a", "user": "u", "password": "p",
                    "warehouse": "W", "database": "D", "schema": "S",
                },
                query="SELECT * FROM metrics",
                schema=sc,
            )
            connector.connect()
            gdf = connector.load()
    assert len(gdf.df) == 1
    assert gdf.source_type == "snowflake"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_connectors.py::test_sql_connector_loads tests/test_connectors.py::test_snowflake_connector_loads -v
```

Expected: `ModuleNotFoundError: No module named 'connectors.sql_connector'`

- [ ] **Step 3: Create src/connectors/sql_connector.py**

```python
from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine

from connectors.base import BaseConnector
from core.models import GuideDataFrame, SchemaContract


class SQLConnector(BaseConnector):
    def __init__(self, connection_string: str, query: str, schema: SchemaContract) -> None:
        self._connection_string = connection_string
        self._query = query
        self._schema = schema
        self._engine = None

    def connect(self) -> None:
        self._engine = create_engine(self._connection_string)

    def load(self) -> GuideDataFrame:
        df = pd.read_sql(self._query, self._engine)
        return GuideDataFrame(
            df=df,
            schema=self._schema,
            source_type="sql",
            origin=self._connection_string,
        )
```

- [ ] **Step 4: Create src/connectors/snowflake_connector.py**

```python
from __future__ import annotations

import pandas as pd

from connectors.base import BaseConnector
from core.models import GuideDataFrame, SchemaContract

try:
    import snowflake.connector as snowflake
except ImportError:
    snowflake = None


class SnowflakeConnector(BaseConnector):
    def __init__(self, credentials: dict, query: str, schema: SchemaContract) -> None:
        if snowflake is None:
            raise ImportError(
                "snowflake-connector-python is required. "
                "Install with: pip install 'data_guide[snowflake]'"
            )
        self._credentials = credentials
        self._query = query
        self._schema = schema
        self._conn = None

    def connect(self) -> None:
        self._conn = snowflake.connector.connect(
            account=self._credentials["account"],
            user=self._credentials["user"],
            password=self._credentials["password"],
            warehouse=self._credentials["warehouse"],
            database=self._credentials["database"],
            schema=self._credentials["schema"],
        )

    def load(self) -> GuideDataFrame:
        df = pd.read_sql(self._query, self._conn)
        return GuideDataFrame(
            df=df,
            schema=self._schema,
            source_type="snowflake",
            origin=f"snowflake://{self._credentials['account']}/{self._credentials['database']}",
        )
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_connectors.py -v
```

Expected: 7 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/connectors/sql_connector.py src/connectors/snowflake_connector.py tests/test_connectors.py
git commit -m "feat: add SQL and Snowflake connectors"
```

---

## Task 6: Migrate profilers

**Files:**
- Create: `src/profilers/__init__.py`
- Create: `src/profilers/bivariate.py` (migrated from `src/data_pipeline/bivariate_profiler.py`)
- Create: `src/profilers/univariate.py`

- [ ] **Step 1: Create src/profilers/__init__.py**

Create `src/profilers/__init__.py` (empty).

- [ ] **Step 2: Migrate bivariate profiler**

Copy `src/data_pipeline/bivariate_profiler.py` to `src/profilers/bivariate.py`. Then update its import at the top:

Find:
```python
from data_profiler import TypeResolver, slugify
```

Replace with:
```python
from data_profiler import TypeResolver, slugify
```

(No change needed — `data_profiler` stays at `src/data_profiler.py` and is on the path. Just verify this import resolves.)

- [ ] **Step 3: Create src/profilers/univariate.py**

This wraps the existing `DataProfiler` to accept a `GuideDataFrame` and return a `ProfilingResult`:

```python
from __future__ import annotations

from data_profiler import DataProfiler
from core.models import GuideDataFrame, ProfilingResult


def profile(gdf: GuideDataFrame, analyses: list[str] | None = None) -> ProfilingResult:
    """Run univariate profiling on a GuideDataFrame, return a ProfilingResult."""
    if analyses is None:
        analyses = ["dataset", "columns"]

    custom_types: dict[str, str] = {}
    if gdf.schema.type_col and gdf.schema.type_col in gdf.df.columns:
        type_series = gdf.df[gdf.schema.type_col].dropna()
        if gdf.schema.metric_col in gdf.df.columns:
            for _, row in gdf.df[[gdf.schema.metric_col, gdf.schema.type_col]].dropna().iterrows():
                custom_types[row[gdf.schema.metric_col]] = row[gdf.schema.type_col]

    profiler = DataProfiler(gdf.df, custom_types=custom_types)

    dataset_stats: dict = {}
    column_stats: dict = {}

    if "dataset" in analyses:
        profiler.profile_dataset()
        dataset_stats = profiler.dataset_summary if hasattr(profiler, "dataset_summary") else {}

    if "columns" in analyses:
        profiler.profile_columns()
        column_stats = profiler.column_summaries if hasattr(profiler, "column_summaries") else {}

    return ProfilingResult(
        source=gdf,
        dataset_stats=dataset_stats,
        column_stats=column_stats,
    )
```

- [ ] **Step 4: Verify imports resolve**

```bash
cd C:/Users/zrhodes/Repositories/Data-Guide
python -c "from profilers.univariate import profile; print('OK')"
python -c "from profilers.bivariate import BivariateProfiler; print('OK')"
```

Expected: `OK` for both

- [ ] **Step 5: Commit**

```bash
git add src/profilers/
git commit -m "feat: add profilers package, migrate bivariate profiler, wrap univariate"
```

---

## Task 7: Static report renderer

**Files:**
- Create: `src/outputs/__init__.py`
- Create: `src/outputs/html_utils.py`
- Create: `src/outputs/static_report.py`
- Create: `tests/test_static_report.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_static_report.py`:

```python
import pandas as pd
import pytest
from pathlib import Path

from core.models import GuideDataFrame, ProfilingResult, SchemaContract
from outputs.static_report import StaticReportRenderer


@pytest.fixture
def simple_gdf():
    df = pd.DataFrame({
        "metric": ["balance_due", "visit_count", "balance_due", "visit_count"],
        "value": [150.0, 3, 0.0, 1],
        "data_type": ["currency", "numeric", "currency", "numeric"],
    })
    sc = SchemaContract(metric_col="metric", value_col="value", type_col="data_type", mode="long")
    return GuideDataFrame(df=df, schema=sc, source_type="csv", origin="test.csv")


@pytest.fixture
def simple_result(simple_gdf):
    return ProfilingResult(
        source=simple_gdf,
        dataset_stats={"row_count": 4, "col_count": 3, "missing_pct": 0.0},
        column_stats={
            "value": {"mean": 38.5, "min": 0.0, "max": 150.0, "null_count": 0}
        },
    )


def test_renderer_produces_html(simple_result, tmp_path):
    out_path = tmp_path / "report.html"
    renderer = StaticReportRenderer()
    renderer.render(simple_result, output_path=str(out_path))
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "<html" in content
    assert "Data Guide" in content


def test_html_is_self_contained(simple_result, tmp_path):
    out_path = tmp_path / "report.html"
    renderer = StaticReportRenderer()
    renderer.render(simple_result, output_path=str(out_path))
    content = out_path.read_text(encoding="utf-8")
    assert "<img src=" not in content or "base64" in content


def test_html_contains_dataset_stats(simple_result, tmp_path):
    out_path = tmp_path / "report.html"
    renderer = StaticReportRenderer()
    renderer.render(simple_result, output_path=str(out_path))
    content = out_path.read_text(encoding="utf-8")
    assert "row_count" in content or "4" in content


def test_renderer_creates_parent_dirs(simple_result, tmp_path):
    out_path = tmp_path / "nested" / "deep" / "report.html"
    renderer = StaticReportRenderer()
    renderer.render(simple_result, output_path=str(out_path))
    assert out_path.exists()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_static_report.py -v
```

Expected: `ModuleNotFoundError: No module named 'outputs'`

- [ ] **Step 3: Create src/outputs/__init__.py**

Create `src/outputs/__init__.py` (empty).

- [ ] **Step 4: Create src/outputs/html_utils.py**

Migrated and cleaned up from `inline_html.py`:

```python
from __future__ import annotations

import base64
import io
import mimetypes

import matplotlib.pyplot as plt


def fig_to_base64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f'<img src="data:image/png;base64,{encoded}" style="max-width:100%;">'


def wrap_html(body: str, title: str = "Data Guide Report") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{ font-family: sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
    h1 {{ border-bottom: 2px solid #444; padding-bottom: .5rem; }}
    h2 {{ margin-top: 2rem; color: #333; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #ccc; padding: .4rem .7rem; text-align: left; }}
    th {{ background: #f4f4f4; }}
    .section {{ margin-bottom: 2rem; }}
    img {{ display: block; margin: 1rem 0; }}
  </style>
</head>
<body>
{body}
</body>
</html>"""
```

- [ ] **Step 5: Create src/outputs/static_report.py**

```python
from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.models import ProfilingResult
from outputs.html_utils import wrap_html


class StaticReportRenderer:
    def render(self, result: ProfilingResult, output_path: str) -> None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        sections: list[str] = []
        sections.append(self._header(result))
        sections.append(self._dataset_overview(result))
        sections.append(self._column_stats(result))

        html = wrap_html("\n".join(sections), title="Data Guide Report")
        out.write_text(html, encoding="utf-8")

    def _header(self, result: ProfilingResult) -> str:
        origin = result.source.origin
        source_type = result.source.source_type
        mode = result.source.schema.mode
        return (
            f"<h1>Data Guide Report</h1>"
            f"<p><strong>Source:</strong> {origin} "
            f"(<code>{source_type}</code>, mode: <code>{mode}</code>)</p>"
        )

    def _dataset_overview(self, result: ProfilingResult) -> str:
        stats = result.dataset_stats
        if not stats:
            df = result.source.df
            stats = {
                "row_count": len(df),
                "col_count": len(df.columns),
                "missing_pct": round(df.isnull().mean().mean() * 100, 2),
            }
        rows = "".join(
            f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in stats.items()
        )
        return (
            "<div class='section'>"
            "<h2>Dataset Overview</h2>"
            f"<table><tr><th>Metric</th><th>Value</th></tr>{rows}</table>"
            "</div>"
        )

    def _column_stats(self, result: ProfilingResult) -> str:
        stats = result.column_stats
        if not stats:
            stats = {
                col: {"dtype": str(result.source.df[col].dtype),
                      "null_count": int(result.source.df[col].isnull().sum()),
                      "unique": int(result.source.df[col].nunique())}
                for col in result.source.df.columns
            }
        sections = ["<div class='section'><h2>Column Profiles</h2>"]
        for col, col_stats in stats.items():
            rows = "".join(
                f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in col_stats.items()
            )
            sections.append(
                f"<h3>{col}</h3>"
                f"<table><tr><th>Stat</th><th>Value</th></tr>{rows}</table>"
            )
        sections.append("</div>")
        return "\n".join(sections)
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
python -m pytest tests/test_static_report.py -v
```

Expected: 4 tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/outputs/ tests/test_static_report.py
git commit -m "feat: add static HTML report renderer"
```

---

## Task 8: New CLI entry point

**Files:**
- Create: `src/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_cli.py`:

```python
from pathlib import Path
from typer.testing import CliRunner
from cli import app

runner = CliRunner()
FIXTURES = Path(__file__).parent / "fixtures"


def test_profile_command_produces_report(tmp_path):
    result = runner.invoke(app, [
        "profile", str(FIXTURES / "sample.csv"),
        "--output", str(tmp_path / "report.html"),
    ])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "report.html").exists()


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_validate_command_long_format():
    result = runner.invoke(app, [
        "validate", str(FIXTURES / "sample.csv"),
        "--metric-col", "metric",
        "--value-col", "value",
    ])
    assert result.exit_code == 0
    assert "valid" in result.output.lower()


def test_validate_command_missing_col():
    result = runner.invoke(app, [
        "validate", str(FIXTURES / "sample.csv"),
        "--metric-col", "nonexistent",
        "--value-col", "value",
    ])
    assert result.exit_code != 0 or "not found" in result.output.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_cli.py -v
```

Expected: `ModuleNotFoundError: No module named 'cli'`

- [ ] **Step 3: Create src/cli.py**

```python
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from connectors.csv_connector import CSVConnector
from core.models import SchemaContract
from outputs.static_report import StaticReportRenderer
from profilers.univariate import profile

app = typer.Typer(help="Data Guide — general-purpose EDA tool.")

_VERSION = "0.1.0"


@app.command()
def version() -> None:
    """Show the current version."""
    typer.echo(f"data-guide {_VERSION}")


@app.command()
def validate(
    file: Path = typer.Argument(..., help="Path to data file to validate."),
    metric_col: str = typer.Option("metric", help="Name of the metric column."),
    value_col: str = typer.Option("value", help="Name of the value column."),
    type_col: Optional[str] = typer.Option(None, help="Name of the data_type column (optional)."),
) -> None:
    """Validate that a file matches the expected schema contract."""
    import pandas as pd
    df = pd.read_csv(file)
    errors = []
    if metric_col not in df.columns:
        errors.append(f"metric column '{metric_col}' not found in {list(df.columns)}")
    if value_col not in df.columns:
        errors.append(f"value column '{value_col}' not found in {list(df.columns)}")
    if type_col and type_col not in df.columns:
        errors.append(f"type column '{type_col}' not found in {list(df.columns)}")

    if errors:
        for err in errors:
            typer.echo(f"ERROR: {err}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Valid: schema contract satisfied for '{file.name}'.")


@app.command()
def profile_cmd(
    file: Path = typer.Argument(..., help="Path to data file to profile."),
    output: Path = typer.Option(Path("reports/report.html"), help="Output HTML report path."),
    metric_col: str = typer.Option("metric", help="Name of the metric column."),
    value_col: str = typer.Option("value", help="Name of the value column."),
    type_col: Optional[str] = typer.Option(None, help="Name of the data_type column (optional)."),
    mode: str = typer.Option("unknown", help="Schema mode: long, wide, or unknown."),
) -> None:
    """Profile a data file and generate a static HTML report."""
    sc = SchemaContract(
        metric_col=metric_col,
        value_col=value_col,
        type_col=type_col,
        mode=mode,  # type: ignore[arg-type]
    )
    connector = CSVConnector(path=str(file), schema=sc)
    connector.connect()
    gdf = connector.load()

    result = profile(gdf)

    renderer = StaticReportRenderer()
    renderer.render(result, output_path=str(output))
    typer.echo(f"Report written to {output}")


# Register `profile` as the CLI command name
app.command(name="profile")(profile_cmd.callback)  # type: ignore[attr-defined]


if __name__ == "__main__":
    app()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_cli.py -v
```

Expected: 4 tests PASS

- [ ] **Step 5: Update pyproject.toml entry point**

In `pyproject.toml`, the entry point is already set to `guide = "cli:app"` from Task 1. Verify:

```bash
grep "guide" C:/Users/zrhodes/Repositories/Data-Guide/pyproject.toml
```

Expected: `guide = "cli:app"`

- [ ] **Step 6: Commit**

```bash
git add src/cli.py tests/test_cli.py
git commit -m "feat: add new CLI entry point (guide profile, validate, version)"
```

---

## Task 9: Retire org-specific code

**Files to delete:**
- `src/data_pipeline/api_client.py`
- `src/data_pipeline/data_pull.py`
- `src/data_pipeline/config.py`
- `src/data_pipeline/main.py`
- `src/data_pipeline/pipeline.py`
- `src/data_pipeline/pipeline_transformed.py`
- `src/typer_cli.py`
- `src/profiler_cli.py`
- `src/pipeline.py`
- `src/main_pipeline.py`
- `src/run_profiler.py`
- `src/profiler.py`
- `codex_++/purpose_files/api_client.purpose.md`
- `codex_++/purpose_files/data_pull.purpose.md`
- `codex_++/purpose_files/main.purpose.md`
- `codex_++/purpose_files/notebooks_retention.purpose.md`

**Files to clean (remove org references, keep structure):**
- `codex_++/docs/NOTEBOOK_MODULARIZATION_PLAN.md`
- `codex_++/CLAUDE.md`

- [ ] **Step 1: Run full test suite to confirm green baseline**

```bash
python -m pytest tests/ -v
```

Expected: all tests PASS before any deletion

- [ ] **Step 2: Delete org-specific data_pipeline files**

```bash
cd C:/Users/zrhodes/Repositories/Data-Guide
git rm src/data_pipeline/api_client.py \
       src/data_pipeline/data_pull.py \
       src/data_pipeline/config.py \
       src/data_pipeline/main.py \
       src/data_pipeline/pipeline.py \
       src/data_pipeline/pipeline_transformed.py
```

- [ ] **Step 3: Delete retired CLI and pipeline scripts**

```bash
git rm src/typer_cli.py \
       src/profiler_cli.py \
       src/pipeline.py \
       src/main_pipeline.py \
       src/run_profiler.py \
       src/profiler.py
```

- [ ] **Step 4: Delete org-specific purpose files**

```bash
git rm "codex_++/purpose_files/api_client.purpose.md" \
       "codex_++/purpose_files/data_pull.purpose.md" \
       "codex_++/purpose_files/main.purpose.md" \
       "codex_++/purpose_files/notebooks_retention.purpose.md"
```

- [ ] **Step 5: Run test suite again to confirm still green**

```bash
python -m pytest tests/ -v
```

Expected: all tests still PASS (deleted files had no test coverage)

- [ ] **Step 6: Scrub org references from remaining docs**

In `codex_++/docs/NOTEBOOK_MODULARIZATION_PLAN.md`: remove any sentences containing "Juniper Dentistry", "Dentrix", or specific internal project names. Replace with generic language (e.g. "client dataset" or remove entirely).

In `codex_++/CLAUDE.md`: remove any lines referencing Snowflake internal table names, Dentrix endpoints, or org-specific pipeline details.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: retire org-specific code and scrub internal references"
```

---

## Task 10: Smoke test end-to-end

This task verifies the full pipeline works from CLI to HTML output using the test fixture.

- [ ] **Step 1: Install the package**

```bash
cd C:/Users/zrhodes/Repositories/Data-Guide
pip install -e ".[dev]"
```

- [ ] **Step 2: Run guide profile via CLI**

```bash
guide profile tests/fixtures/sample.csv \
  --output reports/smoke_test.html \
  --metric-col metric \
  --value-col value \
  --type-col data_type \
  --mode long
```

Expected: `Report written to reports/smoke_test.html`

- [ ] **Step 3: Verify the HTML report exists and is non-empty**

```bash
python -c "
from pathlib import Path
p = Path('reports/smoke_test.html')
content = p.read_text()
assert '<html' in content, 'Missing html tag'
assert len(content) > 500, 'Report seems too short'
print(f'OK — report is {len(content)} chars')
"
```

Expected: `OK — report is XXXX chars`

- [ ] **Step 4: Run full test suite**

```bash
python -m pytest tests/ -v --tb=short
```

Expected: all tests PASS

- [ ] **Step 5: Commit smoke test report to gitignore (reports/ already covered)**

Confirm `reports/` is covered by `.gitignore` (it generates `.html` which is ignored). No commit needed for the report itself.

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "chore: Phase 1 complete — EDA tool MVP with connectors, static report, and CLI"
```

---

## Summary

| Task | Deliverable | Commit |
|---|---|---|
| 1 | Updated .gitignore + pyproject.toml | `chore: update gitignore and pyproject for redesign` |
| 2 | `core/models.py` — SchemaContract, GuideDataFrame, ProfilingResult, Narrative | `feat: add core data models` |
| 3 | `connectors/base.py` + `credentials.py` | `feat: add connectors base and credentials loader` |
| 4 | CSV, Excel, JSON, SQLite connectors | `feat: add CSV, Excel, JSON, SQLite connectors` |
| 5 | SQL + Snowflake connectors | `feat: add SQL and Snowflake connectors` |
| 6 | `profilers/` package with bivariate migrated | `feat: add profilers package` |
| 7 | `outputs/static_report.py` — HTML renderer | `feat: add static HTML report renderer` |
| 8 | `src/cli.py` — new entry point | `feat: add new CLI entry point` |
| 9 | Org code retired, docs scrubbed | `chore: retire org-specific code` |
| 10 | End-to-end smoke test passing | `chore: Phase 1 complete` |
