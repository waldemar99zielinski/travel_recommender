import { createContext, type Dispatch, type SetStateAction } from "react";

import type { ChatMessage } from "@/components/chat/Chat.interfaces";
import type { RecommendationResponseDto } from "@/models/recommendation.models";

export interface RecommendationFeatureContextValue {
    messages: ChatMessage[];
    recommendationResponse: RecommendationResponseDto | null;
    selectedRegionId: string | null;
    setSelectedRegionId: Dispatch<SetStateAction<string | null>>;
    focusedRegionId: string | null;
    setFocusedRegionId: Dispatch<SetStateAction<string | null>>;
    startNewSession: () => Promise<void>;
    submitRecommendationMessage: (
        message: string,
    ) => Promise<RecommendationResponseDto | null>;
    recommendationsStatus: "idle" | "loading" | "success" | "error";
    recommendationsError: string | null;
    isLoading: boolean;
    errorMessage: string | null;
}

export const RecommendationFeatureContext =
    createContext<RecommendationFeatureContextValue | undefined>(undefined);
