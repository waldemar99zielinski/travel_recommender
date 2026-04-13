import path from "node:path";
import { readFileSync } from "node:fs";

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const packageJson = JSON.parse(
    readFileSync(path.resolve(__dirname, "./package.json"), "utf-8"),
) as { version?: string };
const appVersion = packageJson.version ?? "0.0.0";

// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    define: {
        __APP_VERSION__: JSON.stringify(appVersion),
    },
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
});
