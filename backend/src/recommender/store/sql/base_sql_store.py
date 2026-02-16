from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TypeVar

from sqlmodel import SQLModel
from sqlmodel.sql.expression import SelectOfScalar

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