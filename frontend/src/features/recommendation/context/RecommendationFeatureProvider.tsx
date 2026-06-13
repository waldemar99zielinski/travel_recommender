import type { ReactNode } from "react";

import {
    RecommendationFeatureContext,
} from "@/features/recommendation/context/recommendationFeatureContext";
import { useRecommendationFeatureContextValue } from "@/features/recommendation/context/useRecommendationFeatureContextValue";
import type { RegionFeatureCollection } from "@/models/region.model";
import { useSessionContext } from "@/shared/context";

type RecommendationFeatureProviderProps = {
    children: ReactNode;
    regions: RegionFeatureCollection,
};

type RecommendationFeatureStateProps = RecommendationFeatureProviderProps;

function RecommendationFeatureState({
    children,
    regions,
}: RecommendationFeatureStateProps) {
    const contextValue = useRecommendationFeatureContextValue(regions);

    return (
        <RecommendationFeatureContext.Provider value={contextValue}>
            {children}
        </RecommendationFeatureContext.Provider>
    );
}

export function RecommendationFeatureProvider({
    children,
    regions,
}: RecommendationFeatureProviderProps) {
    const { session } = useSessionContext();

    return (
        <RecommendationFeatureState
            key={session?.session_id ?? "no-session"}
            regions={regions}
        >
            {children}
        </RecommendationFeatureState>
    );
}
