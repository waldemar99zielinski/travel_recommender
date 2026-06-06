from pydantic import BaseModel, Field

class RecommendationV2ResponseGenerationResult(BaseModel):
    """Unified response payload for recommendation_v2 response generation agents."""

    response: str = Field(..., description="Final response text to be sent to the user")