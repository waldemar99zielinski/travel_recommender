import { useCallback, useMemo, useState } from "react";

import type { RecommendationResponseDto } from "@/models/recommendation.models";
import type {
    RecommendationContextValue,
    RecommendationRequest,
} from "@/shared/context/recommendation/recommendationContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "RecommendationContext" });

export function useRecommendationContextValue(): RecommendationContextValue {
    const [recommendationRequest, setRecommendationRequest] =
        useState<RecommendationRequest | null>(null);
    const [recommendationResponse, setRecommendationResponse] =
        useState<RecommendationResponseDto | null>(null);

    const requestRecommendation = useCallback((query: string | null) => {
        logger.trace("Recommendation requested", {
            query,
        });
        setRecommendationRequest({
            query,
            requestedAt: Date.now(),
        });
    }, []);

    const respondRecommendation = useCallback(
        (response: RecommendationResponseDto) => {
            logger.debug("Recommendation response stored", {
                response,
            });
            setRecommendationResponse(response);
        },
        [],
    );

    const clearRecommendationRequest = useCallback(() => {
        logger.debug("Clearing recommendation request");
        setRecommendationRequest(null);
    }, []);

    const clearRecommendationResponse = useCallback(() => {
        logger.debug("Clearing recommendation response");
        setRecommendationResponse(null);
    }, []);

    return useMemo(
        () => ({
            recommendationRequest,
            recommendationResponse,
            requestRecommendation,
            respondRecommendation,
            clearRecommendationRequest,
            clearRecommendationResponse,
        }),
        [
            recommendationRequest,
            recommendationResponse,
            requestRecommendation,
            respondRecommendation,
            clearRecommendationRequest,
            clearRecommendationResponse,
        ],
    );
}
