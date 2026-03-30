import { AppBar, Box, Toolbar, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";
import { Outlet } from "react-router-dom";

export function AppLayout() {
    const { t } = useTranslation();

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
                </Toolbar>
            </AppBar>
            <Box component="main" sx={{ flex: 1, minHeight: 0 }}>
                <Outlet />
            </Box>
        </Box>
    );
}
