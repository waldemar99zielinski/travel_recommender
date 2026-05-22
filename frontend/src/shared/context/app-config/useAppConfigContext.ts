import { useContext } from "react";

import { AppConfigContext } from "@/shared/context/app-config/appConfigContext";

export function useAppConfigContext() {
    const contextValue = useContext(AppConfigContext);

    if (contextValue === undefined) {
        throw new Error("useAppConfigContext must be used within AppConfigContextProvider");
    }

    return contextValue;
}
