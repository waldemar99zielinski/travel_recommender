from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RecommendationBase(BaseModel):
    """Core destination metadata independent from ranking/scoring logic."""

    parent_region: Optional[str] = Field(None, description="Parent region")
    region: Optional[str] = Field(None, description="Destination region")
    u_name: Optional[str] = Field(None, description="Display name from dataset")

    popularity: Optional[str] = Field(None, description="Popularity score")
    cost_per_week: Optional[float] = Field(None, description="Weekly travel cost")

    jan: Optional[str] = Field(None, description="Travel season value for January")
    feb: Optional[str] = Field(None, description="Travel season value for February")
    mar: Optional[str] = Field(None, description="Travel season value for March")
    apr: Optional[str] = Field(None, description="Travel season value for April")
    may: Optional[str] = Field(None, description="Travel season value for May")
    jun: Optional[str] = Field(None, description="Travel season value for June")
    jul: Optional[str] = Field(None, description="Travel season value for July")
    aug: Optional[str] = Field(None, description="Travel season value for August")
    sep: Optional[str] = Field(None, description="Travel season value for September")
    oct: Optional[str] = Field(None, description="Travel season value for October")
    nov: Optional[str] = Field(None, description="Travel season value for November")
    dec: Optional[str] = Field(None, description="Travel season value for December")

    safety: Optional[str] = Field(None, description="Safety preference signal")
    nature: Optional[str] = Field(None, description="Nature preference signal")
    hiking: Optional[str] = Field(None, description="Hiking preference signal")
    beach: Optional[str] = Field(None, description="Beach preference signal")
    watersports: Optional[str] = Field(None, description="Watersports preference signal")
    entertainment: Optional[str] = Field(None, description="Entertainment preference signal")
    wintersports: Optional[str] = Field(None, description="Wintersports preference signal")
    culture: Optional[str] = Field(None, description="Culture preference signal")
    culinary: Optional[str] = Field(None, description="Culinary preference signal")
    architecture: Optional[str] = Field(None, description="Architecture preference signal")
    shopping: Optional[str] = Field(None, description="Shopping preference signal")

    description: Optional[str] = Field(None, description="Destination description")

    def __repr__(self) -> str:
        lines: list[str] = ["RecommendationBase("]
        lines.append(f"  region={self.region!r},")
        lines.append(f"  parent_region={self.parent_region!r},")
        lines.append(f"  u_name={self.u_name!r},")
        lines.append(f"  popularity={self.popularity!r},")
        lines.append(f"  cost_per_week={self.cost_per_week!r},")
        lines.append(")")
        return "\n".join(lines)


class Recommendation(RecommendationBase):
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
