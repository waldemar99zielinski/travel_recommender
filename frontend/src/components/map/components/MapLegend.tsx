import { Box, Paper, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { SCORE_LEGEND, scoreToColor } from "@/components/map/model/mapColors";

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
                {SCORE_LEGEND.map((entry) => (
                    <Stack
                        key={entry.labelKey}
                        direction="row"
                        spacing={1}
                        alignItems="center"
                    >
                        <Box
                            sx={{
                                width: 14,
                                height: 14,
                                borderRadius: 0.5,
                                border: "1px solid rgba(0,0,0,0.12)",
                                bgcolor: scoreToColor(entry.score),
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
