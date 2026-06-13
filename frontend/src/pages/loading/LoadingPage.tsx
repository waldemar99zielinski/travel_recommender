import { CircularProgress, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

export function LoadingPage() {
    const { t } = useTranslation();

    return (
        <Stack
            sx={{ minHeight: "100vh", px: 2, alignItems: "center", justifyContent: "center" }}
            spacing={2}
        >
            <CircularProgress />
            <Typography color="text.secondary">{t("loading.message")}</Typography>
        </Stack>
    );
}
