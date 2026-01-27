
from pydantic import BaseModel, Field
from typing import Optional

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
        description="Strength of preference from 0 (dislike) to 5 (very strong interest)"
    )

    extracted_text: str = Field(
        ...,
        description="Phrase extracted from the user input that supports this preference"
    )

    def __repr__(self) -> str:
        return (
            "Preference(\n"
            f"  strength={self.strength},\n"
            f"  extracted_text={self.extracted_text!r}\n"
            ")"
    )


class UserPreferences(BaseModel):
    """
    Structured representation of user preferences extracted from a raw user query.

    - the primary output of a preference extraction step
    - the input for preference validation and correction
    - a reliable, explainable representation of user intent

    Semantics:
    - Each category field is OPTIONAL.
    - A value of `None` means the user did not express any clear preference.
    - A populated Preference means the preference was explicitly or implicitly stated.
    - Negative preferences MUST be represented with strength = 0 (not by omission).
    """

    raw_user_query: str = Field(
        ...,
        description="Original unmodified user input from which preferences were extracted"
    )

    nature: Optional[Preference] = Field(
        None,
        description="Preference related to nature, landscapes, parks, and outdoor environments"
    )

    hiking: Optional[Preference] = Field(
        None,
        description="Preference related to hiking, trekking, or long walks in natural terrain"
    )

    beach: Optional[Preference] = Field(
        None,
        description="Preference related to beaches, seaside locations, and coastal activities"
    )

    watersports: Optional[Preference] = Field(
        None,
        description="Preference related to water-based sports such as surfing, diving, snorkeling, or kayaking"
    )

    entertainment: Optional[Preference] = Field(
        None,
        description="Preference related to entertainment such as nightlife, shows, events, or amusement activities"
    )

    wintersports: Optional[Preference] = Field(
        None,
        description="Preference related to winter sports such as skiing, snowboarding, or ice activities"
    )

    culture: Optional[Preference] = Field(
        None,
        description="Preference related to cultural experiences such as museums, traditions, history, and local customs"
    )

    culinary: Optional[Preference] = Field(
        None,
        description="Preference related to food, dining, gastronomy, and culinary experiences"
    )

    architecture: Optional[Preference] = Field(
        None,
        description="Preference related to architecture, historical buildings, and urban design"
    )

    shopping: Optional[Preference] = Field(
        None,
        description="Preference related to shopping, markets, malls, and retail experiences"
    )


    def are_preferences_present(self) -> bool:
        """
        Returns True if any category field (except raw_user_query) is present, else False.
        """
        for field_name in UserPreferences.model_fields:
            if field_name == "raw_user_query":
                continue
            if getattr(self, field_name) is not None:
                return True
        return False

    def __repr__(self) -> str:
        lines = ["UserPreferences("]

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