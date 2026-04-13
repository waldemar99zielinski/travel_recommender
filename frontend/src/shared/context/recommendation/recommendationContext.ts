import { createContext } from "react";

import type { RecommendationResponseDto } from "@/models/recommendation.models";

export interface RecommendationRequest {
    query: string | null;
    requestedAt: number;
}

export interface RecommendationContextValue {
    recommendationRequest: RecommendationRequest | null;
    recommendationResponse: RecommendationResponseDto | null;
    requestRecommendation: (query: string | null) => void;
    respondRecommendation: (response: RecommendationResponseDto) => void;
    clearRecommendationRequest: () => void;
    clearRecommendationResponse: () => void;
}

export const RecommendationContext =
    createContext<RecommendationContextValue | undefined>(undefined);
