from __future__ import annotations

from typing import Optional

from pydantic import Field
from recommender.models.data_flow.travel_destination import TravelDestination

class Recommendation(TravelDestination):
    """Recommendation record with embedding and final ranking scores."""

    embedding_score: float = Field(
        ...,
        description="Raw similarity/distance score returned by vector retrieval",
    )
    interest_score: Optional[float] = Field(
        None,
        description="Normalized interest relevance score used for blended ranking",
    )
    logistical_score: Optional[float] = Field(
        None,
        description="Logistical compatibility score used for blended ranking",
    )
    ranking_score: Optional[float] = Field(
        None,
        description="Final score after additional ranking by logistics/preferences",
    )

    def __repr__(self) -> str:
        lines: list[str] = ["Recommendation("]
        lines.append(f"  embedding_score={self.embedding_score:.4f},")
        lines.append(f"  interest_score={self.interest_score!r},")
        lines.append(f"  logistical_score={self.logistical_score!r},")
        lines.append(f"  ranking_score={self.ranking_score!r},")
        lines.append(f"  region={self.region!r},")
        lines.append(f"  parent_region={self.parent_region!r},")
        lines.append(f"  u_name={self.u_name!r},")
        lines.append(")")
        return "\n".join(lines)
