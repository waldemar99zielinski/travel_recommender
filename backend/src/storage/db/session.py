from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a SQLModel session factory."""
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


@contextmanager
def read_session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """Yield a read-only session without committing transactions."""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def write_session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """Yield a write session with commit/rollback handling."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


session_scope = write_session_scope
