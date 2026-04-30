import { useEffect, type ReactNode } from "react";

import {
    HealthContext,
    type HealthContextValue,
} from "@/shared/context/health/healthContext";
import { useHealthContextValue } from "@/shared/context/health/useHealthContextValue";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "HealthContextProvider" });

type HealthContextProviderProps = {
    children: ReactNode;
    value?: HealthContextValue;
};

export function HealthContextProvider({
    children,
    value,
}: HealthContextProviderProps) {
    const internalValue = useHealthContextValue();
    const contextValue = value ?? internalValue;

    useEffect(() => {
        const runInitialHealthCheck = async () => {
            logger.trace("Triggering initial health check...")

            await contextValue.fetch();

            logger.trace("Initial health check completed", {
                status: contextValue.status,
                error: contextValue.error,
                isOperational: contextValue.isOperational,
            });
        };

        runInitialHealthCheck();
    }, []);

    return (
        <HealthContext.Provider value={contextValue}>
            {children}
        </HealthContext.Provider>
    );
}
