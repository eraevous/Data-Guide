from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import GuideDataFrame


class BaseConnector(ABC):
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def load(self) -> GuideDataFrame: ...
