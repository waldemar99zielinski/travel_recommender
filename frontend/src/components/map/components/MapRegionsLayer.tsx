import type { MapCanvasProps } from "@/components/map/Map.interfaces";
import { MapRegionFeatureLayer } from "@/components/map/components/MapRegionFeatureLayer";
import { createRelativeScoreColorScale } from "@/components/map/model/mapColors";

interface MapRegionsLayerProps {
    enrichedRegions: MapCanvasProps["enrichedRegions"];
    onSelectRegion: MapCanvasProps["onSelectRegion"];
    rankingConfig: MapCanvasProps["rankingConfig"];
    selectionForRecommendationProps: MapCanvasProps["selectionForRecommendationProps"];
}

export function MapRegionsLayer({
    enrichedRegions,
    onSelectRegion,
    rankingConfig,
    selectionForRecommendationProps,
}: MapRegionsLayerProps) {
    const colorScale = createRelativeScoreColorScale(
        enrichedRegions.features
            .map((feature) => feature.properties.recommendation?.score)
            .filter((score): score is number => score != null),
    );

    return enrichedRegions.features.map((feature) => (
        <MapRegionFeatureLayer
            key={feature.properties.u_name}
            feature={feature}
            colorScale={colorScale}
            rankingConfig={rankingConfig}
            selectionForRecommendationProps={selectionForRecommendationProps}
            onSelectRegion={onSelectRegion}
        />
    ));
}
