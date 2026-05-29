import { GlobalStyles } from "@mui/material";

import type { MapInteractionMode } from "@/components/map/Map.interfaces";

interface MapCursorModeStylesProps {
    selectionMode: MapInteractionMode;
}

export function MapCursorModeStyles({
    selectionMode,
}: MapCursorModeStylesProps) {
    if (selectionMode !== "selecting-for-recommendation") {
        return null;
    }

    return (
        <GlobalStyles
            styles={{
                ".map-canvas": {
                    cursor: "crosshair",
                },
                ".map-canvas .leaflet-interactive": {
                    cursor: "crosshair",
                },
            }}
        />
    );
}
