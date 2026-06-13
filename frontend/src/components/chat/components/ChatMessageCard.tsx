import type { ReactNode } from "react";

import { Box, Card, CardContent, Stack } from "@mui/material";

import type { ChatMessageCardProps } from "@/components/chat/Chat.interfaces";
import { ChatAssistantContent } from "@/components/chat/components/ChatAssistantContent";

function renderBubble(
    content: ReactNode,
    {
        align,
        isUser,
        onClick,
    }: {
        align: "flex-start" | "flex-end";
        isUser: boolean;
        onClick?: () => void;
    },
) {
    const isClickable = onClick != null;

    return (
        <Stack sx={{ alignItems: align }}>
            <Card
                variant="outlined"
                onClick={onClick}
                sx={{
                    maxWidth: "85%",
                    bgcolor: isUser ? "primary.main" : "background.paper",
                    color: isUser ? "primary.contrastText" : "text.primary",
                    cursor: isClickable ? "pointer" : "default",
                    transition: "transform 120ms ease, box-shadow 120ms ease",
                    "&:hover": isClickable
                        ? {
                              transform: "translateY(-1px)",
                              boxShadow: 2,
                          }
                        : undefined,
                }}
            >
                <CardContent sx={{ py: 1.25, px: 1.5, "&:last-child": { pb: 1.25 } }}>
                    <Box
                        sx={{
                            fontSize: 14,
                            lineHeight: 1.5,
                            whiteSpace: "pre-wrap",
                        }}
                    >
                        {content}
                    </Box>
                </CardContent>
            </Card>
        </Stack>
    );
}

export function ChatMessageCard({
    turn,
    isStreaming = false,
    loadingDetail = null,
    loadingStep = null,
    isDestinationResearchLoading = false,
    showTravelDestinationFilter = false,
    showRecommendations = false,
    onRecommendationSelect,
}: ChatMessageCardProps) {
    const userRequest = turn.user_request?.trim();
    const systemResponse = turn.system_response?.trim();
    const showAssistantCard = isStreaming || Boolean(systemResponse);

    return (
        <Stack spacing={1}>
            {userRequest &&
                renderBubble(userRequest, {
                    align: "flex-end",
                    isUser: true,
                })}
            {showAssistantCard && (
                <Stack sx={{ alignItems: "flex-start" }}>
                    <Card
                        variant="outlined"
                        sx={{
                            maxWidth: "85%",
                            bgcolor: "background.paper",
                            opacity: isStreaming ? 0.96 : 1,
                        }}
                    >
                        <CardContent sx={{ py: 1.25, px: 1.5, "&:last-child": { pb: 1.25 } }}>
                            <ChatAssistantContent
                                turn={turn}
                                isStreaming={isStreaming}
                                loadingDetail={loadingDetail}
                                loadingStep={loadingStep}
                                isDestinationResearchLoading={isDestinationResearchLoading}
                                showTravelDestinationFilter={showTravelDestinationFilter}
                                showRecommendations={showRecommendations}
                                onRecommendationSelect={onRecommendationSelect}
                            />
                        </CardContent>
                    </Card>
                </Stack>
            )}
        </Stack>
    );
}
