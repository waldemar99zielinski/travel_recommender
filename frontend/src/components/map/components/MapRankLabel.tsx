import { Typography } from "@mui/material";

import type { MapRankLabelProps } from "@/components/map/Map.interfaces";

function buildLabel({ rank, score, mode }: MapRankLabelProps): string {
    const roundedScore = Math.round(score);

    if (mode === "score") {
        return `${roundedScore}`;
    }

    if (mode === "rank-score") {
        return `#${rank} ${roundedScore}`;
    }

    return `${rank}`;
}

export function MapRankLabel({ rank, score, mode }: MapRankLabelProps) {
    return (
        <Typography
            sx={{
                fontWeight: 700,
                fontSize: 14,
                color: "#112433",
                textShadow: "0 1px 0 rgba(255,255,255,0.65)",
                px: 0.3,
            }}
        >
            {buildLabel({ rank, score, mode })}
        </Typography>
    );
}
