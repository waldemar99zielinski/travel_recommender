import { useContext } from "react";

import { HealthContext } from "@/shared/context/health/healthContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "useHealthContext" });

export function useHealthContext() {
    const context = useContext(HealthContext);

    if (context == null) {
        logger.error("HealthContext is missing in component tree");
        throw new Error("useHealthContext must be used within HealthContextProvider");
    }

    return context;
}
