from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from storage.db.session import read_session_scope
from storage.db.session import write_session_scope


@dataclass(slots=True)
class StorageUnitOfWork:
    """Provides explicit read and write transaction scopes."""

    session_factory: sessionmaker[Session]

    @contextmanager
    def read(self) -> Iterator[Session]:
        """Open a read-only session scope."""
        with read_session_scope(self.session_factory) as session:
            yield session

    @contextmanager
    def write(self) -> Iterator[Session]:
        """Open a transactional write session scope."""
        with write_session_scope(self.session_factory) as session:
            yield session
