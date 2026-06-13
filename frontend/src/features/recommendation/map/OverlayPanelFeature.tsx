import { useCallback } from "react";

import { OverlayPanel } from "@/components/overlay/OverlayPanel";
import { RegionDetailContent } from "@/components/overlay/content/RegionDetailContent";
import { normalizeRegionId } from "@/components/map/model/mapSelectors";
import { useRecommendationFeatureContext } from "@/features/recommendation/context/useRecommendationFeatureContext";

const DEFAULT_DESTINATION_RESEARCH_LOADING_DURATION_MS = 30_000;

export function OverlayPanelFeature() {
    const {
        regions,
        chatState: { chatRecords, onGoingChatTurn, destinationResearchStarted },
        mapState: { selectedRegionId, setSelectedRegionId },
    } = useRecommendationFeatureContext();

    const latestChatTurn = onGoingChatTurn ?? chatRecords.at(-1) ?? null;

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
        normalizedSelectedId == null || latestChatTurn == null
            ? null
            : latestChatTurn.travel_destinations_evaluations?.find(
                  (evaluation) =>
                      normalizeRegionId(evaluation.region_id) === normalizedSelectedId,
              ) ?? null;

    const isDestinationResearchLoading =
        selectedRegionId != null &&
        selectedDestinationResearch == null &&
        onGoingChatTurn != null &&
        destinationResearchStarted;
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
