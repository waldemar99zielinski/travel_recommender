import { useCallback } from "react";

import type {
    RecommendationRequestDto,
    RecommendationResponseDto,
} from "@/models/recommendation/model/types";
import { fetchRecommendations } from "@/shared/api/recommendationApi";
import type { ApiHookTuple } from "@/shared/hooks/apiHookTypes";
import { useApiRequest } from "@/shared/hooks/useApiRequest";

export function useRecommendationsApi(): ApiHookTuple<
    RecommendationResponseDto,
    RecommendationRequestDto
> {
    const request = useCallback(async (payload?: RecommendationRequestDto) => {
        if (payload == null) {
            throw new Error("Recommendation payload is required");
        }

        return fetchRecommendations(payload);
    }, []);

    return useApiRequest<RecommendationResponseDto, RecommendationRequestDto>(
        request,
    );
}
