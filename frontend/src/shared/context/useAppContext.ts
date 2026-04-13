import { useContext } from "react";

import { AppContext } from "@/shared/context/appContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "useAppContext" });

export function useAppContext() {
    const context = useContext(AppContext);

    if (context == null) {
        logger.error("AppContext is missing in component tree");
        throw new Error("useAppContext must be used within AppContextProvider");
    }

    return context;
}
