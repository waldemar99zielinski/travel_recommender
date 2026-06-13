import { useContext } from "react";

import { DestinationContext } from "@/shared/context/destination/destinationContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "useDestinationContext" });

export function useDestinationContext() {
    const context = useContext(DestinationContext);

    if (context == null) {
        logger.error("DestinationContext is missing in component tree");
        throw new Error(
            "useDestinationContext must be used within DestinationContextProvider",
        );
    }

    return context;
}
