import type { ReactNode } from "react";

import {
    RecommendationFeatureContext,
} from "@/features/recommendation/recommendationFeatureContext";
import { useRecommendationFeatureContextValue } from "@/features/recommendation/useRecommendationFeatureContextValue";

type RecommendationFeatureProviderProps = {
    children: ReactNode;
};

export function RecommendationFeatureProvider({
    children,
}: RecommendationFeatureProviderProps) {
    const contextValue = useRecommendationFeatureContextValue();

    return (
        <RecommendationFeatureContext.Provider value={contextValue}>
            {children}
        </RecommendationFeatureContext.Provider>
    );
}
