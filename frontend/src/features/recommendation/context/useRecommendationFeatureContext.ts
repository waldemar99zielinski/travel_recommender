import { useContext } from "react";

import {
    RecommendationFeatureContext,
} from "@/features/recommendation/context/recommendationFeatureContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "useRecommendationFeatureContext" });

export function useRecommendationFeatureContext() {
    const context = useContext(RecommendationFeatureContext);

    if (context == null) {
        logger.error("RecommendationFeatureContext is missing in component tree");
        throw new Error(
            "useRecommendationFeatureContext must be used within RecommendationFeatureProvider",
        );
    }

    return context;
}
