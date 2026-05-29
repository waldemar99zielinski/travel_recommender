import { useState } from "react";

import L from "leaflet";
import { Rectangle, useMapEvents } from "react-leaflet";

import type { MapCanvasProps } from "@/components/map/Map.interfaces";

interface MapSelectionBoxProps {
    enrichedRegions: MapCanvasProps["enrichedRegions"];
    onSelectionComplete: (selectedRegionIds: string[]) => void;
}

export function MapSelectionBox({
    enrichedRegions,
    onSelectionComplete,
}: MapSelectionBoxProps) {
    const [startPoint, setStartPoint] = useState<L.LatLng | null>(null);
    const [currentPoint, setCurrentPoint] = useState<L.LatLng | null>(null);

    useMapEvents({
        mousedown: (e) => {
            // Skip if the click originated on a GeoJSON polygon — those are
            // handled by the individual region click handler. Checking for
            // leaflet-interactive catches all interactive vector layers.
            if (
                e.originalEvent?.target != null &&
                (e.originalEvent.target as HTMLElement).classList?.contains("leaflet-interactive")
            ) {
                return;
            }
            setStartPoint(e.latlng);
            setCurrentPoint(e.latlng);
        },
        mousemove: (e) => {
            if (startPoint == null) return;
            setCurrentPoint(e.latlng);
        },
        mouseup: (e) => {
            if (startPoint == null) return;

            const distance = startPoint.distanceTo(e.latlng);
            if (distance < 10) {
                setStartPoint(null);
                setCurrentPoint(null);
                return;
            }

            const bounds = L.latLngBounds(startPoint, e.latlng);
            if (!bounds.isValid()) {
                setStartPoint(null);
                setCurrentPoint(null);
                return;
            }

            const intersectingIds: string[] = [];
            enrichedRegions.features.forEach((feature) => {
                const featureBounds = L.geoJSON(feature).getBounds();
                if (bounds.intersects(featureBounds)) {
                    intersectingIds.push(feature.properties.u_name);
                }
            });

            setStartPoint(null);
            setCurrentPoint(null);
            onSelectionComplete(intersectingIds);
        },
    });

    if (startPoint == null || currentPoint == null) return null;

    const boxBounds = L.latLngBounds(startPoint, currentPoint);

    return (
        <Rectangle
            bounds={boxBounds}
            pathOptions={{
                color: "#1976d2",
                weight: 2,
                fillColor: "#1976d2",
                fillOpacity: 0.1,
                dashArray: "5 5",
            }}
        />
    );
}
