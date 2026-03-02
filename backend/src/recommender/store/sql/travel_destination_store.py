from __future__ import annotations

from typing import Any
from typing import Literal

from sqlalchemy import case
from sqlalchemy import func
from sqlalchemy import literal
from sqlmodel import col
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from sqlmodel import delete
from sqlmodel import select
from sqlmodel.sql.expression import SelectOfScalar

from recommender.models.data_flow.recommendation_output import Recommendation
from recommender.models.data_flow.user_preferences import UserLogisticalPreferences
from recommender.store.sql.base_sql_store import BaseSqlStore
from recommender.store.sql.base_sql_store import TableModel
from recommender.store.sql.travel_destination_sql_csv_loader import TravelDestinationSqlCsvLoader
from recommender.store.sql.travel_destination_table_mapper import TravelDestinationTableMapper
from recommender.store.sql.travel_destination_table import TravelDestinationTable
from utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)

SEASON_TO_MONTHS: dict[str, tuple[str, ...]] = {
    "winter": ("dec", "jan", "feb"),
    "spring": ("mar", "apr", "may"),
    "summer": ("jun", "jul", "aug"),
    "autumn": ("sep", "oct", "nov"),
    "fall": ("sep", "oct", "nov"),
}

INTEREST_WEIGHT = 0.85
LOGISTICS_WEIGHT = 0.15
PRICE_WEIGHT = 0.45
TIME_WEIGHT = 0.35
POPULARITY_WEIGHT = 0.20


