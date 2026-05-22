import "leaflet/dist/leaflet.css";

import { useEffect } from "react";

import { GlobalStyles } from "@mui/material";
import L from "leaflet";
import {
    GeoJSON,
    MapContainer,
    Popup,
    Tooltip,
    useMap,
    useMapEvents,
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
import { MapRankLabel } from "@/components/map/components/MapRankLabel";
import type { EnrichedRegionFeatureProperties } from "@/models/region.model";

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

type MapBackgroundResetSelectionProps = {
    onSelectRegion: (regionId: string | null) => void;
};

function MapBackgroundResetSelection({
    onSelectRegion,
}: MapBackgroundResetSelectionProps) {
    useMapEvents({
        click: (event) => {
            const targetElement = event.originalEvent
                .target as HTMLElement | null;
            if (targetElement == null) {
                return;
            }

            const isCountryPath =
                targetElement.closest(".leaflet-interactive") != null;
            const isPopupOrTooltip =
                targetElement.closest(".leaflet-popup") != null ||
                targetElement.closest(".leaflet-tooltip") != null;

            if (!isCountryPath && !isPopupOrTooltip) {
                onSelectRegion(null);
            }
        },
    });

    return null;
}

type MapFocusHandlerProps = {
    focusedRegionId: string | null;
    enrichedRegions: MapCanvasProps["enrichedRegions"];
};

function MapFocusHandler({
    focusedRegionId,
    enrichedRegions,
}: MapFocusHandlerProps) {
    const map = useMap();

    useEffect(() => {
        if (focusedRegionId == null) {
            return;
        }

        const feature = enrichedRegions.features.find(
            (f) => f.properties.u_name === focusedRegionId,
        );

        if (feature == null) {
            return;
        }

        const leafletGeoJson = L.geoJSON(feature);
        const bounds = leafletGeoJson.getBounds();

        if (bounds.isValid()) {
            map.fitBounds(bounds, {
                padding: [40, 40],
                maxZoom: 5,
            });
        }
    }, [enrichedRegions.features, focusedRegionId, map]);

    return null;
}

export function MapCanvas({
    enrichedRegions,
    selectedRegionId,
    onSelectRegion,
    focusedRegionId,
    rankingConfig,
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
                <MapBackgroundResetSelection onSelectRegion={onSelectRegion} />
                <MapFocusHandler
                    focusedRegionId={focusedRegionId}
                    enrichedRegions={enrichedRegions}
                />
                {enrichedRegions.features.map((feature) => {
                    const regionId = feature.properties.u_name;
                    const isSelected = selectedRegionId === regionId;

                    return (
                        <GeoJSON
                            key={regionId}
                            data={feature}
                            style={{
                                fillOpacity: isSelected ? 0.9 : 1,
                                fillColor: getFillColor(
                                    feature.properties,
                                    rankingConfig,
                                    colorScale,
                                ),
                                color: isSelected
                                    ? MAP_COLORS.selectedBorder
                                    : MAP_COLORS.defaultBorder,
                                weight: isSelected ? 3 : 1,
                            }}
                            eventHandlers={{
                                dblclick: (event) => {
                                    event.target.bringToFront?.();
                                    onSelectRegion(regionId);
                                },
                                click: (event) => {
                                    event.target.bringToFront?.();
                                    onSelectRegion(regionId);
                                },
                            }}
                        >
                            {feature.properties.rank != null &&
                                feature.properties.rank <= rankingConfig.topN &&
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
                            <Popup>
                                <MapPopupCard properties={feature.properties} />
                            </Popup>
                        </GeoJSON>
                    );
                })}
            </MapContainer>
            <MapLegend />
        </>
    );
}
