import {
    type RecommendationRequestDto,
    type RecommendationResponseDto,
    validateRecommendationRequestDto,
    validateRecommendationResponseDto,
} from "@/models/recommendation.models";
import { recommendationApiUrlBuilder } from "@/shared/api/urls.api";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "RecommendationApi" });

export async function fetchRecommendations(
    payload: RecommendationRequestDto,
): Promise<RecommendationResponseDto> {
    const requestPayload = validateRecommendationRequestDto(payload);
    const startedAt = Date.now();
    const url = recommendationApiUrlBuilder.fetchRecommendations();

    logger.trace("Sending recommendation request", {
        url,
        userId: requestPayload.user_id,
        sessionId: requestPayload.session_id,
        messageLength: requestPayload.message.length,
        payload: requestPayload,
    });

    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(requestPayload),
    });

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

    const rawResponseData: unknown = await response.json();
    const responseData = validateRecommendationResponseDto(rawResponseData);

    logger.debug("Recommendation request succeeded", {
        status: response.status,
        durationMs: Date.now() - startedAt,
        requestPayload,
        responseData,
    });

    return responseData;
}
