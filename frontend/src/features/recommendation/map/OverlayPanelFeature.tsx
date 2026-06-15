import { useCallback } from "react";

import { OverlayPanel } from "@/components/overlay/OverlayPanel";
import { RegionDetailContent } from "@/components/overlay/content/RegionDetailContent";
import { normalizeRegionId } from "@/components/map/model/mapSelectors";
import { useRecommendationFeatureContext } from "@/features/recommendation/context/useRecommendationFeatureContext";
import {
    getLatestTurnWithRecommendations,
    hasRecommendations,
} from "@/models/chat.models";

const DEFAULT_DESTINATION_RESEARCH_LOADING_DURATION_MS = 30_000;

export function OverlayPanelFeature() {
    const {
        regions,
        chatState: {
            chatRecords,
            onGoingChatTurn,
            destinationResearchRegionIds,
        },
        mapState: { selectedRegionId, setSelectedRegionId },
    } = useRecommendationFeatureContext();

    const currentAssistantTurn = onGoingChatTurn ?? chatRecords.at(-1) ?? null;
    const recommendationSourceTurn = hasRecommendations(currentAssistantTurn)
        ? currentAssistantTurn
        : getLatestTurnWithRecommendations(chatRecords);

    const normalizedSelectedId =
        selectedRegionId != null ? normalizeRegionId(selectedRegionId) : null;
    const selectedRegion =
        normalizedSelectedId == null
            ? null
            : regions.features.find(
                  (feature) =>
                      normalizeRegionId(feature.properties.u_name) === normalizedSelectedId,
              ) ?? null;

    const selectedDestinationResearch =
        normalizedSelectedId == null || recommendationSourceTurn == null
            ? null
            : recommendationSourceTurn.travel_destinations_evaluations?.find(
                  (evaluation) =>
                      normalizeRegionId(evaluation.region_id) === normalizedSelectedId,
              ) ?? null;
    const isDestinationResearchRequestedForSelectedRegion =
        normalizedSelectedId != null &&
        destinationResearchRegionIds.some(
            (regionId) => normalizeRegionId(regionId) === normalizedSelectedId,
        );

    const isDestinationResearchLoading =
        selectedRegionId != null &&
        selectedDestinationResearch == null &&
        onGoingChatTurn != null &&
        isDestinationResearchRequestedForSelectedRegion;
    const overlayPanel =
        selectedRegionId == null
            ? null
            : {
                  title: selectedRegion?.properties.display_name ?? selectedRegionId,
                  type: "region-detail" as const,
                  data: {
                      id: selectedRegionId,
                      name: selectedRegion?.properties.display_name,
                      recommendation: undefined,
                  },
              };

    const handleOverlayClose = useCallback(() => {
        setSelectedRegionId(null);
    }, [setSelectedRegionId]);

    return (
        <OverlayPanel
            title={overlayPanel?.title ?? ""}
            open={overlayPanel != null}
            onClose={handleOverlayClose}
        >
            {overlayPanel?.type === "region-detail" && (
                <RegionDetailContent
                    regionId={overlayPanel.data.id}
                    regionName={overlayPanel.data.name}
                    recommendation={overlayPanel.data.recommendation}
                    destinationResearch={selectedDestinationResearch}
                    isDestinationResearchLoading={isDestinationResearchLoading}
                    destinationResearchLoadingDurationMs={
                        DEFAULT_DESTINATION_RESEARCH_LOADING_DURATION_MS
                    }
                />
            )}
        </OverlayPanel>
    );
}
