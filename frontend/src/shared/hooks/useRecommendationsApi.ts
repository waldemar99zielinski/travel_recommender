import { useCallback } from "react";

import type {
    RecommendationRequestDto,
    RecommendationResponseDto,
} from "@/models/recommendation.models";
import { fetchRecommendations } from "@/shared/api/recommendation.api";
import { useAppConfigContext } from "@/shared/context";
import type { ApiHookTuple } from "@/shared/hooks/apiHookTypes";
import { useApiRequest } from "@/shared/hooks/useApiRequest";

export function useRecommendationsApi(): ApiHookTuple<
    RecommendationResponseDto,
    RecommendationRequestDto
> {
    const {
        config: { recommendationApiVersion },
    } = useAppConfigContext();

    const request = useCallback(async (payload?: RecommendationRequestDto) => {
        if (payload == null) {
            throw new Error("Recommendation payload is required");
        }

        return fetchRecommendations(payload, recommendationApiVersion);
    }, [recommendationApiVersion]);

    return useApiRequest<RecommendationResponseDto, RecommendationRequestDto>(
        request,
        {
            requestName: "recommendations",
        },
    );
}
