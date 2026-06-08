import { Box } from "@mui/material";

import type { ChatPromptFooterProps } from "@/components/chat/Chat.interfaces";

export function ChatPromptFooter({ children }: ChatPromptFooterProps) {
    return (
        <Box
            sx={{
                borderTop: "1px solid",
                borderColor: "divider",
                p: 1.5,
            }}
        >
            {children}
        </Box>
    );
}
