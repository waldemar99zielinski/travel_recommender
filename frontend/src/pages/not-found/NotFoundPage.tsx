import { Button, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";
import { Link as RouterLink } from "react-router-dom";

export function NotFoundPage() {
    const { t } = useTranslation();

    return (
        <Stack
            sx={{ height: "100vh", px: 2 }}
            alignItems="center"
            justifyContent="center"
            spacing={2}
        >
            <Typography variant="h4">{t("notFound.title")}</Typography>
            <Typography color="text.secondary">
                {t("notFound.description")}
            </Typography>
            <Button
                variant="contained"
                component={RouterLink}
                to="/"
            >
                {t("notFound.cta")}
            </Button>
        </Stack>
    );
}
