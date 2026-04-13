import type {
    RecommendationRequestDto,
    RecommendationResponseDto,
} from "@/models/recommendation.models";
import { apiConfig } from "@/shared/api/api.config";

export async function fetchRecommendations(
    payload: RecommendationRequestDto,
): Promise<RecommendationResponseDto> {
    const response = await fetch(
        `${apiConfig.baseUrl}/api/v1/recommendations/chat`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        },
    );

    if (!response.ok) {
        throw new Error(
            `Recommendation request failed with status ${response.status}`,
        );
    }

    const responseData: RecommendationResponseDto = await response.json();

    return responseData;
}
