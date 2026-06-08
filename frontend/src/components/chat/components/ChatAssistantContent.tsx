import { Box, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { ChatRecordDto } from "@/models/chat.models";

interface ChatAssistantContentProps {
    turn: ChatRecordDto | Partial<ChatRecordDto>;
    isStreaming?: boolean;
    loadingDetail?: string | null;
}

export function ChatAssistantContent({
    turn,
    isStreaming = false,
    loadingDetail = null,
}: ChatAssistantContentProps) {
    const { t } = useTranslation();
    const systemResponse = turn.system_response?.trim();

    return (
        <Stack spacing={1.25}>
            {!systemResponse && isStreaming && (
                <Typography variant="caption" color="text.secondary">
                    {loadingDetail ?? t("chat.loading")}
                </Typography>
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
