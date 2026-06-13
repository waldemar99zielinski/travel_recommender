import { runtimeConfiguration } from "@/shared/configuration/runtimeConfiguration";

export type AppEnvironment = "dev" | "production";

export interface AppConfiguration {
    environment: AppEnvironment;
    version: string;
}

function resolveEnvironment(): AppEnvironment {
    if (runtimeConfiguration.environment === "dev") {
        return "dev";
    }

    if (runtimeConfiguration.environment === "production") {
        return "production";
    }

    const mode = import.meta.env.MODE;

    if (mode === "development" || mode === "dev") {
        return "dev";
    }

    if (mode === "production") {
        return "production";
    }

    return "production";
}

export const appConfiguration: AppConfiguration = {
    environment: resolveEnvironment(),
    version: __APP_VERSION__,
};
