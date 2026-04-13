import { useContext } from "react";

import { RecommendationContext } from "@/shared/context/recommendation/recommendationContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "useRecommendationContext" });

export function useRecommendationContext() {
    const context = useContext(RecommendationContext);

    if (context == null) {
        logger.error("RecommendationContext is missing in component tree");
        throw new Error(
            "useRecommendationContext must be used within RecommendationContextProvider",
        );
    }

    return context;
}
