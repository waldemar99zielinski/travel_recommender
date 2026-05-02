import { useContext } from "react";

import { SessionContext } from "@/shared/context/session/sessionContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "useSessionContext" });

export function useSessionContext() {
    const context = useContext(SessionContext);

    if (context == null) {
        logger.error("SessionContext is missing in component tree");
        throw new Error("useSessionContext must be used within SessionContextProvider");
    }

    return context;
}
