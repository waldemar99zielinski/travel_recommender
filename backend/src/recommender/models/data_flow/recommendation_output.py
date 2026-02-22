from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field
from recommender.models.data_flow.travel_destination import TravelDestination

class Recommendation(TravelDestination):
    """Recommendation record with embedding and final ranking scores."""

    embedding_score: float = Field(..., description="Similarity score from embedding retrieval")
    ranking_score: Optional[float] = Field(
        None,
        description="Final score after additional ranking by logistics/preferences",
    )
    content: str = Field(..., description="Document content used in similarity search")
    source: str = Field(..., description="Source CSV file path")

    def __repr__(self) -> str:
        lines: list[str] = ["Recommendation("]
        lines.append(f"  embedding_score={self.embedding_score:.4f},")
        lines.append(f"  ranking_score={self.ranking_score!r},")
        lines.append(f"  region={self.region!r},")
        lines.append(f"  parent_region={self.parent_region!r},")
        lines.append(f"  u_name={self.u_name!r},")
        lines.append(f"  popularity={self.popularity!r},")
        lines.append(f"  cost_per_week={self.cost_per_week!r},")
        lines.append(f"  source={self.source!r},")
        lines.append(f"  content_preview={self.content[:120]!r},")
        lines.append(")")
        return "\n".join(lines)
