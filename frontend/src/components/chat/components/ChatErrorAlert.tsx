import { Alert, Box } from "@mui/material";

import type { ChatErrorAlertProps } from "@/components/chat/Chat.interfaces";

export function ChatErrorAlert({ errorMessage }: ChatErrorAlertProps) {
    if (errorMessage == null) {
        return null;
    }

    return (
        <Box sx={{ px: 1.5, pb: 1 }}>
            <Alert severity="error">{errorMessage}</Alert>
        </Box>
    );
}
