from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import case
from sqlalchemy import literal
from sqlalchemy import Float
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func
from sqlmodel import Session
from sqlmodel import col
from sqlmodel import select

from storage.models.travel_destination import TravelDestinationRecord
from storage.stores.search_models import ScoredTravelDestination
from storage.stores.search_models import TravelSearchConstraints

VALID_MONTH_COLUMNS = {
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
}


class TravelDestinationRepository:
    """Repository for unified travel destination metadata and embeddings."""

    def __init__(
        self,
        session: Session,
        *,
        embedding_dimension: int,
    ) -> None:
        if embedding_dimension <= 0:
            raise ValueError("embedding_dimension must be greater than zero")

        self.session = session
        self.embedding_dimension = embedding_dimension

    def count(self) -> int:
        """Return number of stored travel destinations."""
        statement = select(func.count()).select_from(TravelDestinationRecord)
        result = self.session.exec(statement).one()
        return int(result)

    def list_all(self) -> list[TravelDestinationRecord]:
        """Return all travel destinations."""
        statement = select(TravelDestinationRecord)
        return list(self.session.exec(statement).all())

    def list_by_ids(self, destination_ids: Sequence[str]) -> list[TravelDestinationRecord]:
        """Return all travel destinations matching the provided IDs."""
        if not destination_ids:
            return []

        statement = select(TravelDestinationRecord).where(col(TravelDestinationRecord.id).in_(list(destination_ids)))
        return list(self.session.exec(statement).all())

    def upsert_many(self, rows: Sequence[TravelDestinationRecord]) -> None:
        """Insert or update many rows by primary key."""
        if not rows:
            return

        for row in rows:
            self._validate_embedding_dimension(row.embedding)

        payloads = [row.model_dump() for row in rows]
        statement = insert(TravelDestinationRecord).values(payloads)
        updatable_columns = {
            field_name: getattr(statement.excluded, field_name)
            for field_name in payloads[0]
            if field_name not in {"id", "created_at"}
        }

        upsert_statement = statement.on_conflict_do_update(
            index_elements=["id"],
            set_=updatable_columns,
        )
        self.session.exec(upsert_statement)

    def semantic_search(
        self,
        query_embedding: Sequence[float],
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]:
        """Return nearest travel destinations with semantic-only ranking."""
        self._validate_embedding_dimension(query_embedding)
        self._validate_limit(limit)

        distance_expression = col(TravelDestinationRecord.embedding).op("<->")(list(query_embedding)).cast(Float)
        semantic_score_expression = literal(1.0) / (literal(1.0) + distance_expression)

        statement = (
            select(TravelDestinationRecord)
            .add_columns(distance_expression.label("embedding_distance"))
            .add_columns(semantic_score_expression.label("semantic_score"))
            .order_by(distance_expression)
        )
        if limit is not None:
            statement = statement.limit(limit)

        rows = self.session.execute(statement).all()
        return [
            ScoredTravelDestination(
                destination=row[0],
                embedding_distance=float(row[1]),
                semantic_score=float(row[2]),
                logistics_score=1.0,
                ranking_score=float(row[2]),
            )
            for row in rows
        ]

    def hybrid_search(
        self,
        query_embedding: Sequence[float],
        *,
        constraints: TravelSearchConstraints,
        limit: int | None = None,
        semantic_weight: float = 0.85,
        logistics_weight: float = 0.15,
    ) -> list[ScoredTravelDestination]:
        """Return destinations ranked by semantic and logistics blending."""
        self._validate_embedding_dimension(query_embedding)
        self._validate_limit(limit)
        self._validate_weight(semantic_weight, "semantic_weight")
        self._validate_weight(logistics_weight, "logistics_weight")

        distance_expression = col(TravelDestinationRecord.embedding).op("<->")(list(query_embedding)).cast(Float)
        semantic_score_expression = literal(1.0) / (literal(1.0) + distance_expression)
        logistics_score_expression = self._build_logistics_score_expression(constraints).cast(Float)

        ranking_score_expression = (
            (literal(float(semantic_weight)) * semantic_score_expression)
            + (literal(float(logistics_weight)) * logistics_score_expression)
        ).cast(Float)

        statement = (
            select(TravelDestinationRecord)
            .add_columns(distance_expression.label("embedding_distance"))
            .add_columns(semantic_score_expression.label("semantic_score"))
            .add_columns(logistics_score_expression.label("logistics_score"))
            .add_columns(ranking_score_expression.label("ranking_score"))
            .order_by(ranking_score_expression.desc(), distance_expression)
        )
        if limit is not None:
            statement = statement.limit(limit)

        rows = self.session.execute(statement).all()
        return [
            ScoredTravelDestination(
                destination=row[0],
                embedding_distance=float(row[1]),
                semantic_score=float(row[2]),
                logistics_score=float(row[3]),
                ranking_score=float(row[4]),
            )
            for row in rows
        ]

    def _build_logistics_score_expression(self, constraints: TravelSearchConstraints) -> Any:
        score_expressions: list[Any] = []

        if constraints.max_cost_per_week is not None:
            max_cost = float(constraints.max_cost_per_week)
            denominator = max(max_cost, 1.0)
            cost_column = col(TravelDestinationRecord.cost_per_week)
            cost_score_expression = case(
                (cost_column <= literal(max_cost), literal(1.0)),
                else_=func.greatest(literal(0.0), literal(1.0) - ((cost_column - literal(max_cost)) / literal(denominator))),
            )
            score_expressions.append(cost_score_expression)

        if constraints.min_popularity is not None:
            min_popularity = max(float(constraints.min_popularity), 0.01)
            popularity_column = col(TravelDestinationRecord.popularity)
            popularity_score_expression = func.least(literal(1.0), popularity_column / literal(min_popularity))
            score_expressions.append(popularity_score_expression)

        month_score_expression = self._build_month_score_expression(constraints.months)
        if month_score_expression is not None:
            score_expressions.append(month_score_expression)

        if not score_expressions:
            return literal(1.0)

        score_sum_expression = literal(0.0)
        for expression in score_expressions:
            score_sum_expression = score_sum_expression + expression

        return score_sum_expression / literal(float(len(score_expressions)))

    def _build_month_score_expression(self, months: Sequence[str]) -> Any | None:
        normalized_months: list[str] = []
        for month in months:
            normalized = month.lower().strip()
            if normalized in VALID_MONTH_COLUMNS and normalized not in normalized_months:
                normalized_months.append(normalized)

        if not normalized_months:
            return None

        month_score_sum = literal(0.0)
        for month in normalized_months:
            month_score_sum = month_score_sum + col(getattr(TravelDestinationRecord, month))

        return month_score_sum / literal(float(len(normalized_months)))

    def _validate_embedding_dimension(self, embedding: Sequence[float]) -> None:
        if len(embedding) != self.embedding_dimension:
            raise ValueError(
                "Embedding dimension mismatch: "
                f"expected {self.embedding_dimension}, got {len(embedding)}"
            )

    def _validate_limit(self, limit: int | None) -> None:
        if limit is not None and limit <= 0:
            raise ValueError("limit must be greater than zero")

    def _validate_weight(self, weight: float, field_name: str) -> None:
        if weight < 0.0:
            raise ValueError(f"{field_name} must be greater than or equal to zero")
