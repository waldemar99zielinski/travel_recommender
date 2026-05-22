import path from "node:path";
import { readFileSync } from "node:fs";

import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

const packageJson = JSON.parse(
    readFileSync(path.resolve(__dirname, "./package.json"), "utf-8"),
) as { version?: string };
const appVersion = packageJson.version ?? "0.0.0";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, __dirname, "");
    const frontendHost = env.FRONTEND_HOST ?? "127.0.0.1";
    const parsedFrontendPort = Number.parseInt(env.FRONTEND_PORT ?? "5173", 10);
    const frontendPort = Number.isNaN(parsedFrontendPort)
        ? 5173
        : parsedFrontendPort;

    return {
        plugins: [react()],
        define: {
            __APP_VERSION__: JSON.stringify(appVersion),
        },
        server: {
            host: frontendHost,
            port: frontendPort,
        },
        resolve: {
            alias: {
                "@": path.resolve(__dirname, "./src"),
            },
        },
    };
});
