import type { ReactNode } from "react";

import {
    SessionContext,
    type SessionContextValue,
} from "@/shared/context/session/sessionContext";
import { useSessionContextValue } from "@/shared/context/session/useSessionContextValue";

type SessionContextProviderProps = {
    children: ReactNode;
    value?: SessionContextValue;
};

export function SessionContextProvider({
    children,
    value,
}: SessionContextProviderProps) {
    const internalValue = useSessionContextValue();

    return (
        <SessionContext.Provider value={value ?? internalValue}>
            {children}
        </SessionContext.Provider>
    );
}