class SqlStore(BaseSqlStore):
    """SQLite implementation of a multi-table SQLModel store."""

    def __init__(self, db_url: str) -> None:
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        self._loaded = False
        #TODO dependency injection
        self.travel_destination_loader = TravelDestinationSqlCsvLoader()
        self.travel_destination_mapper = TravelDestinationTableMapper()

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

    def rank_travel_destinations_by_logistical_preferences(
        self,
        recommendation: list[Recommendation],
        logistical_preferences: UserLogisticalPreferences,
    ) -> list[Recommendation]:
        """Rank vector candidates with SQL-based logistical re-scoring."""
        self._ensure_loaded()

        if not recommendation:
            return []

        if not logistical_preferences.are_preferences_present():
            return recommendation

        recommendation_ids = [item.u_name for item in recommendation]
        embedding_score_by_id = {item.u_name: item.embedding_score for item in recommendation}
        interest_score_by_id = self._build_interest_score_by_id(recommendation)

        interest_score_expr = case(
            *[
                (col(TravelDestinationTable.id) == destination_id, literal(score))
                for destination_id, score in interest_score_by_id.items()
            ],
            else_=literal(0.0),
        )

        logistics_score_expr = self._build_logistics_score_expression(logistical_preferences)
        final_score_expr = (
            (literal(INTEREST_WEIGHT) * interest_score_expr)
            + (literal(LOGISTICS_WEIGHT) * logistics_score_expr)
        )

        statement = (
            select(
                TravelDestinationTable,
                logistics_score_expr.label("logistical_score"),
                final_score_expr.label("ranking_score"),
            )
            .where(col(TravelDestinationTable.id).in_(recommendation_ids))
            .order_by(col(final_score_expr).desc())
        )

        with Session(self.engine) as session:
            rows = list(session.exec(statement).all())

        ranked: list[Recommendation] = []
        seen_ids: set[str] = set()
        for row, logistical_score, ranking_score in rows:
            seen_ids.add(row.id)
            ranked.append(
                self.travel_destination_mapper.to_recommendation(
                    row=row,
                    embedding_score=embedding_score_by_id.get(row.id),
                    interest_score=interest_score_by_id.get(row.id),
                    logistical_score=logistical_score,
                    ranking_score=ranking_score,
                ),
            )

        for item in recommendation:
            if item.u_name not in seen_ids:
                ranked.append(item)

        logger.info(
            "Ranked %s recommendations with SQL logistical scoring.",
            len(ranked),
        )
        return ranked

    def _build_interest_score_by_id(
        self,
        recommendations: list[Recommendation],
    ) -> dict[str, float]:
        if not recommendations:
            return {}

        if len(recommendations) == 1:
            return {recommendations[0].u_name: 1.0}

        raw_scores = [item.embedding_score for item in recommendations]
        min_score = min(raw_scores)
        max_score = max(raw_scores)

        if abs(max_score - min_score) < 1e-9:
            return {item.u_name: 1.0 for item in recommendations}

        normalized_scores: dict[str, float] = {}
        for item in recommendations:
            normalized = (item.embedding_score - min_score) / (max_score - min_score)
            # lower embedding scores indicate better matches, so invert the normalized score
            normalized = 1.0 - normalized
            # faiss should use the Squared Euclidean Distance, so values should be non-negative, but just in case
            normalized_scores[item.u_name] = max(0.0, min(1.0, normalized))
        return normalized_scores

    def _build_logistics_score_expression(
        self,
        logistical_preferences: UserLogisticalPreferences,
    ) -> Any:
        weighted_scores: list[tuple[float, Any]] = []

        price_expr = self._build_price_score_expression(logistical_preferences)
        if price_expr is not None:
            weighted_scores.append((PRICE_WEIGHT, price_expr))

        time_expr = self._build_time_score_expression(logistical_preferences)
        if time_expr is not None:
            weighted_scores.append((TIME_WEIGHT, time_expr))

        popularity_expr = self._build_popularity_score_expression(logistical_preferences)
        if popularity_expr is not None:
            weighted_scores.append((POPULARITY_WEIGHT, popularity_expr))

        if not weighted_scores:
            return literal(1.0)

        total_weight = sum(weight for weight, _ in weighted_scores)
        weighted_sum = literal(0.0)
        for weight, expression in weighted_scores:
            weighted_sum = weighted_sum + (literal(weight) * expression)

        return weighted_sum / literal(total_weight)

    def _build_price_score_expression(
        self,
        logistical_preferences: UserLogisticalPreferences,
    ) -> Any | None:
        price_preferences = logistical_preferences.price
        if price_preferences is None:
            return None

        score_terms: list[Any] = []
        cost_column = col(TravelDestinationTable.cost_per_week)

        # max min logic
        if price_preferences.max_cost_per_week is not None:
            max_cost = float(price_preferences.max_cost_per_week)
            max_denominator = max(max_cost, 1.0)

            # if cost is below or equal to max_cost, score is 1.0
            # otherwise it's 0
            upper_score = case(
                (cost_column <= literal(max_cost), literal(1.0)),
                (cost_column >= literal(max_cost + max_denominator), literal(0.0)),
                else_=(literal(1.0) - ((cost_column - literal(max_cost)) / literal(max_denominator))),
            )

            score_terms.append(upper_score)

        if price_preferences.min_cost_per_week is not None:
            min_cost = float(price_preferences.min_cost_per_week)
            min_denominator = max(min_cost, 1.0)

            # if cost is above or equal to min_cost, score is 1.0
            # otherwise it's 0
            lower_score = case(
                (cost_column >= literal(min_cost), literal(1.0)),
                (cost_column <= literal(max(0.0, min_cost - min_denominator)), literal(0.0)),
                else_=(literal(1.0) - ((literal(min_cost) - cost_column) / literal(min_denominator))),
            )

            score_terms.append(lower_score)

        if score_terms:
            if len(score_terms) == 1:
                return score_terms[0]

            score_sum = literal(0.0)
            for score in score_terms:
                score_sum = score_sum + score
            return score_sum / literal(float(len(score_terms)))

        # budget tier logic, if explicit min/max not provided
        if price_preferences.budget_tier is not None:
            tier_to_target = {
                "low": 450.0,
                "medium": 900.0,
                "high": 1800.0,
            }

            target = tier_to_target.get(price_preferences.budget_tier or "")

            if target is None:
                return None

            tolerance = max(target * 0.6, 1.0)

            return func.max(
                literal(0.0),
                literal(1.0) - (func.abs(cost_column - literal(target)) / literal(tolerance)),
            )

        return None

    def _build_popularity_score_expression(
        self,
        logistical_preferences: UserLogisticalPreferences,
    ) -> Any | None:
        popularity_preferences = logistical_preferences.popularity
        if popularity_preferences is None:
            return None

        target = popularity_preferences.strength / 5.0
        popularity_column = col(TravelDestinationTable.popularity)
        return func.max(
            literal(0.0),
            literal(1.0) - func.abs(popularity_column - literal(target)),
        )

    def _build_time_score_expression(
        self,
        logistical_preferences: UserLogisticalPreferences,
    ) -> Any | None:
        time_preferences = logistical_preferences.time_of_year
        if time_preferences is None:
            return None

        months = self._extract_months(
            months=time_preferences.months,
            season=time_preferences.season,
        )
        if not months:
            return None

        month_sum = literal(0.0)
        for month in months:
            month_sum = month_sum + col(getattr(TravelDestinationTable, month))
        return month_sum / literal(float(len(months)))

    def _extract_months(self, months: list[str] | None, season: str | None) -> tuple[str, ...]:
        valid_months = {
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
        if months:
            normalized_months = tuple(month.lower().strip() for month in months if month)
            filtered_months = tuple(month for month in normalized_months if month in valid_months)
            if filtered_months:
                return filtered_months

        if season:
            return SEASON_TO_MONTHS.get(season.lower().strip(), ())

        return ()

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            raise RuntimeError("SQLite SQLModel store is not loaded. Call load() first.")
