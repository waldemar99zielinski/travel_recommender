import { type Dispatch, type SetStateAction, useState } from "react";

import { type RegionFeatureCollection } from "@/models/region.model";

export type SelectionMode = "browse" | "selecting-for-recommendation";

export type SelectedForRecommendationStatusType = "draft" | "included" | "excluded" | "unset";

export interface SelectedForRecommendationRegionStatus {
    regionId: string;
    status: SelectedForRecommendationStatusType;
} 

export interface RegionForRecommendationState {
    selectionMode: SelectionMode;
    setSelectionMode: (mode: SelectionMode) => void;

    regionSelectedForRecommendationStatus: Map<string, SelectedForRecommendationStatusType>;
    setRegionSelectedForRecommendationStatus: (ids: string[], status: SelectedForRecommendationStatusType) => void;
    replaceResolvedRegionFilterStatuses: (
        includedIds: string[],
        excludedIds: string[],
    ) => void;

    addRegionsToDraftSelection: (ids: string[]) => void;
    moveDraftSelectionToIncluded: () => void;
    moveDraftSelectionToExcluded: () => void;
    clearDraftSelectedRegionIds: () => void;
    clearAllSelectedRegionIds: () => void;
}

export interface UseRecommendationMapStateReturn {
    selectedRegionId: string | null;
    setSelectedRegionId: Dispatch<SetStateAction<string | null>>;
    focusedRegionId: string | null;
    setFocusedRegionId: Dispatch<SetStateAction<string | null>>;
    regionForRecommendationSelection: RegionForRecommendationState;
}

export function useRecommendationMapState(
    regions: RegionFeatureCollection,
): UseRecommendationMapStateReturn {
    const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);
    const [focusedRegionId, setFocusedRegionId] = useState<string | null>(null);
    const [selectionMode, _setSelectionMode] = useState<SelectionMode>("browse");
    const [
        regionSelectedForRecommendationStatus,
        setRegionsSelectedForRecommendationStatus
    ] = useState<Map<string, SelectedForRecommendationStatusType>>(() => {
        const initialMapStatus = new Map<string, SelectedForRecommendationStatusType>();

        regions.features.forEach((feature) => {
            const regionId = feature.properties.u_name;
            initialMapStatus.set(regionId, "unset");
        });

        return initialMapStatus;
    });

    const setSelectionMode = (mode: SelectionMode) => {
        if (mode === "browse") {
            clearDraftSelectedRegionIds();
        }
        _setSelectionMode(mode);
    };

    const setRegionSelectedForRecommendationStatus = (
        ids: string[],
        status: SelectedForRecommendationStatusType
    ) => {
        setRegionsSelectedForRecommendationStatus((prev) => {
            const newMap = new Map(prev);

            ids.forEach((id) => {
                newMap.set(id, status);
            });

            return newMap;
        });
    };

    const replaceResolvedRegionFilterStatuses = (
        includedIds: string[],
        excludedIds: string[],
    ) => {
        setRegionsSelectedForRecommendationStatus((prev) => {
            const newMap = new Map(prev);

            newMap.forEach((status, regionId) => {
                if (status === "included" || status === "excluded") {
                    newMap.set(regionId, "unset");
                }
            });

            includedIds.forEach((id) => {
                newMap.set(id, "included");
            });

            excludedIds.forEach((id) => {
                newMap.set(id, "excluded");
            });

            return newMap;
        });
    };

    const addRegionsToDraftSelection = (ids: string[]) => {
        setRegionsSelectedForRecommendationStatus((prev) => {
            const newMap = new Map(prev);
            
            ids.forEach((id) => {
                newMap.set(id, "draft");
            });

            return newMap;
        });
    }

    const moveDraftSelectionToIncluded = () => {
        setRegionsSelectedForRecommendationStatus((prev) => {
            const newMap = new Map(prev);
            
            newMap.forEach((status, regionId) => {
                if (status === "draft") {
                    newMap.set(regionId, "included");
                }
            });

            return newMap;
        });
    };

    const moveDraftSelectionToExcluded = () => {
        setRegionsSelectedForRecommendationStatus((prev) => {
            const newMap = new Map(prev);
            
            newMap.forEach((status, regionId) => {
                if (status === "draft") {
                    newMap.set(regionId, "excluded");
                }
            });

            return newMap;
        });
    };

    const clearDraftSelectedRegionIds = () => {
        setRegionsSelectedForRecommendationStatus((prev) => {
            const newMap = new Map(prev);

            newMap.forEach((status, regionId) => {
                if (status === "draft") {
                    newMap.set(regionId, "unset");
                }
            });

            return newMap;
        });
    };

    const clearAllSelectedRegionIds = () => {
        setRegionsSelectedForRecommendationStatus((prev) => {
            const newMap = new Map(prev);
            
            newMap.forEach((_, regionId) => {
                newMap.set(regionId, "unset");
            }
            );
            
            return newMap;
        });
    };

    return {
        selectedRegionId,
        setSelectedRegionId,
        focusedRegionId,
        setFocusedRegionId,
        regionForRecommendationSelection: {
            selectionMode,
            setSelectionMode,
            regionSelectedForRecommendationStatus,
            setRegionSelectedForRecommendationStatus,
            replaceResolvedRegionFilterStatuses,
            addRegionsToDraftSelection,
            moveDraftSelectionToIncluded,
            moveDraftSelectionToExcluded,
            clearDraftSelectedRegionIds,
            clearAllSelectedRegionIds,
        },
    };
}
