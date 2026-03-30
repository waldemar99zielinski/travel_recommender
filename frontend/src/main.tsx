import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { CssBaseline } from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import App from "./App.tsx";
import { appTheme } from "./theme.ts";
import "@/app/providers/i18n/i18n";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <ThemeProvider theme={appTheme}>
            <CssBaseline />
            <BrowserRouter>
                <App />
            </BrowserRouter>
        </ThemeProvider>
    </StrictMode>,
);
