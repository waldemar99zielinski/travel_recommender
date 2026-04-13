import type {
    RecommendationRequestDto,
    RecommendationResponseDto,
} from "@/models/recommendation.models";
import { apiConfig } from "@/shared/api/api.config";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "RecommendationApi" });

export async function fetchRecommendations(
    payload: RecommendationRequestDto,
): Promise<RecommendationResponseDto> {
    const startedAt = Date.now();
    logger.trace("Sending recommendation request", {
        userId: payload.user_id,
        sessionId: payload.session_id,
        messageLength: payload.message.length,
    });

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
        logger.error("Recommendation request failed", {
            status: response.status,
            statusText: response.statusText,
            durationMs: Date.now() - startedAt,
        });
        throw new Error(
            `Recommendation request failed with status ${response.status}`,
        );
    }

    const responseData: RecommendationResponseDto = await response.json();
    logger.debug("Recommendation request succeeded", {
        durationMs: Date.now() - startedAt,
        recommendationsCount: responseData.recommendations.length,
    });

    return responseData;
}
