import { GlobalStyles } from "@mui/material";

import { MAP_COLORS } from "@/components/map/map.config";

export function MapCanvasGlobalStyles() {
    return (
        <GlobalStyles
            styles={{
                ".leaflet-container": {
                    height: "100%",
                    width: "100%",
                    background: MAP_COLORS.background,
                },
                ".leaflet-popup-content-wrapper, .leaflet-popup-tip": {
                    borderRadius: 10,
                },
                ".leaflet-tooltip": {
                    background: "transparent",
                    border: "none",
                    boxShadow: "none",
                },
                ".leaflet-top.leaflet-left": {
                    top: 52,
                },
            }}
        />
    );
}
