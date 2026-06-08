import { CircularProgress, IconButton, Stack, SvgIcon, TextField } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { ChatPromptCardProps } from "@/components/chat/Chat.interfaces";

export function ChatPromptCard({
    message,
    onMessageChange,
    onSubmit,
    isLoading,
}: ChatPromptCardProps) {
    const { t } = useTranslation();
    const canSubmit = message.trim().length > 0 && !isLoading;

    return (
        <Stack direction="row" spacing={1} sx={{ alignItems: "flex-end" }}>
            <TextField
                fullWidth
                minRows={1}
                maxRows={6}
                multiline
                value={message}
                onChange={(event) => onMessageChange(event.target.value)}
                placeholder={t("chat.inputPlaceholder")}
                onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey && !isLoading) {
                        event.preventDefault();
                        if (canSubmit) {
                            void onSubmit();
                        }
                    }
                }}
            />
            <IconButton
                color="primary"
                onClick={() => {
                    void onSubmit();
                }}
                disabled={!canSubmit}
                aria-label={isLoading ? t("chat.loading") : t("chat.send")}
                sx={{
                    width: 42,
                    height: 42,
                    borderRadius: 2,
                    border: "1px solid",
                    borderColor: "divider",
                    transition: "all 120ms ease",
                    "&:hover": {
                        transform: "translateY(-1px)",
                    },
                }}
            >
                {isLoading ? (
                    <CircularProgress size={18} color="inherit" />
                ) : (
                    <SvgIcon fontSize="small" viewBox="0 0 24 24">
                        <path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z" />
                    </SvgIcon>
                )}
            </IconButton>
        </Stack>
    );
}
