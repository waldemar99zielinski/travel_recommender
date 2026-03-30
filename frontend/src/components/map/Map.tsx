import { useMemo } from "react";

import { Box } from "@mui/material";

import type { MapProps } from "@/components/map/Map.interfaces";
import { MapCanvas } from "@/components/map/components/MapCanvas";
import { enrichRegions } from "@/components/map/model/mapSelectors";

export function Map({
    regions,
    recommendations,
    selectedRegionId,
    onSelectRegion,
    rankingConfig,
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
                rankingConfig={resolvedRankingConfig}
            />
        </Box>
    );
}
