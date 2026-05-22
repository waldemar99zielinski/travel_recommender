import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Box,
    Stack,
    SvgIcon,
    Typography,
} from "@mui/material";
import { useTranslation } from "react-i18next";

import { formatRecommendationScore } from "@/components/map/model/mapColors";
import type { RecommendationItemDto } from "@/models/recommendation.models";
import { useRecommendationFeatureContext } from "@/features/recommendation/useRecommendationFeatureContext";

type RecommendationResultsMessageProps = {
    recommendations: RecommendationItemDto[];
};

export function RecommendationResultsMessage({
    recommendations,
}: RecommendationResultsMessageProps) {
    const { t } = useTranslation();
    const { selectedRegionId, setSelectedRegionId, setFocusedRegionId } =
        useRecommendationFeatureContext();

    if (recommendations.length === 0) {
        return null;
    }

    return (
        <Stack spacing={1} sx={{ minWidth: 0 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                {t("chat.recommendations.title", {
                    count: recommendations.length,
                })}
            </Typography>
            {recommendations.map((recommendation, index) => {
                const isExpanded = selectedRegionId === recommendation.id;

                return (
                    <Accordion
                        key={recommendation.id}
                        expanded={isExpanded}
                        onChange={(_, nextExpanded) => {
                            if (nextExpanded) {
                                setSelectedRegionId(recommendation.id);
                                setFocusedRegionId(recommendation.id);
                            } else {
                                setSelectedRegionId(null);
                                setFocusedRegionId(null);
                            }
                        }}
                        disableGutters
                        elevation={0}
                        square
                        sx={{
                            border: "1px solid",
                            borderColor: isExpanded ? "primary.light" : "divider",
                            borderRadius: 1.5,
                            overflow: "hidden",
                            bgcolor: "background.default",
                            "&:before": {
                                display: "none",
                            },
                        }}
                    >
                        <AccordionSummary
                            expandIcon={
                                <SvgIcon fontSize="small" viewBox="0 0 24 24">
                                    <path d="m7 10 5 5 5-5z" />
                                </SvgIcon>
                            }
                            sx={{
                                px: 1.25,
                                minHeight: 0,
                                "& .MuiAccordionSummary-content": {
                                    my: 1,
                                },
                            }}
                        >
                            <Stack
                                direction="row"
                                spacing={1}
                                alignItems="center"
                                sx={{ width: "100%", minWidth: 0 }}
                            >
                                <Box
                                    sx={{
                                        width: 24,
                                        height: 24,
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
                                    <Typography
                                        variant="body2"
                                        sx={{ fontWeight: 600 }}
                                    >
                                        {recommendation.title}
                                    </Typography>
                                    <Typography
                                        variant="caption"
                                        color="text.secondary"
                                    >
                                        {t("chat.recommendations.score", {
                                            score: formatRecommendationScore(
                                                recommendation.score,
                                            ),
                                        })}
                                    </Typography>
                                </Box>
                            </Stack>
                        </AccordionSummary>
                        <AccordionDetails sx={{ px: 1.25, pt: 0, pb: 1.25 }}>
                            <Typography variant="body2" color="text.secondary">
                                {recommendation.description.trim() ||
                                    t("chat.recommendations.noDescription")}
                            </Typography>
                        </AccordionDetails>
                    </Accordion>
                );
            })}
        </Stack>
    );
}
