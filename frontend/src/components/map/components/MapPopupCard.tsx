import { Box, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { MapPopupCardProps } from "@/components/map/Map.interfaces";
import { formatRecommendationScore } from "@/components/map/model/mapColors";

export function MapPopupCard({ properties }: MapPopupCardProps) {
    const { t } = useTranslation();
    const regionTitle = properties.display_name;

    return (
        <Box sx={{ minWidth: 200, p: 0.5 }}>
            <Stack spacing={0.5}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                    {regionTitle}
                </Typography>
                {properties.recommendation ? (
                    <Typography variant="body2">
                        {t("map.popup.score", {
                            score: formatRecommendationScore(
                                properties.recommendation.score,
                            ),
                        })}
                    </Typography>
                ) : null}
            </Stack>
        </Box>
    );
}
