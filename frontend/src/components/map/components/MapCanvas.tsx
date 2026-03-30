import "leaflet/dist/leaflet.css";

import { GlobalStyles } from "@mui/material";
import {
    GeoJSON,
    MapContainer,
    Popup,
    Tooltip,
    useMapEvents,
} from "react-leaflet";

import type { MapCanvasProps } from "@/components/map/Map.interfaces";
import { scoreToColor } from "@/components/map/model/mapColors";
import { MapLegend } from "@/components/map/components/MapLegend";
import { MapPopupCard } from "@/components/map/components/MapPopupCard";
import { MapRankLabel } from "@/components/map/components/MapRankLabel";
import type { EnrichedRegionFeatureProperties } from "@/models/destination/model/types";

const MAP_CENTER: [number, number] = [20.3, 5.96];
const MAP_BOUNDS: [[number, number], [number, number]] = [
    [-85, -180],
    [85, 180],
];

function getFillColor(
    properties: EnrichedRegionFeatureProperties,
    rankingConfig: MapCanvasProps["rankingConfig"],
): string {
    if (properties.recommendation == null) {
        return "#cfdae5";
    }

    if (
        rankingConfig.forceTopColor &&
        properties.rank != null &&
        properties.rank <= rankingConfig.topN
    ) {
        return scoreToColor(100);
    }

    return scoreToColor(properties.recommendation.score);
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

export function MapCanvas({
    enrichedRegions,
    selectedRegionId,
    onSelectRegion,
    rankingConfig,
}: MapCanvasProps) {
    return (
        <>
            <GlobalStyles
                styles={{
                    ".leaflet-container": {
                        height: "100%",
                        width: "100%",
                        background: "#a3ceff",
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
                                ),
                                color: isSelected ? "#ffffff" : "#868686",
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
