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
