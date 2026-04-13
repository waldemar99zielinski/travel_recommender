import type { ReactNode } from "react";

import {
    RecommendationContext,
    type RecommendationContextValue,
} from "@/shared/context/recommendation/recommendationContext";
import { useRecommendationContextValue } from "@/shared/context/recommendation/useRecommendationContextValue";

type RecommendationContextProviderProps = {
    children: ReactNode;
    value?: RecommendationContextValue;
};

export function RecommendationContextProvider({
    children,
    value,
}: RecommendationContextProviderProps) {
    const internalValue = useRecommendationContextValue();

    return (
        <RecommendationContext.Provider value={value ?? internalValue}>
            {children}
        </RecommendationContext.Provider>
    );
}
