import type { MapCanvasProps } from "@/components/map/Map.interfaces";
import {
    normalizedScoreToColor,
} from "@/components/map/model/mapColors";
import { MAP_COLORS } from "@/components/map/map.config";
import type { EnrichedRegionFeatureProperties } from "@/models/region.model";
import type { SelectedForRecommendationStatusType } from "@/features/recommendation/context/handlers/useRecommendationMapState";

type ColorScale = (score: number) => string;

export interface MapRegionStyle {
    fillColor: string;
    borderColor: string;
    borderWeight: number;
    fillOpacity: number;
}

function getRegionFillColor(
    properties: EnrichedRegionFeatureProperties,
    rankingConfig: MapCanvasProps["rankingConfig"],
    colorScale: ColorScale,
): string {
    if (properties.recommendation == null) {
        return MAP_COLORS.noRecommendationFill;
    }

    if (
        rankingConfig.forceTopColor &&
        properties.rank != null &&
        properties.rank <= rankingConfig.topN
    ) {
        return normalizedScoreToColor(1);
    }

    return colorScale(properties.recommendation.score);
}

export function getMapRegionStyle(
    properties: EnrichedRegionFeatureProperties,
    regionStatus: SelectedForRecommendationStatusType,
    rankingConfig: MapCanvasProps["rankingConfig"],
    colorScale: ColorScale,
): MapRegionStyle {
    if (regionStatus === "draft") {
        return {
            fillColor: MAP_COLORS.draftFill,
            borderColor: "#37474f",
            borderWeight: 2,
            fillOpacity: 0.8,
        };
    }

    if (regionStatus === "excluded") {
        return {
            fillColor: MAP_COLORS.excludedFill,
            borderColor: "#d32f2f",
            borderWeight: 2,
            fillOpacity: 0.9,
        };
    }

    if (regionStatus === "included") {
        return {
            fillColor: MAP_COLORS.includedFill,
            borderColor: "#4caf50",
            borderWeight: 2,
            fillOpacity: 0.9,
        };
    }

    return {
        fillColor: getRegionFillColor(properties, rankingConfig, colorScale),
        borderColor: MAP_COLORS.defaultBorder,
        borderWeight: 1,
        fillOpacity: 1,
    };
}

export function shouldShowMapRegionRankLabel(
    properties: EnrichedRegionFeatureProperties,
    topN: number,
): boolean {
    return (
        properties.rank != null &&
        properties.rank <= topN &&
        properties.recommendation != null
    );
}
