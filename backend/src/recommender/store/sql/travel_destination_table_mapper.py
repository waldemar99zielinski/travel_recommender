from __future__ import annotations

from recommender.models.data_flow.recommendation_output import Recommendation
from recommender.store.sql.travel_destination_table import TravelDestinationTable


class TravelDestinationTableMapper:
    """Maps SQL travel destination rows to recommendation models."""

    def to_recommendation(
        self,
        row: TravelDestinationTable,
        embedding_score: float,
        interest_score: float | None,
        logistical_score: float | None,
        ranking_score: float | None,
    ) -> Recommendation:
        return Recommendation(
            parent_region=row.parent_region,
            region=row.region,
            u_name=row.id,
            popularity=row.popularity,
            cost_per_week=row.cost_per_week,
            jan=row.jan,
            feb=row.feb,
            mar=row.mar,
            apr=row.apr,
            may=row.may,
            jun=row.jun,
            jul=row.jul,
            aug=row.aug,
            sep=row.sep,
            oct=row.oct,
            nov=row.nov,
            dec=row.dec,
            nature=row.nature,
            hiking=row.hiking,
            beach=row.beach,
            watersports=row.watersports,
            entertainment=row.entertainment,
            wintersports=row.wintersports,
            culture=row.culture,
            culinary=row.culinary,
            architecture=row.architecture,
            shopping=row.shopping,
            description=row.description,
            embedding_score=float(embedding_score),
            interest_score=None if interest_score is None else float(interest_score),
            logistical_score=None if logistical_score is None else float(logistical_score),
            ranking_score=None if ranking_score is None else float(ranking_score),
        )
