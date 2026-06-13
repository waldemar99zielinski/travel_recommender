import { MAP_COLORS } from "@/components/map/map.config";
import type { EnrichedRegionFeatureProperties } from "@/models/region.model";
import type { SelectedForRecommendationStatusType } from "@/features/recommendation/context/handlers/useRecommendationMapState";

export interface MapRegionStyle {
    fillColor: string;
    borderColor: string;
    borderWeight: number;
    fillOpacity: number;
}

function getRegionFillColor(
    properties: EnrichedRegionFeatureProperties,
): string {
    if (properties.recommendation == null) {
        return MAP_COLORS.noRecommendationFill;
    }

    return MAP_COLORS.recommendedFill;
}

function hasRecommendation(properties: EnrichedRegionFeatureProperties): boolean {
    return properties.recommendation != null;
}

export function getMapRegionStyle(
    properties: EnrichedRegionFeatureProperties,
    regionStatus: SelectedForRecommendationStatusType,
    isSelected: boolean = false,
): MapRegionStyle {
    let style: MapRegionStyle;

    if (regionStatus === "draft") {
        style = {
            fillColor: MAP_COLORS.draftFill,
            borderColor: "#37474f",
            borderWeight: 2,
            fillOpacity: 0.8,
        };
    } else if (regionStatus === "excluded") {
        style = {
            fillColor: hasRecommendation(properties)
                ? MAP_COLORS.recommendedFill
                : MAP_COLORS.excludedFill,
            borderColor: "#d32f2f",
            borderWeight: 2,
            fillOpacity: 0.9,
        };
    } else if (regionStatus === "included") {
        style = {
            fillColor: hasRecommendation(properties)
                ? MAP_COLORS.recommendedFill
                : MAP_COLORS.includedFill,
            borderColor: "#4caf50",
            borderWeight: 2,
            fillOpacity: 0.9,
        };
    } else {
        style = {
            fillColor: getRegionFillColor(properties),
            borderColor: MAP_COLORS.defaultBorder,
            borderWeight: 1,
            fillOpacity: properties.recommendation == null ? 0.65 : 0.9,
        };
    }

    if (!isSelected) {
        return style;
    }

    return {
        ...style,
        borderColor: MAP_COLORS.selectedBorder,
        borderWeight: 3,
    };
}
