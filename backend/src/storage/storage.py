from __future__ import annotations

from types import TracebackType

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from embeddings.protocols import TextEmbeddingModelProtocol
from storage.configuration import StorageConfiguration
from storage.db.engine import create_storage_engine
from storage.db.migration_runner import run_storage_migrations
from storage.health import StorageHealthReport
from storage.health import check_storage_health
from storage.health import validate_storage_health
from storage.db.session import create_session_factory
from storage.db.unit_of_work import StorageUnitOfWork
from storage.stores.chat_store import ChatStore
from storage.stores.storage_metadata_store import StorageMetadataStore
from storage.stores.travel_destination_store import TravelDestinationStore


class Storage:
    """Entry point for PostgreSQL storage dependencies and lifecycle."""

    def __init__(
        self,
        config: StorageConfiguration,
        embedding_model: TextEmbeddingModelProtocol,
    ) -> None:
        if config is None:
            raise ValueError("Storage configuration is required")
        if embedding_model is None:
            raise ValueError("Embedding model dependency is required")

        self.config = config
        self.embedding_model = embedding_model

        self.engine: Engine = create_storage_engine(config.engine)

        embedding_dimension = embedding_model.get_dimentions()
        if embedding_dimension <= 0:
            raise ValueError("Embedding model dimension must be greater than zero")
        self.embedding_dimension = embedding_dimension

        if config.migrations.enabled:
            run_storage_migrations(
                self.engine,
                embedding_dimension=self.embedding_dimension,
                migration_lock_key=config.migrations.lock_key,
            )

        self.validate_health()

        self.session_factory: sessionmaker[Session] = create_session_factory(self.engine)
        self.unit_of_work = StorageUnitOfWork(session_factory=self.session_factory)

        self.travel_destinations = TravelDestinationStore(
            unit_of_work=self.unit_of_work,
            embedding_model=embedding_model,
        )
        self.storage_metadata = StorageMetadataStore(unit_of_work=self.unit_of_work)
        self.chat = ChatStore(unit_of_work=self.unit_of_work)

    def check_health(self) -> StorageHealthReport:
        """Return current storage health report for observability and readiness checks."""
        return check_storage_health(
            self.engine,
            expected_embedding_dimension=self.embedding_dimension,
            schema_name=self.config.schema_name,
        )

    def validate_health(self) -> None:
        """Raise when storage health checks fail for the configured embedding contract."""
        validate_storage_health(
            self.engine,
            expected_embedding_dimension=self.embedding_dimension,
            schema_name=self.config.schema_name,
        )

    def close(self) -> None:
        """Release database connections held by the storage engine."""
        self.engine.dispose()

    def __enter__(self) -> Storage:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
