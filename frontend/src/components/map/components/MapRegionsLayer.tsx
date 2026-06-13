import type { MapCanvasProps } from "@/components/map/Map.interfaces";
import { MapRegionFeatureLayer } from "@/components/map/components/MapRegionFeatureLayer";

interface MapRegionsLayerProps {
    enrichedRegions: MapCanvasProps["enrichedRegions"];
    selectedRegionId: MapCanvasProps["selectedRegionId"];
    onSelectRegion: MapCanvasProps["onSelectRegion"];
    selectionForRecommendationProps: MapCanvasProps["selectionForRecommendationProps"];
}

export function MapRegionsLayer({
    enrichedRegions,
    selectedRegionId,
    onSelectRegion,
    selectionForRecommendationProps,
}: MapRegionsLayerProps) {
    return enrichedRegions.features.map((feature) => (
        <MapRegionFeatureLayer
            key={feature.properties.u_name}
            feature={feature}
            selectionForRecommendationProps={selectionForRecommendationProps}
            onSelectRegion={onSelectRegion}
            selectedRegionId={selectedRegionId}
        />
    ));
}
