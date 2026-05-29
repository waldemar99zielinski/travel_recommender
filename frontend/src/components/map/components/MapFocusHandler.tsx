import { useEffect } from "react";

import L from "leaflet";
import { useMap } from "react-leaflet";

import type { MapCanvasProps } from "@/components/map/Map.interfaces";

interface MapFocusHandlerProps {
    focusedRegionId: string | null;
    enrichedRegions: MapCanvasProps["enrichedRegions"];
}

export function MapFocusHandler({
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
