import { useContext } from "react";

import { AppContext } from "@/shared/context/appContext";

export function useAppContext() {
    const context = useContext(AppContext);

    if (context == null) {
        throw new Error("useAppContext must be used within AppContextProvider");
    }

    return context;
}
