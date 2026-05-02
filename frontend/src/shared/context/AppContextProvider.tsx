import type { ReactNode } from "react";

import { HealthContextProvider } from "@/shared/context/health/HealthContextProvider";
import { RecommendationContextProvider } from "@/shared/context/recommendation/RecommendationContextProvider";
import { SessionContextProvider } from "@/shared/context/session/SessionContextProvider";

type AppContextProviderProps = {
    children: ReactNode;
};

export function AppContextProvider({ children }: AppContextProviderProps) {
    return (
        <HealthContextProvider>
            <SessionContextProvider>
                <RecommendationContextProvider>
                    {children}
                </RecommendationContextProvider>
            </SessionContextProvider>
        </HealthContextProvider>
    );
}
