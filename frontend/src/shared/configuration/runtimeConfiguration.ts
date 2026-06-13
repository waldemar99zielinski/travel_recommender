import type { AppEnvironment } from "@/shared/configuration/appConfiguration";

export interface RuntimeConfiguration {
    environment?: AppEnvironment;
    baseUrl?: string;
    regionsDataUrl?: string;
}

function resolveRuntimeConfiguration(): RuntimeConfiguration {
    if (typeof window === "undefined") {
        return {};
    }

    return window.__APP_CONFIG__ ?? {};
}

export const runtimeConfiguration = resolveRuntimeConfiguration();
