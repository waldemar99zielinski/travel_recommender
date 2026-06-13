import { Box, CircularProgress, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { normalizeRegionId } from "@/components/map/model/mapSelectors";
import type { ChatRecordDto } from "@/models/chat.models";
import {
    recommendationItemDtoSchema,
    recommendationV2TravelDestinationEvaluationDtoSchema,
} from "@/models/recommendation.models";

interface ChatRecommendationsProps {
    recommendations?: ChatRecordDto["recommendations"];
    travelDestinationsEvaluations?: ChatRecordDto["travel_destinations_evaluations"];
    isDestinationResearchLoading?: boolean;
    maxItems?: number;
    onRecommendationSelect?: (regionId: string) => void;
}

export function ChatRecommendations({
    recommendations,
    travelDestinationsEvaluations,
    isDestinationResearchLoading = false,
    maxItems = 5,
    onRecommendationSelect,
}: ChatRecommendationsProps) {
    const { t } = useTranslation();
    const parsedRecommendations = recommendationItemDtoSchema.array().safeParse(
        recommendations ?? [],
    );
    const parsedEvaluations =
        recommendationV2TravelDestinationEvaluationDtoSchema.array().safeParse(
            travelDestinationsEvaluations ?? [],
        );

    if (!parsedRecommendations.success || parsedRecommendations.data.length === 0) {
        return null;
    }

    const topRecommendations = parsedRecommendations.data.slice(0, maxItems);
    const loadedDestinationResearchIds = new Set(
        parsedEvaluations.success
            ? parsedEvaluations.data.map((evaluation) =>
                  normalizeRegionId(evaluation.region_id),
              )
            : [],
    );
    const shouldShowDestinationResearchStatus =
        isDestinationResearchLoading || loadedDestinationResearchIds.size > 0;

    return (
        <Stack spacing={1} sx={{ minWidth: 0 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                {t("chat.recommendations.title", { count: topRecommendations.length })}
            </Typography>
            {topRecommendations.map((recommendation, index) => {
                const isDestinationResearchReady = loadedDestinationResearchIds.has(
                    normalizeRegionId(recommendation.region_id),
                );
                const shouldShowDestinationResearchLoader =
                    isDestinationResearchLoading && !isDestinationResearchReady;

                return (
                    <Box
                        key={recommendation.region_id}
                        onClick={() => onRecommendationSelect?.(recommendation.region_id)}
                        sx={{
                            border: "1px solid",
                            borderColor: "divider",
                            borderRadius: 1.5,
                            px: 1.25,
                            py: 1,
                            bgcolor: "background.default",
                            cursor:
                                onRecommendationSelect != null ? "pointer" : "default",
                            transition: "transform 120ms ease, box-shadow 120ms ease",
                            "&:hover":
                                onRecommendationSelect != null
                                    ? {
                                          transform: "translateY(-1px)",
                                          boxShadow: 2,
                                      }
                                    : undefined,
                        }}
                    >
                        <Stack spacing={0.75}>
                            <Stack
                                direction="row"
                                spacing={1}
                                sx={{ alignItems: "flex-start", minWidth: 0 }}
                            >
                                <Box
                                    sx={{
                                        width: 22,
                                        height: 22,
                                        flexShrink: 0,
                                        borderRadius: "50%",
                                        display: "grid",
                                        placeItems: "center",
                                        bgcolor: "primary.main",
                                        color: "primary.contrastText",
                                        fontSize: 12,
                                        fontWeight: 700,
                                    }}
                                >
                                    {index + 1}
                                </Box>
                                <Box sx={{ minWidth: 0, flex: 1 }}>
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                        {recommendation.region_name}
                                    </Typography>
                                </Box>
                                {shouldShowDestinationResearchStatus &&
                                    (isDestinationResearchReady ||
                                        shouldShowDestinationResearchLoader) && (
                                        <Box
                                            sx={{
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 0.5,
                                                flexShrink: 0,
                                                color: isDestinationResearchReady
                                                    ? "success.main"
                                                    : "text.secondary",
                                            }}
                                            >
                                            {isDestinationResearchReady ? (
                                                <Box
                                                    sx={{
                                                        width: 8,
                                                        height: 8,
                                                        borderRadius: "50%",
                                                        bgcolor: "currentColor",
                                                    }}
                                                />
                                            ) : (
                                                <CircularProgress
                                                    color="inherit"
                                                    size={14}
                                                />
                                            )}
                                            <Typography variant="caption" color="inherit">
                                                {isDestinationResearchReady
                                                    ? t(
                                                          "chat.recommendations.destinationResearch.ready",
                                                      )
                                                    : t(
                                                          "chat.recommendations.destinationResearch.loading",
                                                      )}
                                            </Typography>
                                        </Box>
                                    )}
                            </Stack>
                            <Typography variant="caption" color="text.secondary">
                                {recommendation.region_id}
                            </Typography>
                        </Stack>
                    </Box>
                );
            })}
        </Stack>
    );
}
