import { useCallback } from "react";

import type { RegionFeatureCollection } from "@/models/region.model";
import type { RecommendationFeatureContextValue } from "@/features/recommendation/context/recommendationFeatureContext";

import { useRecommendationMapState } from "./handlers/useRecommendationMapState";
import { useRecommendationChat } from "./handlers/useRecommendationChat";
import { useRecommendationSession } from "./handlers/useRecommendationSession";

export function useRecommendationFeatureContextValue(
    regions: RegionFeatureCollection,
): RecommendationFeatureContextValue {
    const mapState = useRecommendationMapState(regions);

    const applyResolvedRegionFilters = useCallback(
        (includedIds: string[], excludedIds: string[]) => {
            mapState.regionForRecommendationSelection.replaceResolvedRegionFilterStatuses(
                includedIds,
                excludedIds,
            );
        },
        [mapState.regionForRecommendationSelection],
    );

    const chatState = useRecommendationChat({
        applyResolvedRegionFilters,
    });
    const sessionState = useRecommendationSession();

    return {
        regions,
        mapState,
        chatState,
        sessionState,
        overlayPanel: null,
    };
}
