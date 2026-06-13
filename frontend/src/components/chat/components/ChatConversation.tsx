import { useEffect, useRef } from "react";

import { Box, Card, CardContent, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { ChatConversationProps } from "@/components/chat/Chat.interfaces";
import { ChatMessageCard } from "@/components/chat/components/ChatMessageCard";

export function ChatConversation({
    chatRecords,
    onGoingChatTurn,
    isLoading,
    loadingDetail,
    loadingStep = null,
    isDestinationResearchLoading = false,
    onRecommendationSelect,
}: ChatConversationProps) {
    const { t } = useTranslation();
    const bottomRef = useRef<HTMLDivElement | null>(null);
    const hasTurns = chatRecords.length > 0 || onGoingChatTurn != null;
    const shouldShowEmptyState = !hasTurns;
    const shouldShowStandaloneLoading = isLoading && onGoingChatTurn == null;
    const shouldShowOnGoingFilter = onGoingChatTurn?.travel_destination_filter != null;
    const shouldShowOnGoingRecommendations =
        (onGoingChatTurn?.recommendations?.length ?? 0) > 0;

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [chatRecords, onGoingChatTurn, isLoading, loadingDetail]);

    return (
        <Stack spacing={1.5}>
            {shouldShowEmptyState ? (
                <Typography variant="body2" color="text.secondary">
                    {t("chat.emptyState")}
                </Typography>
            ) : (
                chatRecords.map((turn, index) => (
                    <ChatMessageCard
                        key={`${turn.session_id}-${turn.chat_history_number}`}
                        turn={turn}
                        showTravelDestinationFilter={
                            index === chatRecords.length - 1 && !shouldShowOnGoingFilter
                        }
                        showRecommendations={
                            index === chatRecords.length - 1 && !shouldShowOnGoingRecommendations
                        }
                        onRecommendationSelect={onRecommendationSelect}
                    />
                ))
            )}
            {onGoingChatTurn != null && (
                <ChatMessageCard
                    turn={onGoingChatTurn}
                    isStreaming
                    loadingDetail={loadingDetail}
                    loadingStep={loadingStep}
                    isDestinationResearchLoading={isDestinationResearchLoading}
                    showTravelDestinationFilter={shouldShowOnGoingFilter}
                    showRecommendations={shouldShowOnGoingRecommendations}
                    onRecommendationSelect={onRecommendationSelect}
                />
            )}
            {shouldShowStandaloneLoading && (
                <Stack sx={{ alignItems: "flex-start" }}>
                    <Card
                        variant="outlined"
                        sx={{ maxWidth: "85%", bgcolor: "background.paper" }}
                    >
                        <CardContent
                            sx={{ py: 1.25, px: 1.5, "&:last-child": { pb: 1.25 } }}
                        >
                            <Typography variant="caption" color="text.secondary">
                                {loadingDetail ?? t("chat.loading")}
                            </Typography>
                        </CardContent>
                    </Card>
                </Stack>
            )}
            <Box ref={bottomRef} />
        </Stack>
    );
}
