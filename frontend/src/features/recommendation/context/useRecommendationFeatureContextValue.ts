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

    const setIncludedRegionIds = useCallback(
        (ids: string[]) => {
            mapState.regionForRecommendationSelection.setRegionSelectedForRecommendationStatus(
                ids,
                "included",
            );
        },
        [mapState.regionForRecommendationSelection],
    );
    const setExcludedRegionIds = useCallback(
        (ids: string[]) => {
            mapState.regionForRecommendationSelection.setRegionSelectedForRecommendationStatus(
                ids,
                "excluded",
            );
        },
        [mapState.regionForRecommendationSelection],
    );

    const chatState = useRecommendationChat({
        setIncludedRegionIds,
        setExcludedRegionIds,
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
