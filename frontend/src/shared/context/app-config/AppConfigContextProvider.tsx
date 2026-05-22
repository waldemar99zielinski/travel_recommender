import { useCallback, useMemo, useState, type ReactNode } from "react";

import {
    appConfiguration,
    type AppConfiguration,
    type RecommendationApiVersion,
} from "@/shared/configuration";
import { AppConfigContext } from "@/shared/context/app-config/appConfigContext";
import { browserStorage, STORAGE_KEYS } from "@/shared/storage";

type AppConfigContextProviderProps = {
    children: ReactNode;
};

function loadStoredRecommendationApiVersion(): RecommendationApiVersion | null {
    const rawValue = browserStorage.getItem(STORAGE_KEYS.recommendationApiVersion);

    if (rawValue === "v1" || rawValue === "v2" || rawValue === "v3") {
        return rawValue;
    }

    return null;
}

export function AppConfigContextProvider({ children }: AppConfigContextProviderProps) {
    const [recommendationApiVersion, setRecommendationApiVersionState] =
        useState<RecommendationApiVersion>(
            () =>
                loadStoredRecommendationApiVersion() ??
                appConfiguration.recommendationApiVersion,
        );

    const setRecommendationApiVersion = useCallback(
        (nextRecommendationApiVersion: RecommendationApiVersion) => {
            setRecommendationApiVersionState(nextRecommendationApiVersion);
            browserStorage.setItem(
                STORAGE_KEYS.recommendationApiVersion,
                nextRecommendationApiVersion,
            );
        },
        [],
    );

    const resetRecommendationApiVersion = useCallback(() => {
        setRecommendationApiVersionState(appConfiguration.recommendationApiVersion);
        browserStorage.removeItem(STORAGE_KEYS.recommendationApiVersion);
    }, []);

    const config = useMemo<AppConfiguration>(
        () => ({
            ...appConfiguration,
            recommendationApiVersion,
        }),
        [recommendationApiVersion],
    );

    const contextValue = useMemo(
        () => ({
            config,
            setRecommendationApiVersion,
            resetRecommendationApiVersion,
        }),
        [config, resetRecommendationApiVersion, setRecommendationApiVersion],
    );

    return (
        <AppConfigContext.Provider value={contextValue}>
            {children}
        </AppConfigContext.Provider>
    );
}
