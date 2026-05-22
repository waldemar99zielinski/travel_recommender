import { createContext } from "react";

import type {
    AppConfiguration,
    RecommendationApiVersion,
} from "@/shared/configuration";

export interface AppConfigContextValue {
    config: AppConfiguration;
    setRecommendationApiVersion: (version: RecommendationApiVersion) => void;
    resetRecommendationApiVersion: () => void;
}

export const AppConfigContext =
    createContext<AppConfigContextValue | undefined>(undefined);
