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
        try:
            df = pd.read_sql(self._query, self._engine)
        finally:
            if self._engine is not None:
                self._engine.dispose()
                self._engine = None
        return GuideDataFrame(
            df=df,
            schema=self._schema,
            source_type="sql",
            origin=self._connection_string,
        )
