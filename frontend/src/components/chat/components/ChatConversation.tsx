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
}: ChatConversationProps) {
    const { t } = useTranslation();
    const bottomRef = useRef<HTMLDivElement | null>(null);
    const hasTurns = chatRecords.length > 0 || onGoingChatTurn != null;
    const shouldShowEmptyState = !hasTurns;
    const shouldShowStandaloneLoading = isLoading && onGoingChatTurn == null;

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
                chatRecords.map((turn) => (
                    <ChatMessageCard
                        key={`${turn.session_id}-${turn.chat_history_number}`}
                        turn={turn}
                    />
                ))
            )}
            {onGoingChatTurn != null && (
                <ChatMessageCard
                    turn={onGoingChatTurn}
                    isStreaming
                    loadingDetail={loadingDetail}
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
