from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

class RecommendationBase(BaseModel):
    """
        Single recommendation match returned by embedding search.
    """

    score: float = Field(..., description="Similarity score returned by vector search")
    content: str = Field(..., description="Document content used in similarity search")
    source: str = Field(..., description="Source CSV file path")

    parent_region: str = Field(None, description="Parent region")
    region: str = Field(None, description="Destination region")
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
        lines.append(f"  score={self.score:.4f},")
        lines.append(f"  region={self.region!r},")
        lines.append(f"  parent_region={self.parent_region!r},")
        lines.append(f"  u_name={self.u_name!r},")
        # lines.append(f"  popularity={self.popularity!r},")
        # lines.append(f"  cost_per_week={self.cost_per_week!r},")

        # seasonality = {
        #     "jan": self.jan,
        #     "feb": self.feb,
        #     "mar": self.mar,
        #     "apr": self.apr,
        #     "may": self.may,
        #     "jun": self.jun,
        #     "jul": self.jul,
        #     "aug": self.aug,
        #     "sep": self.sep,
        #     "oct": self.oct,
        #     "nov": self.nov,
        #     "dec": self.dec,
        # }
        # lines.append(f"  seasonality={seasonality!r},")

        # lines.append(f"  source={self.source!r},")
        # lines.append(f"  content_preview={self.content[:120]!r},")
        lines.append(")")
        return "\n".join(lines)
