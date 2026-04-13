import { useContext } from "react";

import { UserContext } from "@/shared/context/user/userContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "useUserContext" });

export function useUserContext() {
    const context = useContext(UserContext);

    if (context == null) {
        logger.error("UserContext is missing in component tree");
        throw new Error("useUserContext must be used within UserContextProvider");
    }

    return context;
}
