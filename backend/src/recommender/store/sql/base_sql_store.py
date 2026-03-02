from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TypeVar

from sqlmodel import SQLModel
from sqlmodel.sql.expression import SelectOfScalar

from recommender.models.data_flow.user_preferences import UserLogisticalPreferences
from recommender.models.data_flow.recommendation_output import Recommendation

TableModel = TypeVar("TableModel", bound=SQLModel)


class BaseSqlStore(ABC):
    """Abstract contract for SQLModel-backed stores supporting multiple tables."""

    @abstractmethod
    def load(self) -> None:
        """Initialize underlying SQL store resources and schema."""

    @abstractmethod
    def is_loaded(self) -> bool:
        """Return True when the store is ready for use."""

    @abstractmethod
    def size(self, table_model: type[TableModel]) -> int:
        """Return number of rows for a given SQLModel table."""

    @abstractmethod
    def query(self, statement: SelectOfScalar[TableModel]) -> list[TableModel]:
        """Execute a SQLModel select statement."""

    @abstractmethod
    def all(self, table_model: type[TableModel]) -> list[TableModel]:
        """Return all rows for a table."""

    @abstractmethod
    def rank_travel_destinations_by_logistical_preferences(
        self,
        recommendation: list[Recommendation],
        logistical_preferences: UserLogisticalPreferences,
    ) -> list[Recommendation]:
        """Return ranked destination IDs with final scores."""
