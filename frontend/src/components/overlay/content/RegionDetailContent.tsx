import { Box, Chip, Link, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { TimedProgressLoader } from "@/components/loader/TimedProgressLoader";
import type {
    RecommendationItemDto,
    RecommendationV2TravelDestinationEvaluationDto,
} from "@/models/recommendation.models";
import { useDestinationContext } from "@/shared/context";

interface RegionDetailContentProps {
    regionId: string;
    regionName?: string;
    recommendation?: RecommendationItemDto;
    destinationResearch?: RecommendationV2TravelDestinationEvaluationDto | null;
    isDestinationResearchLoading?: boolean;
    destinationResearchLoadingDurationMs?: number;
}

export function RegionDetailContent({
    regionId,
    regionName,
    recommendation,
    destinationResearch = null,
    isDestinationResearchLoading = false,
    destinationResearchLoadingDurationMs = 30_000,
}: RegionDetailContentProps) {
    const { t } = useTranslation();
    const { getDestination } = useDestinationContext();

    const destination = getDestination(regionId);

    return (
        <Stack spacing={2}>
            {isDestinationResearchLoading && (
                <TimedProgressLoader
                    durationMs={destinationResearchLoadingDurationMs}
                    label={t("loader.loading")}
                />
            )}

            {destinationResearch != null && (
                <Stack spacing={1}>
                    <Typography variant="body2" color="text.secondary">
                        {destinationResearch.description}
                    </Typography>
                    {destinationResearch.image_urls.length > 0 && (
                        <Box
                            sx={{
                                display: "grid",
                                gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                                gap: 1,
                            }}
                        >
                            {destinationResearch.image_urls.map((imageUrl) => (
                                <Link
                                    key={imageUrl}
                                    href={imageUrl}
                                    target="_blank"
                                    rel="noreferrer"
                                    sx={{
                                        display: "block",
                                        borderRadius: 1.5,
                                        overflow: "hidden",
                                        bgcolor: "grey.100",
                                    }}
                                >
                                    <Box
                                        component="img"
                                        src={imageUrl}
                                        alt={regionName ?? regionId}
                                        sx={{
                                            display: "block",
                                            width: "100%",
                                            aspectRatio: "4 / 3",
                                            objectFit: "cover",
                                        }}
                                    />
                                </Link>
                            ))}
                        </Box>
                    )}
                </Stack>
            )}

            {destinationResearch == null && destination != null && !isDestinationResearchLoading && (
                <Typography variant="body2" color="text.secondary">
                    {destination.description}
                </Typography>
            )}

            {recommendation != null && (
                <Box>
                    <Typography variant="subtitle2" sx={{ mb: 0.5 }}>
                        {t("chat.recommendations.title", {
                            count: 1,
                        })}
                    </Typography>
                    <Chip
                        label={recommendation.region_name}
                        size="small"
                        color="primary"
                        variant="outlined"
                    />
                    <Typography variant="body2" sx={{ mt: 1 }}>
                        {recommendation.region_id}
                    </Typography>
                </Box>
            )}
        </Stack>
    );
}
