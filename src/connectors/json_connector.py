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
