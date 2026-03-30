import { Button, Stack, TextField } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { ChatPromptCardProps } from "@/components/chat/Chat.interfaces";

export function ChatPromptCard({
    message,
    onMessageChange,
    onSubmit,
    isLoading,
}: ChatPromptCardProps) {
    const { t } = useTranslation();

    return (
        <Stack direction="row" spacing={1} alignItems="flex-end">
            <TextField
                fullWidth
                minRows={1}
                maxRows={6}
                multiline
                value={message}
                onChange={(event) => onMessageChange(event.target.value)}
                placeholder={t("chat.inputPlaceholder")}
                onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                        event.preventDefault();
                        onSubmit();
                    }
                }}
            />
            <Button variant="contained" onClick={onSubmit} disabled={isLoading}>
                {isLoading ? t("chat.loading") : t("chat.send")}
            </Button>
        </Stack>
    );
}
