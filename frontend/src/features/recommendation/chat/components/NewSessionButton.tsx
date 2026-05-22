import { useState } from "react";

import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Typography,
} from "@mui/material";
import { useTranslation } from "react-i18next";

type NewSessionButtonProps = {
    disabled: boolean;
    onConfirm: () => Promise<void>;
};

export function NewSessionButton({ disabled, onConfirm }: NewSessionButtonProps) {
    const { t } = useTranslation();
    const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false);

    const handleConfirm = async () => {
        await onConfirm();
        setIsConfirmDialogOpen(false);
    };

    return (
        <>
            <Button
                size="small"
                variant="outlined"
                onClick={() => setIsConfirmDialogOpen(true)}
                disabled={disabled}
            >
                {t("chat.newSession.action")}
            </Button>
            <Dialog
                open={isConfirmDialogOpen}
                onClose={() => {
                    if (!disabled) {
                        setIsConfirmDialogOpen(false);
                    }
                }}
                fullWidth
                maxWidth="xs"
            >
                <DialogTitle>{t("chat.newSession.title")}</DialogTitle>
                <DialogContent>
                    <Typography variant="body2" color="text.secondary">
                        {t("chat.newSession.description")}
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setIsConfirmDialogOpen(false)} disabled={disabled}>
                        {t("chat.newSession.cancel")}
                    </Button>
                    <Button
                        variant="contained"
                        onClick={() => {
                            void handleConfirm();
                        }}
                        disabled={disabled}
                    >
                        {t("chat.newSession.confirm")}
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
}
