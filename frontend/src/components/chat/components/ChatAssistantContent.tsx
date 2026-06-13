import { Box, Divider, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { ChatRecommendations } from "@/components/chat/components/ChatRecommendations";
import { TimedProgressLoader } from "@/components/loader/TimedProgressLoader";
import { TravelDestinationFilterDisplay } from "@/components/chat/components/TravelDestinationFilterDisplay";
import type { ChatRecordDto } from "@/models/chat.models";
import type { ProgressStage } from "@/models/recommendation.stream.models";

const STEP_LOADER_DURATION_MS: Partial<Record<ProgressStage, number>> = {
    initializing: 10_000,
    validating_request: 10_000,
    gathering_filter: 15_000,
    recommendation_generation: 10_000,
    desination_research_generation: 15_000,
    destination_research: 10_000,
    response_generation: 10_000,
};

interface ChatAssistantContentProps {
    turn: ChatRecordDto | Partial<ChatRecordDto>;
    isStreaming?: boolean;
    loadingDetail?: string | null;
    loadingStep?: ProgressStage | null;
    isDestinationResearchLoading?: boolean;
    showTravelDestinationFilter?: boolean;
    showRecommendations?: boolean;
    onRecommendationSelect?: (regionId: string) => void;
}

export function ChatAssistantContent({
    turn,
    isStreaming = false,
    loadingDetail = null,
    loadingStep = null,
    isDestinationResearchLoading = false,
    showTravelDestinationFilter = false,
    showRecommendations = false,
    onRecommendationSelect,
}: ChatAssistantContentProps) {
    const { t } = useTranslation();
    const travelDestinationFilter = turn.travel_destination_filter;
    const systemResponse = turn.system_response?.trim();
    const hasRecommendations = showRecommendations && (turn.recommendations?.length ?? 0) > 0;
    const hasSupplementaryContent =
        (showTravelDestinationFilter && travelDestinationFilter != null) || hasRecommendations;
    const hasAssistantBody = isStreaming || Boolean(systemResponse);
    const loadingDurationMs =
        loadingStep == null ? null : STEP_LOADER_DURATION_MS[loadingStep] ?? null;

    return (
        <Stack spacing={1.25}>
            {showTravelDestinationFilter && travelDestinationFilter && (
                <TravelDestinationFilterDisplay filter={travelDestinationFilter} />
            )}
            {hasRecommendations && (
                <ChatRecommendations
                    recommendations={turn.recommendations}
                    travelDestinationsEvaluations={turn.travel_destinations_evaluations}
                    isDestinationResearchLoading={isDestinationResearchLoading}
                    onRecommendationSelect={onRecommendationSelect}
                />
            )}
            {hasSupplementaryContent && hasAssistantBody && <Divider flexItem />}
            {!systemResponse && isStreaming && (
                loadingDurationMs != null ? (
                    <TimedProgressLoader
                        key={loadingStep}
                        durationMs={loadingDurationMs}
                        label={loadingDetail ?? t("chat.loading")}
                    />
                ) : (
                    <Typography variant="caption" color="text.secondary">
                        {loadingDetail ?? t("chat.loading")}
                    </Typography>
                )
            )}
            {systemResponse && (
                <Box
                    sx={{
                        fontSize: 14,
                        lineHeight: 1.5,
                        whiteSpace: "pre-wrap",
                    }}
                >
                    {systemResponse}
                </Box>
            )}
        </Stack>
    );
}
