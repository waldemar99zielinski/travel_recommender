import { useRef, useState } from "react";

import booleanIntersects from "@turf/boolean-intersects";
import { polygon } from "@turf/helpers";
import L from "leaflet";
import { Rectangle, useMapEvents } from "react-leaflet";

import type { MapCanvasProps } from "@/components/map/Map.interfaces";

interface MapSelectionBoxProps {
    enrichedRegions: MapCanvasProps["enrichedRegions"];
    onSelectionComplete: (selectedRegionIds: string[]) => void;
}

const DRAG_THRESHOLD_PX = 5;

export function MapSelectionBox({
    enrichedRegions,
    onSelectionComplete,
}: MapSelectionBoxProps) {
    const dragStartLatLngRef = useRef<L.LatLng | null>(null);
    const dragStartContainerPointRef = useRef<L.Point | null>(null);
    const [startPoint, setStartPoint] = useState<L.LatLng | null>(null);
    const [currentPoint, setCurrentPoint] = useState<L.LatLng | null>(null);

    useMapEvents({
        mousedown: (e) => {
            dragStartLatLngRef.current = e.latlng;
            dragStartContainerPointRef.current = e.containerPoint;
            setStartPoint(null);
            setCurrentPoint(null);
        },
        mousemove: (e) => {
            const dragStartLatLng = dragStartLatLngRef.current;
            const dragStartContainerPoint = dragStartContainerPointRef.current;

            if (dragStartLatLng == null || dragStartContainerPoint == null) {
                return;
            }

            if (
                dragStartContainerPoint.distanceTo(e.containerPoint) <
                DRAG_THRESHOLD_PX
            ) {
                return;
            }

            if (startPoint == null) {
                setStartPoint(dragStartLatLng);
            }

            setCurrentPoint(e.latlng);
        },
        mouseup: (e) => {
            const dragStartLatLng = dragStartLatLngRef.current;
            const dragStartContainerPoint = dragStartContainerPointRef.current;

            dragStartLatLngRef.current = null;
            dragStartContainerPointRef.current = null;

            if (dragStartLatLng == null || dragStartContainerPoint == null) {
                return;
            }

            if (
                dragStartContainerPoint.distanceTo(e.containerPoint) <
                DRAG_THRESHOLD_PX
            ) {
                setStartPoint(null);
                setCurrentPoint(null);
                return;
            }

            const bounds = L.latLngBounds(dragStartLatLng, e.latlng);
            if (!bounds.isValid()) {
                setStartPoint(null);
                setCurrentPoint(null);
                return;
            }

            const selectionPolygon = polygon([[
                [bounds.getWest(), bounds.getSouth()],
                [bounds.getEast(), bounds.getSouth()],
                [bounds.getEast(), bounds.getNorth()],
                [bounds.getWest(), bounds.getNorth()],
                [bounds.getWest(), bounds.getSouth()],
            ]]);

            const intersectingIds = enrichedRegions.features
                .filter((feature) => booleanIntersects(selectionPolygon, feature))
                .map((feature) => feature.properties.u_name);

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
