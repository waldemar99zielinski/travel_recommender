import type { ReactNode } from "react";

import { AppConfigContextProvider } from "@/shared/context/app-config/AppConfigContextProvider";
import { HealthContextProvider } from "@/shared/context/health/HealthContextProvider";
import { SessionContextProvider } from "@/shared/context/session/SessionContextProvider";

type AppContextProviderProps = {
    children: ReactNode;
};

export function AppContextProvider({ children }: AppContextProviderProps) {
    return (
        <AppConfigContextProvider>
            <HealthContextProvider>
                <SessionContextProvider>{children}</SessionContextProvider>
            </HealthContextProvider>
        </AppConfigContextProvider>
    );
}
