import { Box } from "@mui/material";

import type { ChatConversationPanelProps } from "@/components/chat/Chat.interfaces";

export function ChatConversationPanel({ children }: ChatConversationPanelProps) {
    return (
        <Box
            sx={{
                flex: 1,
                overflow: "auto",
                px: 1.5,
                py: 1.5,
                position: "relative",
            }}
        >
            {children}
        </Box>
    );
}
