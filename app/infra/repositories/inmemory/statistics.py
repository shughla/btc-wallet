import json
from dataclasses import dataclass, field
from typing import Any

from app.core.models.statistics import Statistics
from app.core.repositories import IStatisticsRepository


@dataclass
class InMemoryStatisticsRepository(IStatisticsRepository):
    statistics: Statistics = field(default_factory=lambda: Statistics(0, 0))

    def record_transaction(self, commission: int) -> None:
        self.statistics.profit += commission
        self.statistics.total_transactions += 1

    def get_statistics(self) -> Statistics:
        return self.statistics


class FileStatisticsRepository(InMemoryStatisticsRepository):
    def __init__(self, file_path: str = "statistics.json"):
        self.file_path = file_path
        try:
            self.statistics = self._read_file()
        except FileNotFoundError:
            self.statistics = Statistics(0, 0)
            self._persist__()

    def _to_string(self) -> str:
        return json.dumps(self.statistics.__dict__)

    def _read_file(self) -> Any:
        with open(self.file_path, "r") as f:
            return json.loads(f.read(), object_hook=lambda d: Statistics(**d))

    def _persist__(self) -> None:
        with open(self.file_path, "w") as f:
            f.write(self._to_string())

    def record_transaction(self, commission: int) -> None:
        super().record_transaction(commission)
        self._persist__()
