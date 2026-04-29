from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic import Field


class ApiHealthCheckDto(BaseModel):
    healthy: bool = Field(...)
    status: Literal["ok", "error"] = Field(...)
    details: str = Field(...)


class EmbeddingsHealthCheckDto(BaseModel):
    healthy: bool = Field(...)
    status: Literal["ok", "error"] = Field(...)
    details: str = Field(...)
    dimensions: int | None = Field(...)


class StorageHealthCheckDto(BaseModel):
    healthy: bool = Field(...)
    status: Literal["ok", "error"] = Field(...)
    details: str = Field(...)
    database_reachable: bool = Field(...)
    postgresql_18_compatible: bool = Field(...)
    pgvector_enabled: bool = Field(...)
    pgvector_version_compatible: bool = Field(...)
    embedding_dimension_matches: bool = Field(...)
    vector_index_present: bool = Field(...)


class HealthChecksDto(BaseModel):
    api: ApiHealthCheckDto = Field(...)
    embeddings: EmbeddingsHealthCheckDto = Field(...)
    storage: StorageHealthCheckDto = Field(...)


class HealthResponseDto(BaseModel):
    status: Literal["ok", "degraded"] = Field(...)
    env: str = Field(...)
    log_level: str = Field(...)
    checks: HealthChecksDto = Field(...)
