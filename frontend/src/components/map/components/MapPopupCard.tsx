import { Box, Divider, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { MapPopupCardProps } from "@/components/map/Map.interfaces";

export function MapPopupCard({ properties }: MapPopupCardProps) {
    const { t } = useTranslation();

    return (
        <Box sx={{ minWidth: 200, p: 0.5 }}>
            <Stack spacing={0.5}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                    {properties.display_name ??
                        properties.name ??
                        properties.u_name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                    {t("map.popup.regionId", { id: properties.u_name })}
                </Typography>
                <Divider sx={{ my: 0.5 }} />
                {properties.recommendation ? (
                    <>
                        <Typography variant="body2">
                            {t("map.popup.score", {
                                score: String(
                                    Math.round(properties.recommendation.score),
                                ),
                            })}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            {properties.recommendation.description}
                        </Typography>
                    </>
                ) : (
                    <Typography variant="body2" color="text.secondary">
                        {t("map.popup.noRecommendation")}
                    </Typography>
                )}
            </Stack>
        </Box>
    );
}
