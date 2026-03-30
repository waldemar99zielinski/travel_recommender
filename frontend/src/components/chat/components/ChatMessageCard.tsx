import { Box, Card, CardContent, Stack } from "@mui/material";

import type { ChatMessageCardProps } from "@/components/chat/Chat.interfaces";

export function ChatMessageCard({ message }: ChatMessageCardProps) {
    const isUser = message.role === "user";
    const isClickable = message.onClick != null;

    return (
        <Stack alignItems={isUser ? "flex-end" : "flex-start"}>
            <Card
                variant="outlined"
                onClick={message.onClick}
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
                <CardContent
                    sx={{ py: 1.25, px: 1.5, "&:last-child": { pb: 1.25 } }}
                >
                    <Box
                        sx={{
                            fontSize: 14,
                            lineHeight: 1.5,
                            whiteSpace: "pre-wrap",
                        }}
                    >
                        {message.content}
                    </Box>
                </CardContent>
            </Card>
        </Stack>
    );
}
