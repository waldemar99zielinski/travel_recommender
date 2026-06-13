import { Box, Paper, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { MAP_COLORS } from "@/components/map/map.config";

const MAP_LEGEND = [
    { labelKey: "map.legend.recommended", color: MAP_COLORS.recommendedFill },
    { labelKey: "map.legend.included", color: MAP_COLORS.includedFill },
    { labelKey: "map.legend.excluded", color: MAP_COLORS.excludedFill },
] as const;

export function MapLegend() {
    const { t } = useTranslation();

    return (
        <Paper
            elevation={2}
            sx={{
                position: "absolute",
                zIndex: 900,
                left: 16,
                bottom: 16,
                px: 1.5,
                py: 1,
                borderRadius: 1,
            }}
        >
            <Stack spacing={0.5}>
                {MAP_LEGEND.map((entry) => (
                    <Stack
                        key={entry.labelKey}
                        direction="row"
                        spacing={1}
                        sx={{ alignItems: "center" }}
                    >
                        <Box
                            sx={{
                                width: 14,
                                height: 14,
                                borderRadius: 0.5,
                                border: "1px solid rgba(0,0,0,0.12)",
                                bgcolor: entry.color,
                            }}
                        />
                        <Typography variant="caption">
                            {t(entry.labelKey)}
                        </Typography>
                    </Stack>
                ))}
            </Stack>
        </Paper>
    );
}
