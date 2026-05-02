import { useEffect, type ReactNode } from "react";

import { HealthContext } from "@/shared/context/health/healthContext";
import { useHealthContextValue } from "@/shared/context/health/useHealthContextValue";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "HealthContextProvider" });

type HealthContextProviderProps = {
    children: ReactNode;
};

export function HealthContextProvider({ children }: HealthContextProviderProps) {
    const contextValue = useHealthContextValue();

    useEffect(() => {
        const runInitialHealthCheck = async () => {
            logger.trace("Triggering initial health check...");

            await contextValue.fetchHealth();

            logger.trace("Initial health check completed", {
                status: contextValue.healthStatus,
                error: contextValue.healthError,
                isOperational: contextValue.isOperational,
            });
        };

        void runInitialHealthCheck();
    }, []);

    return (
        <HealthContext.Provider value={contextValue}>
            {children}
        </HealthContext.Provider>
    );
}
