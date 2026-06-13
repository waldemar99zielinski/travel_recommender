import { useEffect, type ReactNode } from "react";

import { DestinationContext } from "@/shared/context/destination/destinationContext";
import { useDestinationContextValue } from "@/shared/context/destination/useDestinationContextValue";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "DestinationContextProvider" });

type DestinationContextProviderProps = {
    children: ReactNode;
};

export function DestinationContextProvider({
    children,
}: DestinationContextProviderProps) {
    const contextValue = useDestinationContextValue();

    useEffect(() => {
        const loadDestinations = async () => {
            logger.trace("Fetching travel destinations...");

            await contextValue.fetchDestinations();

            if (contextValue.destinationsError) {
                throw new Error(
                    `Failed to load travel destinations: ${contextValue.destinationsError}`,
                );
            }

            logger.debug("Travel destinations loaded", {
                count: Object.keys(contextValue.destinationsById).length,
                status: contextValue.destinationsStatus,
                error: contextValue.destinationsError,
            });
        };

        void loadDestinations();
    }, []);

    return (
        <DestinationContext.Provider value={contextValue}>
            {children}
        </DestinationContext.Provider>
    );
}
