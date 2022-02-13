from dataclasses import dataclass
from typing import Protocol

from app.core.models.statistics import Statistics
from app.core.repositories import IStatisticsRepository


class IStatisticsInteractor(Protocol):
    def log_transaction_commission(self, commission: int) -> None:
        pass

    def get_statistics(self) -> Statistics:
        pass


@dataclass
class StatisticsInteractor(IStatisticsInteractor):
    statistics_repository: IStatisticsRepository

    def log_transaction_commission(self, commission: int) -> None:
        self.statistics_repository.record_transaction(commission)

    def get_statistics(self) -> Statistics:
        return self.statistics_repository.get_statistics()
