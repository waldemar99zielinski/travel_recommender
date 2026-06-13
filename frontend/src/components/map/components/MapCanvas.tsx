import "leaflet/dist/leaflet.css";

import {
    MapContainer,
} from "react-leaflet";

import type { MapCanvasProps } from "@/components/map/Map.interfaces";
import {
    MAP_BOUNDS,
    MAP_CENTER,
} from "@/components/map/map.config";
import { MapCanvasGlobalStyles } from "@/components/map/components/MapCanvasGlobalStyles";
import { MapCursorModeStyles } from "@/components/map/components/MapCursorModeStyles";
import { MapDraftSelectionControls } from "@/components/map/components/MapDraftSelectionControls";
import { MapLegend } from "@/components/map/components/MapLegend";

import { MapFocusHandler } from "@/components/map/components/MapFocusHandler";
import { MapRegionsLayer } from "@/components/map/components/MapRegionsLayer";
import { MapSelectionModeEffects } from "@/components/map/components/MapSelectionModeEffects";

export function MapCanvas({
    enrichedRegions,
    selectedRegionId,
    onSelectRegion,
    focusedRegionId,
    selectionForRecommendationProps,
}: MapCanvasProps) {
    return (
        <>
            <MapCanvasGlobalStyles />
            <MapCursorModeStyles
                selectionMode={selectionForRecommendationProps.selectionMode}
            />
            <MapContainer
                className="map-canvas"
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
                <MapSelectionModeEffects
                    enrichedRegions={enrichedRegions}
                    selectionForRecommendationProps={selectionForRecommendationProps}
                />
                <MapRegionsLayer
                    enrichedRegions={enrichedRegions}
                    selectedRegionId={selectedRegionId}
                    onSelectRegion={onSelectRegion}
                    selectionForRecommendationProps={selectionForRecommendationProps}
                />
            </MapContainer>
            <MapLegend />
            <MapDraftSelectionControls
                selectionForRecommendationProps={selectionForRecommendationProps}
            />
        </>
    );
}
