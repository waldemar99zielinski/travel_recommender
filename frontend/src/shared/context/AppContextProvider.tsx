import { useMemo, type ReactNode } from "react";

import { AppContext, type AppContextValue } from "@/shared/context/appContext";

type AppContextProviderProps = {
    children: ReactNode;
};

export function AppContextProvider({ children }: AppContextProviderProps) {
    const value = useMemo<AppContextValue>(() => ({}), []);

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
