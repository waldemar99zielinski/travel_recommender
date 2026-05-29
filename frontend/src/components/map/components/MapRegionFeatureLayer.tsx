import { GeoJSON, Popup, Tooltip } from "react-leaflet";

import type { MapCanvasProps } from "@/components/map/Map.interfaces";
import { MapPopupCard } from "@/components/map/components/MapPopupCard";
import { MapRankLabel } from "@/components/map/components/MapRankLabel";
import {
    getMapRegionStyle,
    shouldShowMapRegionRankLabel,
} from "@/components/map/model/mapRegionPresentation";

interface MapRegionFeatureLayerProps {
    feature: MapCanvasProps["enrichedRegions"]["features"][number];
    colorScale: (score: number) => string;
    rankingConfig: MapCanvasProps["rankingConfig"];
    selectionForRecommendationProps: MapCanvasProps["selectionForRecommendationProps"];
    onSelectRegion: MapCanvasProps["onSelectRegion"];
}

export function MapRegionFeatureLayer({
    feature,
    colorScale,
    rankingConfig,
    selectionForRecommendationProps,
    onSelectRegion,
}: MapRegionFeatureLayerProps) {
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

    const regionStyle = getMapRegionStyle(
        feature.properties,
        regionStatus,
        rankingConfig,
        colorScale,
    );
    const showRankLabel = shouldShowMapRegionRankLabel(
        feature.properties,
        rankingConfig.topN,
    );
    const showPopup = selectionForRecommendationProps.selectionMode === "browse";

    return (
        <GeoJSON
            key={regionId}
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
                    <MapRankLabel
                        rank={feature.properties.rank!}
                        score={feature.properties.recommendation!.score}
                        mode={rankingConfig.labelMode}
                    />
                </Tooltip>
            )}
            {showPopup && (
                <Popup>
                    <MapPopupCard properties={feature.properties} />
                </Popup>
            )}
        </GeoJSON>
    );
}
