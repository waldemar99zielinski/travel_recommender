from __future__ import annotations

from typing import Literal

from sqlalchemy import func
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel import delete
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from recommender.store.sql.base_sql_store import BaseSqlStore
from recommender.store.sql.base_sql_store import TableModel
from recommender.store.sql.travel_destination_csv_loader import TravelDestinationCsvLoader
from recommender.store.sql.travel_destination_table import TravelDestinationTable
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class SqlStore(BaseSqlStore):
    """SQLite implementation of a multi-table SQLModel store."""

    def __init__(self, db_url: str) -> None:
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        self._loaded = False
        self.travel_destination_loader = TravelDestinationCsvLoader()

    def load(self) -> None:
        SQLModel.metadata.create_all(self.engine)
        self._loaded = True

    def load_travel_destinations_data_from_csv(
        self,
        csv_file_path: str,
        mode: Literal["append", "replace"] = "append",
    ) -> None:
        """Loads travel destination rows from CSV, appending or replacing table contents."""
        self._ensure_loaded()

        rows = self.travel_destination_loader.load(csv_file_path)
        with Session(self.engine) as session:
            if mode == "replace":
                session.exec(delete(TravelDestinationTable))
            session.add_all(rows)
            session.commit()

        logger.info(
            "Loaded %s travel destinations from %s with mode=%s",
            len(rows),
            csv_file_path,
            mode,
        )

    def is_loaded(self) -> bool:
        return self._loaded

    def size(self, table_model: type[TableModel]) -> int:
        self._ensure_loaded()
        
        with Session(self.engine) as session:
            statement = select(func.count()).select_from(table_model)
            result = session.exec(statement).one()
            return int(result)

    def query(self, statement: SelectOfScalar[TableModel]) -> list[TableModel]:
        self._ensure_loaded()

        with Session(self.engine) as session:
            return list(session.exec(statement).all())

    def all(self, table_model: type[TableModel]) -> list[TableModel]:
        self._ensure_loaded()
        statement: SelectOfScalar[TableModel] = select(table_model)

        return self.query(statement)

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            raise RuntimeError("SQLite SQLModel store is not loaded. Call load() first.")
