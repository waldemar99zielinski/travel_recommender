import { useEffect, useRef } from "react";

import { Box, Card, CardContent, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { ChatConversationProps } from "@/components/chat/Chat.interfaces";
import { ChatMessageCard } from "@/components/chat/components/ChatMessageCard";

const typingDots = [0, 1, 2] as const;

export function ChatConversation({ messages, isLoading }: ChatConversationProps) {
    const { t } = useTranslation();
    const bottomRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [messages, isLoading]);

    return (
        <Stack spacing={1.5}>
            {messages.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                    {t("chat.emptyState")}
                </Typography>
            ) : (
                messages.map((message) => (
                    <ChatMessageCard key={message.id} message={message} />
                ))
            )}
            {isLoading && (
                <Stack alignItems="flex-start">
                    <Card
                        variant="outlined"
                        sx={{ maxWidth: "85%", bgcolor: "background.paper" }}
                    >
                        <CardContent
                            sx={{ py: 1.25, px: 1.5, "&:last-child": { pb: 1.25 } }}
                        >
                            <Stack
                                role="status"
                                aria-live="polite"
                                spacing={0.75}
                                sx={{
                                    "@keyframes chatTypingPulse": {
                                        "0%, 80%, 100%": {
                                            transform: "scale(0.7)",
                                            opacity: 0.35,
                                        },
                                        "40%": {
                                            transform: "scale(1)",
                                            opacity: 1,
                                        },
                                    },
                                }}
                            >
                                <Typography variant="caption" color="text.secondary">
                                    {t("chat.typing")}
                                </Typography>
                                <Stack direction="row" spacing={0.5} alignItems="center">
                                    {typingDots.map((dot) => (
                                        <Box
                                            key={dot}
                                            sx={{
                                                width: 7,
                                                height: 7,
                                                borderRadius: "50%",
                                                bgcolor: "text.secondary",
                                                animation:
                                                    "chatTypingPulse 1.1s infinite ease-in-out",
                                                animationDelay: `${dot * 0.16}s`,
                                            }}
                                        />
                                    ))}
                                </Stack>
                            </Stack>
                        </CardContent>
                    </Card>
                </Stack>
            )}
            <Box ref={bottomRef} />
        </Stack>
    );
}
