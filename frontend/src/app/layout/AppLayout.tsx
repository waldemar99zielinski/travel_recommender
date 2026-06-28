import { AppBar, Box, Toolbar, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";
import { Outlet } from "react-router-dom";

import { SurveyButton } from "@/components/survey/SurveyButton";
import { SurveyOverlay } from "@/components/survey/SurveyOverlay";
import { appConfiguration } from "@/shared/configuration/appConfiguration";
import { useSurveyContext } from "@/shared/context";

export function AppLayout() {
    const { t } = useTranslation();
    const { isSurveyOpen, closeSurvey } = useSurveyContext();
    const isSurveyEnabled = appConfiguration.surveyEnabled;

    return (
        <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
            <AppBar
                position="static"
                elevation={0}
                sx={{ borderBottom: "1px solid", borderColor: "divider" }}
            >
                <Toolbar sx={{ minHeight: "64px" }}>
                    <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        {t("app.title")}
                    </Typography>
                    {isSurveyEnabled && <SurveyButton />}
                </Toolbar>
            </AppBar>
            <Box component="main" sx={{ flex: 1, minHeight: 0 }}>
                <Outlet />
            </Box>
            {isSurveyEnabled && <SurveyOverlay open={isSurveyOpen} onClose={closeSurvey} />}
        </Box>
    );
}
