import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from connectors.csv_connector import CSVConnector
from connectors.excel_connector import ExcelConnector
from connectors.json_connector import JSONConnector
from connectors.snowflake_connector import SnowflakeConnector
from connectors.sql_connector import SQLConnector
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


def test_csv_connector_loads():
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
        mock_sf.connect.return_value = mock_conn
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
