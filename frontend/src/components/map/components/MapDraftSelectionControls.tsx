import type { MapCanvasProps } from "@/components/map/Map.interfaces";
import { DraftSelectionMenu } from "@/components/map/components/DraftSelectionMenu";

interface MapDraftSelectionControlsProps {
    selectionForRecommendationProps: MapCanvasProps["selectionForRecommendationProps"];
}

export function MapDraftSelectionControls({
    selectionForRecommendationProps,
}: MapDraftSelectionControlsProps) {
    if (
        selectionForRecommendationProps.selectionMode !==
        "selecting-for-recommendation"
    ) {
        return null;
    }

    return (
        <DraftSelectionMenu
            regionSelectedForRecommendationStatus={
                selectionForRecommendationProps.regionSelectedForRecommendationStatus
            }
            onInclude={selectionForRecommendationProps.moveDraftSelectionToIncluded}
            onExclude={selectionForRecommendationProps.moveDraftSelectionToExcluded}
            onClear={selectionForRecommendationProps.clearDraftSelectedRegionIds}
            onExitSelectionMode={() => {
                selectionForRecommendationProps.clearDraftSelectedRegionIds();
                selectionForRecommendationProps.setSelectionMode("browse");
            }}
        />
    );
}
