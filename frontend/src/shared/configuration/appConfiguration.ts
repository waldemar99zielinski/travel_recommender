export type AppEnvironment = "dev" | "production";
export type RecommendationApiVersion = "v1" | "v2" | "v3";

export interface AppConfiguration {
    environment: AppEnvironment;
    version: string;
    recommendationApiVersion: RecommendationApiVersion;
}

function resolveEnvironment(): AppEnvironment {
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
    recommendationApiVersion: "v3",
};
