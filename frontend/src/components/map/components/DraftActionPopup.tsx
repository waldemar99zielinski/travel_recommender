import { Paper, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

export interface DraftActionPopupProps {
    menuPosition: { x: number; y: number } | null;
    
    onDraftInclude: () => void;
    onDraftExclude: () => void;
    onDraftCancel: () => void;
}

export function DraftActionPopup({
    menuPosition,
    onDraftInclude,
    onDraftExclude,
    onDraftCancel,
}: DraftActionPopupProps) {
    const { t } = useTranslation();
    if (menuPosition == null) {
        return null;
    }

    return (
        <Paper
            sx={{
                position: "absolute",
                left: menuPosition.x,
                top: menuPosition.y - 60,
                zIndex: 9999,
                display: "flex",
                gap: 0.5,
                px: 1.5,
                py: 0.5,
                boxShadow: 4,
                borderRadius: 1,
                cursor: "pointer",
            }}
        >
            <Typography
                variant="body2"
                sx={{
                    px: 1,
                    py: 0.5,
                    "&:hover": { bgcolor: "action.hover" },
                    color: "success.main",
                    fontWeight: 600,
                }}
                onClick={() => {
                    onDraftInclude();
                }}
            >
                {t("map.draftAction.include")}
            </Typography>
            <Typography
                variant="body2"
                sx={{
                    px: 1,
                    py: 0.5,
                    "&:hover": { bgcolor: "action.hover" },
                    color: "error.main",
                    fontWeight: 600,
                }}
                onClick={() => {
                    onDraftExclude();
                }}
            >
                {t("map.draftAction.exclude")}
            </Typography>
            <Typography
                variant="body2"
                sx={{
                    px: 1,
                    py: 0.5,
                    "&:hover": { bgcolor: "action.hover" },
                    color: "text.secondary",
                }}
                onClick={() => {
                    onDraftCancel();
                }}
            >
                {t("map.draftAction.remove")}
            </Typography>
        </Paper>
    );
}
