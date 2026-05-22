import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { CssBaseline } from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import App from "./App.tsx";
import { appTheme } from "./theme.ts";
import "@/app/providers/i18n/i18n";
import { appConfiguration } from "@/shared/configuration";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "Bootstrap" });
const rootElement = document.getElementById("root");

if (rootElement == null) {
    logger.error("Application root element not found");
    throw new Error("Root element with id 'root' was not found");
}

logger.info(`Hybrid Travel Recommender ${appConfiguration.version}`);

createRoot(rootElement).render(
    <StrictMode>
        <ThemeProvider theme={appTheme}>
            <CssBaseline />
            <BrowserRouter>
                <App />
            </BrowserRouter>
        </ThemeProvider>
    </StrictMode>,
);
