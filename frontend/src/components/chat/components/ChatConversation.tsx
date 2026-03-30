import { useEffect, useRef } from "react";

import { Box, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { ChatConversationProps } from "@/components/chat/Chat.interfaces";
import { ChatMessageCard } from "@/components/chat/components/ChatMessageCard";

export function ChatConversation({ messages }: ChatConversationProps) {
    const { t } = useTranslation();
    const bottomRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [messages]);

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
            <Box ref={bottomRef} />
        </Stack>
    );
}
