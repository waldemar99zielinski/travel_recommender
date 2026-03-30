import type {
    RecommendationRequestDto,
    RecommendationResponseDto,
} from "@/models/recommendation/model/types";

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080";

export async function fetchRecommendations(
    payload: RecommendationRequestDto,
): Promise<RecommendationResponseDto> {
    const response = await fetch(
        `${API_BASE_URL}/api/v1/recommendations/chat`,
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
