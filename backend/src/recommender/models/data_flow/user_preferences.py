from typing import Literal
from typing import Optional

from pydantic import BaseModel, Field


class Preference(BaseModel):
    """
    Represents a single category preference extracted from user input.

    strength:
        Integer from 0 to 5 indicating strength of preference:
        0 = explicitly dislikes
        1 = very weak interest
        2 = weak interest
        3 = neutral / implicit interest
        4 = strong interest
        5 = very strong / explicit preference

    extracted_text:
        Short phrase or sentence extracted from the user's original input
        that expresses this preference.
    """

    strength: int = Field(
        ...,
        ge=0,
        le=5,
        description="Strength of preference from 0 (dislike) to 5 (very strong interest)",
    )
    extracted_text: str = Field(
        ...,
        description="Phrase extracted from the user input that supports this preference",
    )

    def __repr__(self) -> str:
        return (
            "Preference(\n"
            f"  strength={self.strength},\n"
            f"  extracted_text={self.extracted_text!r}\n"
            ")"
        )


class PricePreference(BaseModel):
    """Budget preference extracted from user query."""

    min_cost_per_week: Optional[float] = Field(
        None,
        ge=0,
        description="Minimum weekly budget if explicitly stated",
    )
    max_cost_per_week: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum weekly budget if explicitly stated",
    )
    budget_tier: Optional[Literal["low", "medium", "high"]] = Field(
        None,
        description="Budget tier hint such as low, medium, or high",
    )
    extracted_text: str = Field(
        ...,
        description="Phrase extracted from user input supporting budget preference",
    )


class PopularityPreference(BaseModel):
    """Popularity or crowding preference extracted from user query."""

    mode: str = Field(
        ...,
        description="Preference mode, for example prefer_popular or avoid_crowds",
    )
    strength: int = Field(
        ...,
        ge=0,
        le=5,
        description="Strength of popularity preference from 0 to 5",
    )
    extracted_text: str = Field(
        ...,
        description="Phrase extracted from user input supporting popularity preference",
    )


class TimeOfYearPreference(BaseModel):
    """Seasonality preference extracted from user query."""

    months: Optional[list[str]] = Field(
        None,
        description="Requested travel months using three-letter lowercase names",
    )
    season: Optional[str] = Field(
        None,
        description="Requested season such as winter, spring, summer, or autumn",
    )
    extracted_text: str = Field(
        ...,
        description="Phrase extracted from user input supporting timing preference",
    )


class UserInterestPreferences(BaseModel):
    """
    Structured user interest preferences extracted from a raw user query.

    This model intentionally contains only thematic interests and excludes
    logistical preferences (price, popularity, seasonality).
    """

    raw_user_query: str = Field(
        ...,
        description="Original unmodified user input from which preferences were extracted",
    )
    nature: Optional[Preference] = Field(
        None,
        description="Preference related to nature, landscapes, parks, and outdoor environments",
    )
    hiking: Optional[Preference] = Field(
        None,
        description="Preference related to hiking, trekking, or long walks in natural terrain",
    )
    beach: Optional[Preference] = Field(
        None,
        description="Preference related to beaches, seaside locations, and coastal activities",
    )
    watersports: Optional[Preference] = Field(
        None,
        description="Preference related to water-based sports such as surfing, diving, snorkeling, or kayaking",
    )
    entertainment: Optional[Preference] = Field(
        None,
        description="Preference related to entertainment such as nightlife, shows, events, or amusement activities",
    )
    wintersports: Optional[Preference] = Field(
        None,
        description="Preference related to winter sports such as skiing, snowboarding, or ice activities",
    )
    culture: Optional[Preference] = Field(
        None,
        description="Preference related to cultural experiences such as museums, traditions, history, and local customs",
    )
    culinary: Optional[Preference] = Field(
        None,
        description="Preference related to food, dining, gastronomy, and culinary experiences",
    )
    architecture: Optional[Preference] = Field(
        None,
        description="Preference related to architecture, historical buildings, and urban design",
    )
    shopping: Optional[Preference] = Field(
        None,
        description="Preference related to shopping, markets, malls, and retail experiences",
    )

    def are_preferences_present(self) -> bool:
        """Return True if any interest category is present, else False."""
        for field_name in UserInterestPreferences.model_fields:
            if field_name == "raw_user_query":
                continue
            if getattr(self, field_name) is not None:
                return True
        return False

    def __repr__(self) -> str:
        lines = ["UserInterestPreferences("]
        lines.append(f"  raw_user_query={self.raw_user_query!r},")

        for field_name in self.model_fields:
            if field_name == "raw_user_query":
                continue

            value = getattr(self, field_name)
            if value is None:
                continue

            value_repr = repr(value).replace("\n", "\n  ")
            lines.append(f"  {field_name}={value_repr},")

        lines.append(")")
        return "\n".join(lines)


class UserLogisticalPreferences(BaseModel):
    """
    Structured user logistical preferences extracted from a raw user query.

    This model is independent from user interest preferences and only captures
    constraints or soft requirements for ranking.
    """

    raw_user_query: str = Field(
        ...,
        description="Original unmodified user input from which preferences were extracted",
    )
    price: Optional[PricePreference] = Field(
        None,
        description="User budget preference for weekly trip cost",
    )
    popularity: Optional[PopularityPreference] = Field(
        None,
        description="User preference for crowded/popular or quieter places",
    )
    time_of_year: Optional[TimeOfYearPreference] = Field(
        None,
        description="User preference for travel months or season",
    )

    def are_preferences_present(self) -> bool:
        """Return True if any logistical preference is present, else False."""
        return any(
            [
                self.price is not None,
                self.popularity is not None,
                self.time_of_year is not None,
            ]
        )

    def __repr__(self) -> str:
        lines = ["UserLogisticalPreferences("]
        lines.append(f"  raw_user_query={self.raw_user_query!r},")

        lines.append(f"  price={self.price!r},")
        lines.append(f"  popularity={self.popularity!r},")
        lines.append(f"  time_of_year={self.time_of_year!r},")

        lines.append(")")
        return "\n".join(lines)
