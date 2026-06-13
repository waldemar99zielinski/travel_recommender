import { type ReactNode } from "react";

import {
    appConfiguration,
} from "@/shared/configuration/appConfiguration";
import { AppConfigContext } from "@/shared/context/app-config/appConfigContext";

type AppConfigContextProviderProps = {
    children: ReactNode;
};

export function AppConfigContextProvider({ children }: AppConfigContextProviderProps) {

    const contextValue = {
        config: appConfiguration,
    }

    return (
        <AppConfigContext.Provider value={contextValue}>
            {children}
        </AppConfigContext.Provider>
    );
}
