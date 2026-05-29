import type { MapCanvasProps } from "@/components/map/Map.interfaces";
import { MapInteractionLock } from "@/components/map/components/MapInteractionLock";
import { MapSelectionBox } from "@/components/map/components/MapSelectionBox";

interface MapSelectionModeEffectsProps {
    enrichedRegions: MapCanvasProps["enrichedRegions"];
    selectionForRecommendationProps: MapCanvasProps["selectionForRecommendationProps"];
}

export function MapSelectionModeEffects({
    enrichedRegions,
    selectionForRecommendationProps,
}: MapSelectionModeEffectsProps) {
    const isSelectionMode =
        selectionForRecommendationProps.selectionMode ===
        "selecting-for-recommendation";

    return (
        <>
            <MapInteractionLock draggingDisabled={isSelectionMode} />
            {isSelectionMode && (
                <MapSelectionBox
                    enrichedRegions={enrichedRegions}
                    onSelectionComplete={(selectedRegionIds: string[]) => {
                        selectionForRecommendationProps.addRegionsToDraftSelection(
                            selectedRegionIds,
                        );
                    }}
                />
            )}
        </>
    );
}
