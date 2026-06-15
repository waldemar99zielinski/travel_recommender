import type { ReactNode } from "react";

import { AppConfigContextProvider } from "@/shared/context/app-config/AppConfigContextProvider";
import { DestinationContextProvider } from "@/shared/context/destination/DestinationContextProvider";
import { HealthContextProvider } from "@/shared/context/health/HealthContextProvider";
import { SessionContextProvider } from "@/shared/context/session/SessionContextProvider";
import { SurveyContextProvider } from "@/shared/context/survey/SurveyContextProvider";

type AppContextProviderProps = {
    children: ReactNode;
};

export function AppContextProvider({ children }: AppContextProviderProps) {
    return (
        <AppConfigContextProvider>
            <HealthContextProvider>
                <DestinationContextProvider>
                    <SessionContextProvider>
                        <SurveyContextProvider>{children}</SurveyContextProvider>
                    </SessionContextProvider>
                </DestinationContextProvider>
            </HealthContextProvider>
        </AppConfigContextProvider>
    );
}
