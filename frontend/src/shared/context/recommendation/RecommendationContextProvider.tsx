import type { ReactNode } from "react";

import { RecommendationContext } from "@/shared/context/recommendation/recommendationContext";
import { useRecommendationContextValue } from "@/shared/context/recommendation/useRecommendationContextValue";

type RecommendationContextProviderProps = {
    children: ReactNode;
};

export function RecommendationContextProvider({ children }: RecommendationContextProviderProps) {
    const contextValue = useRecommendationContextValue();

    return (
        <RecommendationContext.Provider value={contextValue}>
            {children}
        </RecommendationContext.Provider>
    );
}
