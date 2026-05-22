import { Alert, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

type ErrorPageProps = {
    message?: string | null;
};

export function ErrorPage({ message }: ErrorPageProps) {
    const { t } = useTranslation();

    return (
        <Stack
            sx={{ minHeight: "100vh", px: 2 }}
            alignItems="center"
            justifyContent="center"
            spacing={2}
        >
            <Typography variant="h4">{t("error.title")}</Typography>
            <Alert severity="error" sx={{ width: "100%", maxWidth: 560 }}>
                {message ?? t("error.defaultMessage")}
            </Alert>
        </Stack>
    );
}
