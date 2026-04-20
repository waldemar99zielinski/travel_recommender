from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from storage.configuration import StorageConfiguration
from storage.db.engine import create_storage_engine
from storage.db.migration_runner import run_storage_migrations
from storage.db.migration_runner import validate_storage_contract
from storage.db.session import create_session_factory
from storage.db.unit_of_work import StorageUnitOfWork
from storage.stores.recommendation_session_store import RecommendationSessionStore
from storage.stores.travel_destination_store import TravelDestinationStore


@dataclass(slots=True)
class StorageContainer:
    """Composable container for PostgreSQL storage dependencies."""

    engine: Engine
    session_factory: sessionmaker[Session]
    unit_of_work: StorageUnitOfWork
    travel_destinations: TravelDestinationStore
    recommendation_sessions: RecommendationSessionStore


def create_storage_container(config: StorageConfiguration | None = None) -> StorageContainer:
    """Build engine, session factory, and store facades."""
    resolved_config = config or StorageConfiguration()
    engine = create_storage_engine(resolved_config.engine)

    if resolved_config.migrations.enabled:
        run_storage_migrations(
            engine,
            embedding_dimension=resolved_config.vector.embedding_dimension,
            migration_lock_key=resolved_config.migrations.lock_key,
        )
    else:
        validate_storage_contract(
            engine,
            embedding_dimension=resolved_config.vector.embedding_dimension,
        )

    session_factory = create_session_factory(engine)
    unit_of_work = StorageUnitOfWork(session_factory=session_factory)

    return StorageContainer(
        engine=engine,
        session_factory=session_factory,
        unit_of_work=unit_of_work,
        travel_destinations=TravelDestinationStore(
            unit_of_work=unit_of_work,
            embedding_dimension=resolved_config.vector.embedding_dimension,
        ),
        recommendation_sessions=RecommendationSessionStore(unit_of_work=unit_of_work),
    )
