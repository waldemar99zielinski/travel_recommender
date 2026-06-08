import { Box } from "@mui/material";

import type { ChatHeaderActionBarProps } from "@/components/chat/Chat.interfaces";

export function ChatHeaderActionBar({ headerAction }: ChatHeaderActionBarProps) {
    if (headerAction == null) {
        return null;
    }

    return (
        <Box
            sx={{
                display: "flex",
                justifyContent: "flex-end",
                px: 1.5,
                py: 1,
                borderBottom: "1px solid",
                borderColor: "divider",
            }}
        >
            {headerAction}
        </Box>
    );
}
