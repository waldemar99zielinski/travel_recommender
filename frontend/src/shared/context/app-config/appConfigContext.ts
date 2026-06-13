import { createContext } from "react";

import type {
    AppConfiguration,
} from "@/shared/configuration";

export interface AppConfigContextValue {
    config: AppConfiguration;
}

export const AppConfigContext =
    createContext<AppConfigContextValue | undefined>(undefined);
