import type {
    EnrichedRegionFeatureCollection,
    EnrichedRegionFeatureProperties,
    RegionFeatureCollection,
} from "@/models/region.model";
import type { RecommendationItemDto } from "@/models/recommendation.models";
import type { SelectedForRecommendationStatusType } from "@/features/recommendation/context/handlers/useRecommendationMapState";

export type MapInteractionMode = "browse" | "selecting-for-recommendation";

export type SetMode = "add" | "remove";

export interface MapSelectionForRecommendationProps {
    selectionMode: MapInteractionMode;
    setSelectionMode: (mode: MapInteractionMode) => void;

    regionSelectedForRecommendationStatus: Map<string, SelectedForRecommendationStatusType>;

    setRegionSelectedForRecommendationStatus: (ids: string[], status: SelectedForRecommendationStatusType) => void;

    addRegionsToDraftSelection: (ids: string[]) => void;
    moveDraftSelectionToIncluded: () => void;
    moveDraftSelectionToExcluded: () => void;
    clearDraftSelectedRegionIds: () => void;
}

export interface MapCanvasProps {
    enrichedRegions: EnrichedRegionFeatureCollection;
    selectedRegionId: string | null;
    onSelectRegion: (regionId: string | null) => void;
    focusedRegionId: string | null;

    selectionForRecommendationProps: MapSelectionForRecommendationProps;
}

export interface MapProps {
    regions: RegionFeatureCollection;
    recommendations: RecommendationItemDto[];
    selectedRegionId: string | null;
    onSelectRegion: (regionId: string | null) => void;
    focusedRegionId: string | null;

    selectionForRecommendationProps: MapSelectionForRecommendationProps;
}

export interface MapPopupCardProps {
    properties: EnrichedRegionFeatureProperties;
}
