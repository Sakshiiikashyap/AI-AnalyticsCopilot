from abc import ABC, abstractmethod
from typing import Any


class ForecastProvider(ABC):
    @abstractmethod
    def forecast(self, dates: list, values: list, periods: int) -> dict[str, Any]:
        raise NotImplementedError