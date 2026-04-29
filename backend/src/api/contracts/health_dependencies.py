from __future__ import annotations

from typing import Protocol

from storage.health import StorageHealthReport


class EmbeddingHealthDependencyProtocol(Protocol):
    def check_health(self) -> bool:
        ...

    def get_dimentions(self) -> int:
        ...


class StorageHealthDependencyProtocol(Protocol):
    def check_health(self) -> StorageHealthReport:
        ...
