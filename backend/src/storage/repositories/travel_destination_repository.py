from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import literal
from sqlalchemy import Float
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func
from sqlmodel import Session
from sqlmodel import col
from sqlmodel import select

from storage.models.travel_destination import TravelDestinationRecord
from storage.stores.query_models import DATETIME_FIELDS
from storage.stores.query_models import NUMERIC_FIELDS
from storage.stores.query_models import TEXT_FIELDS
from storage.stores.query_models import QueriedTravelDestination
from storage.stores.query_models import TravelDestinationQuery
from storage.stores.query_models import TravelDestinationQueryFilter
from storage.stores.query_models import TravelDestinationQuerySort
from storage.stores.query_models import coerce_query_datetime
from storage.stores.search_models import TravelCostStatistics
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

    def cost_per_week_statistics(self) -> TravelCostStatistics:
        """Return percentile statistics for the cost_per_week field."""
        statement = select(
            func.percentile_cont(0.5)
            .within_group(col(TravelDestinationRecord.cost_per_week))
            .label("percentile_50"),
            func.percentile_cont(0.75)
            .within_group(col(TravelDestinationRecord.cost_per_week))
            .label("percentile_75"),
        )
        result = self.session.exec(statement).one()
        return TravelCostStatistics(
            percentile_50=float(result[0]) if result[0] is not None else None,
            percentile_75=float(result[1]) if result[1] is not None else None,
        )

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

    def query(
        self,
        request: TravelDestinationQuery,
        query_embedding: Sequence[float] | None = None,
    ) -> list[QueriedTravelDestination]:
        """Run structured metadata, text, and semantic queries over travel destinations."""
        self._validate_limit(request.limit)
        self._validate_query_weights(request)
        self._validate_semantic_query_pairing(request=request, query_embedding=query_embedding)
        if query_embedding is not None:
            self._validate_embedding_dimension(query_embedding)

        text_score_expression, text_match_condition = self._build_text_query_components(request)
        semantic_score_expression, distance_expression = self._build_semantic_query_components(query_embedding)
        ranking_score_expression = self._build_query_ranking_expression(
            request=request,
            semantic_score_expression=semantic_score_expression,
            text_score_expression=text_score_expression,
        )

        statement = (
            select(TravelDestinationRecord)
            .add_columns(distance_expression.label("embedding_distance"))
            .add_columns(semantic_score_expression.label("semantic_score"))
            .add_columns(text_score_expression.label("text_score"))
            .add_columns(ranking_score_expression.label("ranking_score"))
        )

        for filter_spec in request.filters:
            statement = statement.where(self._build_query_filter_expression(filter_spec))

        if text_match_condition is not None and request.semantic_query is None:
            statement = statement.where(text_match_condition)

        statement = self._apply_query_sort(
            statement=statement,
            request=request,
            ranking_score_expression=ranking_score_expression,
            distance_expression=distance_expression,
        )
        if request.limit is not None:
            statement = statement.limit(request.limit)

        rows = self.session.execute(statement).all()
        return [
            QueriedTravelDestination(
                destination=row[0],
                embedding_distance=float(row[1]),
                semantic_score=float(row[2]),
                text_score=float(row[3]),
                ranking_score=float(row[4]),
            )
            for row in rows
        ]

    def semantic_search(
        self,
        query_embedding: Sequence[float],
        limit: int | None = None,
        destination_ids: Sequence[str] | None = None,
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
        )
        statement = statement.order_by(distance_expression)
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
        destination_ids: Sequence[str] | None = None,
    ) -> list[ScoredTravelDestination]:
        """Return destinations ranked by semantic and logistics blending."""
        self._validate_embedding_dimension(query_embedding)
        self._validate_limit(limit)
        self._validate_weight(semantic_weight, "semantic_weight")
        self._validate_weight(logistics_weight, "logistics_weight")

        normalized_destination_ids = self._normalize_destination_ids(destination_ids)
        if destination_ids is not None and not normalized_destination_ids:
            return []

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
        )
        statement = self._apply_destination_id_filter(statement, normalized_destination_ids)
        statement = statement.order_by(ranking_score_expression.desc(), distance_expression)
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

    def exact_text_search(
        self,
        query: str,
        limit: int | None = None,
    ) -> list[ScoredTravelDestination]:
        """Return destinations ranked by exact field and full-text matches."""
        normalized_query = self._normalize_search_term(query)
        if not normalized_query:
            raise ValueError("query must not be empty")

        self._validate_limit(limit)

        region_expression = self._normalize_text_expression(col(TravelDestinationRecord.region))
        parent_region_expression = self._normalize_text_expression(col(TravelDestinationRecord.parent_region))
        description_expression = self._normalize_text_expression(col(TravelDestinationRecord.description))
        query_literal = literal(normalized_query)
        contains_pattern = f"%{normalized_query}%"
        search_document = self._build_search_document_expression()
        ts_query = func.websearch_to_tsquery("simple", normalized_query)
        fts_rank_expression = func.ts_rank_cd(search_document, ts_query).cast(Float)

        exact_region_score = case(
            (region_expression == query_literal, literal(1.0)),
            else_=literal(0.0),
        )
        exact_parent_region_score = case(
            (parent_region_expression == query_literal, literal(0.95)),
            else_=literal(0.0),
        )
        partial_region_score = case(
            (region_expression.like(contains_pattern), literal(0.9)),
            else_=literal(0.0),
        )
        partial_parent_region_score = case(
            (parent_region_expression.like(contains_pattern), literal(0.85)),
            else_=literal(0.0),
        )
        description_phrase_score = case(
            (description_expression.like(contains_pattern), literal(0.8)),
            else_=literal(0.0),
        )
        text_match_score_expression = func.greatest(
            exact_region_score,
            exact_parent_region_score,
            partial_region_score,
            partial_parent_region_score,
            description_phrase_score,
            func.least(literal(0.75), fts_rank_expression),
        ).cast(Float)

        statement = (
            select(TravelDestinationRecord)
            .add_columns(text_match_score_expression.label("text_match_score"))
            .where(
                or_(
                    text_match_score_expression > literal(0.0),
                    search_document.op("@@")(ts_query),
                )
            )
            .order_by(text_match_score_expression.desc(), col(TravelDestinationRecord.popularity).desc())
        )
        if limit is not None:
            statement = statement.limit(limit)

        rows = self.session.execute(statement).all()
        return [
            ScoredTravelDestination(
                destination=row[0],
                embedding_distance=0.0,
                semantic_score=float(row[1]),
                logistics_score=1.0,
                ranking_score=float(row[1]),
            )
            for row in rows
            if float(row[1]) > 0.0
        ]

    def find(
        self,
        request: TravelDestinationQuery,
    ) -> list[TravelDestinationRecord]:
        self._validate_limit(request.limit)

        statement = select(TravelDestinationRecord)

        for filter_spec in request.filters:
            statement = statement.where(self._build_query_filter_expression(filter_spec))

        statement = self._apply_find_sort(statement=statement, request=request)
        if request.limit is not None:
            statement = statement.limit(request.limit)

        return list(self.session.exec(statement).all())

    def _build_query_filter_expression(self, filter_spec: TravelDestinationQueryFilter) -> Any:
        column = col(getattr(TravelDestinationRecord, filter_spec.field))

        if filter_spec.field in TEXT_FIELDS:
            return self._build_text_filter_expression(column, filter_spec)
        if filter_spec.field in NUMERIC_FIELDS:
            return self._build_numeric_filter_expression(column, filter_spec)
        if filter_spec.field in DATETIME_FIELDS:
            return self._build_datetime_filter_expression(column, filter_spec)

        raise ValueError(f"unsupported query field: {filter_spec.field}")

    def _build_text_filter_expression(self, column: Any, filter_spec: TravelDestinationQueryFilter) -> Any:
        if filter_spec.operator == "eq":
            return self._normalize_text_expression(column) == literal(self._normalize_query_text_value(filter_spec.value))
        if filter_spec.operator == "ne":
            return self._normalize_text_expression(column) != literal(self._normalize_query_text_value(filter_spec.value))
        if filter_spec.operator == "in":
            values = [self._normalize_query_text_value(value) for value in filter_spec.values]
            return self._normalize_text_expression(column).in_(values)
        if filter_spec.operator == "starts_with":
            return self._normalize_text_expression(column).like(f"{self._normalize_query_text_value(filter_spec.value)}%")
        if filter_spec.operator == "like":
            return column.like(self._require_string_query_value(filter_spec.value))
        if filter_spec.operator == "ilike":
            return column.ilike(self._require_string_query_value(filter_spec.value))
        raise ValueError(f"unsupported text operator: {filter_spec.operator}")

    def _build_numeric_filter_expression(self, column: Any, filter_spec: TravelDestinationQueryFilter) -> Any:
        if filter_spec.field == "embedding_version":
            to_number = self._coerce_query_int_value
        else:
            to_number = self._coerce_query_float_value

        if filter_spec.operator == "eq":
            return column == literal(to_number(filter_spec.value))
        if filter_spec.operator == "ne":
            return column != literal(to_number(filter_spec.value))
        if filter_spec.operator == "gt":
            return column > literal(to_number(filter_spec.value))
        if filter_spec.operator == "gte":
            return column >= literal(to_number(filter_spec.value))
        if filter_spec.operator == "lt":
            return column < literal(to_number(filter_spec.value))
        if filter_spec.operator == "lte":
            return column <= literal(to_number(filter_spec.value))
        if filter_spec.operator == "between":
            minimum = to_number(filter_spec.min_value)
            maximum = to_number(filter_spec.max_value)
            if minimum > maximum:
                raise ValueError(f"between filter min_value cannot exceed max_value for field '{filter_spec.field}'")
            return column.between(minimum, maximum)
        if filter_spec.operator == "in":
            return column.in_([to_number(value) for value in filter_spec.values])
        raise ValueError(f"unsupported numeric operator: {filter_spec.operator}")

    def _build_datetime_filter_expression(self, column: Any, filter_spec: TravelDestinationQueryFilter) -> Any:
        if filter_spec.operator == "eq":
            return column == literal(self._coerce_query_datetime_value(filter_spec.value))
        if filter_spec.operator == "ne":
            return column != literal(self._coerce_query_datetime_value(filter_spec.value))
        if filter_spec.operator == "gt":
            return column > literal(self._coerce_query_datetime_value(filter_spec.value))
        if filter_spec.operator == "gte":
            return column >= literal(self._coerce_query_datetime_value(filter_spec.value))
        if filter_spec.operator == "lt":
            return column < literal(self._coerce_query_datetime_value(filter_spec.value))
        if filter_spec.operator == "lte":
            return column <= literal(self._coerce_query_datetime_value(filter_spec.value))
        if filter_spec.operator == "between":
            minimum = self._coerce_query_datetime_value(filter_spec.min_value)
            maximum = self._coerce_query_datetime_value(filter_spec.max_value)
            if minimum > maximum:
                raise ValueError(f"between filter min_value cannot exceed max_value for field '{filter_spec.field}'")
            return column.between(minimum, maximum)
        if filter_spec.operator == "in":
            return column.in_([self._coerce_query_datetime_value(value) for value in filter_spec.values])
        raise ValueError(f"unsupported datetime operator: {filter_spec.operator}")

    def _build_text_query_components(self, request: TravelDestinationQuery) -> tuple[Any, Any | None]:
        if request.text_query is None:
            return literal(0.0).cast(Float), None

        normalized_query = self._normalize_search_term(request.text_query)
        if not normalized_query:
            raise ValueError("text_query must not be empty")

        query_literal = literal(normalized_query)
        field_score_expressions: list[Any] = []
        document_expressions: list[Any] = []

        for field_name in request.text_fields:
            field_column = col(getattr(TravelDestinationRecord, field_name))
            normalized_expression = self._normalize_text_expression(field_column)
            document_expressions.append(field_column)
            field_score_expressions.append(
                case(
                    (normalized_expression == query_literal, literal(1.0)),
                    else_=literal(0.0),
                )
            )
        search_document = func.to_tsvector("simple", func.concat_ws(" ", *document_expressions))
        ts_query = func.websearch_to_tsquery("simple", normalized_query)
        fts_rank_expression = func.ts_rank_cd(search_document, ts_query).cast(Float)
        field_score_expressions.append(func.least(literal(0.8), fts_rank_expression))
        text_score_expression = func.greatest(*field_score_expressions).cast(Float)
        text_match_condition = or_(text_score_expression > literal(0.0), search_document.op("@@")(ts_query))
        return text_score_expression, text_match_condition

    def _build_semantic_query_components(self, query_embedding: Sequence[float] | None) -> tuple[Any, Any]:
        if query_embedding is None:
            return literal(0.0).cast(Float), literal(0.0).cast(Float)

        distance_expression = col(TravelDestinationRecord.embedding).op("<->")(list(query_embedding)).cast(Float)
        semantic_score_expression = (literal(1.0) / (literal(1.0) + distance_expression)).cast(Float)
        return semantic_score_expression, distance_expression

    def _build_query_ranking_expression(
        self,
        *,
        request: TravelDestinationQuery,
        semantic_score_expression: Any,
        text_score_expression: Any,
    ) -> Any:
        if request.semantic_query is not None and request.text_query is not None:
            total_weight = request.semantic_weight + request.text_weight
            return (
                (
                    (literal(float(request.semantic_weight)) * semantic_score_expression)
                    + (literal(float(request.text_weight)) * text_score_expression)
                )
                / literal(float(total_weight))
            ).cast(Float)
        if request.semantic_query is not None:
            return semantic_score_expression
        if request.text_query is not None:
            return text_score_expression
        return literal(1.0).cast(Float)

    def _apply_query_sort(
        self,
        *,
        statement: Any,
        request: TravelDestinationQuery,
        ranking_score_expression: Any,
        distance_expression: Any,
    ) -> Any:
        if request.sort:
            order_expressions: list[Any] = []
            for sort_spec in request.sort:
                order_expressions.append(self._build_sort_expression(sort_spec))
            order_expressions.append(col(TravelDestinationRecord.id).asc())
            return statement.order_by(*order_expressions)

        if request.semantic_query is not None or request.text_query is not None:
            return statement.order_by(
                ranking_score_expression.desc(),
                distance_expression.asc(),
                col(TravelDestinationRecord.popularity).desc(),
                col(TravelDestinationRecord.id).asc(),
            )

        return statement.order_by(col(TravelDestinationRecord.id).asc())

    def _apply_find_sort(
        self,
        *,
        statement: Any,
        request: TravelDestinationQuery,
    ) -> Any:
        if request.sort:
            order_expressions: list[Any] = []
            for sort_spec in request.sort:
                order_expressions.append(self._build_sort_expression(sort_spec))
            order_expressions.append(col(TravelDestinationRecord.id).asc())
            return statement.order_by(*order_expressions)

        return statement.order_by(col(TravelDestinationRecord.id).asc())

    def _build_sort_expression(self, sort_spec: TravelDestinationQuerySort) -> Any:
        expression = col(getattr(TravelDestinationRecord, sort_spec.field))
        if sort_spec.field in TEXT_FIELDS:
            expression = self._normalize_text_expression(expression)
        if sort_spec.direction == "desc":
            return expression.desc()
        return expression.asc()

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

    def _validate_query_weights(self, request: TravelDestinationQuery) -> None:
        if request.semantic_query is not None and request.text_query is not None:
            if request.semantic_weight == 0.0 and request.text_weight == 0.0:
                raise ValueError("semantic_weight and text_weight cannot both be zero")

    def _validate_semantic_query_pairing(
        self,
        *,
        request: TravelDestinationQuery,
        query_embedding: Sequence[float] | None,
    ) -> None:
        if request.semantic_query is None and query_embedding is not None:
            raise ValueError("query_embedding requires semantic_query")
        if request.semantic_query is not None and query_embedding is None:
            raise ValueError("semantic_query requires query_embedding")

    def _normalize_query_text_value(self, value: object) -> str:
        return self._normalize_search_term(self._require_string_query_value(value))

    def _require_string_query_value(self, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("text filters require string values")
        normalized = value.strip()
        if not normalized:
            raise ValueError("text filters require non-empty string values")
        return normalized

    def _coerce_query_float_value(self, value: object) -> float:
        if isinstance(value, bool) or value is None:
            raise ValueError("numeric filters require numbers")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError as error:
                raise ValueError("numeric filters require numbers") from error
        raise ValueError("numeric filters require numbers")

    def _coerce_query_int_value(self, value: object) -> int:
        if isinstance(value, bool) or value is None:
            raise ValueError("integer filters require integers")
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if not value.is_integer():
                raise ValueError("integer filters require integers")
            return int(value)
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError as error:
                raise ValueError("integer filters require integers") from error
        raise ValueError("integer filters require integers")

    def _coerce_query_datetime_value(self, value: object) -> datetime:
        if value is None:
            raise ValueError("datetime filters require ISO-8601 values")
        return coerce_query_datetime(value)

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

    def _apply_destination_id_filter(self, statement: Any, destination_ids: Sequence[str] | None) -> Any:
        if not destination_ids:
            return statement
        return statement.where(col(TravelDestinationRecord.id).in_(list(destination_ids)))

    def _normalize_destination_ids(self, destination_ids: Sequence[str] | None) -> list[str]:
        if destination_ids is None:
            return []

        normalized_destination_ids: list[str] = []
        for destination_id in destination_ids:
            normalized_destination_id = destination_id.strip()
            if normalized_destination_id and normalized_destination_id not in normalized_destination_ids:
                normalized_destination_ids.append(normalized_destination_id)
        return normalized_destination_ids

    def _build_search_document_expression(self) -> Any:
        return func.to_tsvector(
            "simple",
            func.concat_ws(
                " ",
                col(TravelDestinationRecord.region),
                col(TravelDestinationRecord.parent_region),
                col(TravelDestinationRecord.description),
            ),
        )

    def _normalize_text_expression(self, expression: Any) -> Any:
        return func.trim(func.regexp_replace(func.lower(expression), r"[^a-z0-9]+", " ", "g"))

    def _normalize_search_term(self, value: str) -> str:
        normalized = " ".join(value.lower().strip().split())
        normalized = "".join(character if character.isalnum() or character.isspace() else " " for character in normalized)
        return " ".join(normalized.split())
