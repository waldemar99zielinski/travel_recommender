import "leaflet/dist/leaflet.css";

import {
    GlobalStyles,
} from "@mui/material";
import {
    GeoJSON,
    MapContainer,
    Popup,
    Tooltip,
} from "react-leaflet";

import type { MapCanvasProps } from "@/components/map/Map.interfaces";
import {
    createRelativeScoreColorScale,
    normalizedScoreToColor,
} from "@/components/map/model/mapColors";
import {
    MAP_BOUNDS,
    MAP_CENTER,
    MAP_COLORS,
} from "@/components/map/map.config";
import { MapLegend } from "@/components/map/components/MapLegend";
import { MapPopupCard } from "@/components/map/components/MapPopupCard";

import { DraftSelectionMenu } from "@/components/map/components/DraftSelectionMenu";
import { MapRankLabel } from "@/components/map/components/MapRankLabel";
import type { EnrichedRegionFeatureProperties } from "@/models/region.model";
import { MapInteractionLock } from "@/components/map/components/MapInteractionLock";
import { MapSelectionBox } from "@/components/map/components/MapSelectionBox";
import { MapFocusHandler } from "@/components/map/components/MapFocusHandler";

function getFillColor(
    properties: EnrichedRegionFeatureProperties,
    rankingConfig: MapCanvasProps["rankingConfig"],
    colorScale: (score: number) => string,
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

export function MapCanvas({
    enrichedRegions,
    onSelectRegion,
    focusedRegionId,
    rankingConfig,
    selectionForRecommendationProps,
}: MapCanvasProps) {
    const colorScale = createRelativeScoreColorScale(
        enrichedRegions.features
            .map((feature) => feature.properties.recommendation?.score)
            .filter((score): score is number => score != null),
    );

    return (
        <>
            <GlobalStyles
                styles={{
                    ".leaflet-container": {
                        height: "100%",
                        width: "100%",
                        background: MAP_COLORS.background,
                    },
                    ".leaflet-popup-content-wrapper, .leaflet-popup-tip": {
                        borderRadius: 10,
                    },
                    ".leaflet-tooltip": {
                        background: "transparent",
                        border: "none",
                        boxShadow: "none",
                    },
                    ".leaflet-top.leaflet-left": {
                        top: 52,
                    },

                }}
            />
            <MapContainer
                center={MAP_CENTER}
                zoom={2}
                maxBounds={MAP_BOUNDS}
                maxBoundsViscosity={1}
                doubleClickZoom={false}
                style={{ height: "100%" }}
            >
                <MapFocusHandler
                    focusedRegionId={focusedRegionId}
                    enrichedRegions={enrichedRegions}
                />
                <MapInteractionLock 
                    draggingDisabled={
                        selectionForRecommendationProps.selectionMode === "selecting-for-recommendation"
                    }
                />
                {selectionForRecommendationProps.selectionMode === "selecting-for-recommendation" && (
                    <MapSelectionBox
                        enrichedRegions={enrichedRegions}
                        onSelectionComplete={(selectedRegionIds: string[]) => {
                            selectionForRecommendationProps.addRegionsToDraftSelection(selectedRegionIds);
                        }}
                    />
                )}
                {enrichedRegions.features.map((feature) => {
                    const regionId = feature.properties.u_name;
                    const regionStatus = selectionForRecommendationProps.regionSelectedForRecommendationStatus.get(regionId);

                    if (!regionStatus) {
                       throw new Error(`MapCanvas region status not found for regionId: ${regionId}`);
                    }

                    let fillColor: string;
                    let borderColor: string;
                    let borderWeight: number;
                    let fillOpacity: number;

                    if (regionStatus === "draft") {
                        fillColor = MAP_COLORS.draftFill;
                        borderColor = "#37474f";
                        borderWeight = 2;
                        fillOpacity = 0.8;
                    } else if (regionStatus === "excluded") {
                        fillColor = MAP_COLORS.excludedFill;
                        borderColor = "#d32f2f";
                        borderWeight = 2;
                        fillOpacity = 0.9;
                    } else if (regionStatus === "included") {
                        fillColor = MAP_COLORS.includedFill;
                        borderColor = "#4caf50";
                        borderWeight = 2;
                        fillOpacity = 0.9;
                    } else {
                        fillColor = getFillColor(
                            feature.properties,
                            rankingConfig,
                            colorScale,
                        );
                        borderColor = MAP_COLORS.defaultBorder;
                        borderWeight = 1;
                        fillOpacity = 1;
                    }

                    return (
                        <GeoJSON
                            key={regionId}
                            data={feature}
                            style={{
                                fillOpacity,
                                fillColor,
                                color: borderColor,
                                weight: borderWeight,
                            }}
                            eventHandlers={{
                                click: (leafletEvent) => {
                                    if (selectionForRecommendationProps.selectionMode === "selecting-for-recommendation") {
                                        if (selectionForRecommendationProps.regionSelectedForRecommendationStatus.get(regionId) === "draft") {
                                            selectionForRecommendationProps.setRegionSelectedForRecommendationStatus([regionId], "unset");
                                        } else {
                                            selectionForRecommendationProps.setRegionSelectedForRecommendationStatus([regionId], "draft");
                                        }
                                    } else {
                                        leafletEvent.target.bringToFront?.();
                                        onSelectRegion(regionId);
                                    }
                                },
                            }}
                        >
                            {feature.properties.rank != null &&
                                feature.properties.rank <=
                                    rankingConfig.topN &&
                                feature.properties.recommendation != null && (
                                    <Tooltip
                                        permanent
                                        direction="center"
                                        opacity={1}
                                    >
                                        <MapRankLabel
                                            rank={feature.properties.rank}
                                            score={
                                                feature.properties
                                                    .recommendation.score
                                            }
                                            mode={rankingConfig.labelMode}
                                        />
                                    </Tooltip>
                                )}
                            {(selectionForRecommendationProps.selectionMode === "browse") && <Popup>
                                <MapPopupCard
                                    properties={feature.properties}
                                />
                            </Popup>}
                        </GeoJSON>
                    );
                })}
            </MapContainer>
            <MapLegend />
            {selectionForRecommendationProps.selectionMode === "selecting-for-recommendation" && 
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
            />}
        </>
    );
}
