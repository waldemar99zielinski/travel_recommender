import { useEffect, useRef } from "react";

import L from "leaflet";
import { GeoJSON, Tooltip } from "react-leaflet";

import type { MapCanvasProps } from "@/components/map/Map.interfaces";
import { MapRankLabel } from "@/components/map/components/MapRankLabel";
import {
    getMapRegionStyle,
} from "@/components/map/model/mapRegionPresentation";

interface MapRegionFeatureLayerProps {
    feature: MapCanvasProps["enrichedRegions"]["features"][number];
    selectionForRecommendationProps: MapCanvasProps["selectionForRecommendationProps"];
    onSelectRegion: MapCanvasProps["onSelectRegion"];
    selectedRegionId: MapCanvasProps["selectedRegionId"];
}

export function MapRegionFeatureLayer({
    feature,
    selectionForRecommendationProps,
    onSelectRegion,
    selectedRegionId,
}: MapRegionFeatureLayerProps) {
    const layerRef = useRef<L.GeoJSON | null>(null);
    const regionId = feature.properties.u_name;
    const regionStatus =
        selectionForRecommendationProps.regionSelectedForRecommendationStatus.get(
            regionId,
        );

    if (!regionStatus) {
        throw new Error(
            `MapCanvas region status not found for regionId: ${regionId}`,
        );
    }

    const isSelected = selectedRegionId === regionId;

    const regionStyle = getMapRegionStyle(
        feature.properties,
        regionStatus,
        isSelected,
    );
    const showRankLabel =
        feature.properties.recommendation != null && feature.properties.rank != null;

    useEffect(() => {
        if (!isSelected) {
            return;
        }

        layerRef.current?.bringToFront();
    }, [isSelected]);

    return (
        <GeoJSON
            key={regionId}
            ref={layerRef}
            data={feature}
            style={{
                fillOpacity: regionStyle.fillOpacity,
                fillColor: regionStyle.fillColor,
                color: regionStyle.borderColor,
                weight: regionStyle.borderWeight,
            }}
            eventHandlers={{
                click: (leafletEvent) => {
                    if (
                        selectionForRecommendationProps.selectionMode ===
                        "selecting-for-recommendation"
                    ) {
                        if (
                            selectionForRecommendationProps.regionSelectedForRecommendationStatus.get(
                                regionId,
                            ) === "draft"
                        ) {
                            selectionForRecommendationProps.setRegionSelectedForRecommendationStatus(
                                [regionId],
                                "unset",
                            );
                        } else {
                            selectionForRecommendationProps.setRegionSelectedForRecommendationStatus(
                                [regionId],
                                "draft",
                            );
                        }
                    } else {
                        leafletEvent.target.bringToFront?.();
                        onSelectRegion(regionId);
                    }
                },
            }}
        >
            {showRankLabel && (
                <Tooltip permanent direction="center" opacity={1}>
                    <MapRankLabel rank={feature.properties.rank!} mode="rank" />
                </Tooltip>
            )}
        </GeoJSON>
    );
}
