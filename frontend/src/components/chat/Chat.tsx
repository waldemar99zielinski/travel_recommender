import { Alert, Box, Card, Stack } from "@mui/material";

import type { ChatProps } from "@/components/chat/Chat.interfaces";
import { ChatConversation } from "@/components/chat/components/ChatConversation";
import { ChatPromptCard } from "@/components/chat/components/ChatPromptCard";

export function Chat({
    messages,
    message,
    onMessageChange,
    onSubmit,
    isLoading,
    errorMessage,
}: ChatProps) {
    return (
        <Stack
            sx={{
                width: { xs: "100%", lg: 380 },
                flexShrink: 0,
                minHeight: { xs: 420, lg: "100%" },
            }}
        >
            <Card
                variant="outlined"
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    flex: 1,
                    minHeight: 0,
                    overflow: "hidden",
                }}
            >
                <Box sx={{ flex: 1, overflow: "auto", px: 1.5, py: 1.5 }}>
                    <ChatConversation messages={messages} />
                </Box>
                {errorMessage != null && (
                    <Box sx={{ px: 1.5, pb: 1 }}>
                        <Alert severity="error">{errorMessage}</Alert>
                    </Box>
                )}
                <Box
                    sx={{
                        borderTop: "1px solid",
                        borderColor: "divider",
                        p: 1.5,
                    }}
                >
                    <ChatPromptCard
                        message={message}
                        onMessageChange={onMessageChange}
                        onSubmit={onSubmit}
                        isLoading={isLoading}
                    />
                </Box>
            </Card>
        </Stack>
    );
}
