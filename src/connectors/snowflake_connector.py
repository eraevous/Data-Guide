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
        self._conn = snowflake.connect(
            account=self._credentials["account"],
            user=self._credentials["user"],
            password=self._credentials["password"],
            warehouse=self._credentials["warehouse"],
            database=self._credentials["database"],
            schema=self._credentials["schema"],
        )

    def load(self) -> GuideDataFrame:
        try:
            df = pd.read_sql(self._query, self._conn)
        finally:
            if self._conn is not None:
                self._conn.close()
                self._conn = None
        return GuideDataFrame(
            df=df,
            schema=self._schema,
            source_type="snowflake",
            origin=f"snowflake://{self._credentials['account']}/{self._credentials['database']}",
        )
