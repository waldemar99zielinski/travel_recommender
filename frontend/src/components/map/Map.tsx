import { useMemo } from "react";

import { Box } from "@mui/material";

import type { MapProps } from "@/components/map/Map.interfaces";
import { MapCanvas } from "@/components/map/components/MapCanvas";
import { MapModeSelector } from "@/components/map/components/MapModeSelector";
import { enrichRegions } from "@/components/map/model/mapSelectors";

export function Map({
    regions,
    recommendations,
    selectedRegionId,
    onSelectRegion,
    focusedRegionId,
    rankingConfig,
    selectionForRecommendationProps,
}: MapProps) {
    const resolvedRankingConfig = {
        topN: rankingConfig?.topN ?? 10,
        labelMode: rankingConfig?.labelMode ?? "score",
        forceTopColor: rankingConfig?.forceTopColor ?? false,
    };

    const enrichedRegions = useMemo(
        () => enrichRegions(regions, recommendations),
        [regions, recommendations],
    );

    return (
        <Box
            sx={{
                position: "relative",
                flex: 1,
                minHeight: { xs: 420, lg: "100%" },
                borderRadius: 2,
                overflow: "hidden",
            }}
        >
            <MapCanvas
                enrichedRegions={enrichedRegions}
                selectedRegionId={selectedRegionId}
                onSelectRegion={onSelectRegion}
                focusedRegionId={focusedRegionId}
                rankingConfig={resolvedRankingConfig}
                selectionForRecommendationProps={selectionForRecommendationProps}
            />

            <Box
                sx={{
                    position: "absolute",
                    top: 12,
                    left: 12,
                    zIndex: 1000,
                }}
            >
                <MapModeSelector
                    mode={selectionForRecommendationProps.selectionMode}
                    onChange={selectionForRecommendationProps.setSelectionMode}
                />
            </Box>
        </Box>
    );
}
