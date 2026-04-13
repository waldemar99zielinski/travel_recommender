import type { ReactNode } from "react";

import {
    UserContext,
    type UserContextValue,
} from "@/shared/context/user/userContext";
import { useUserContextValue } from "@/shared/context/user/useUserContextValue";

type UserContextProviderProps = {
    children: ReactNode;
    value?: UserContextValue;
};

export function UserContextProvider({
    children,
    value,
}: UserContextProviderProps) {
    const internalValue = useUserContextValue();

    return (
        <UserContext.Provider value={value ?? internalValue}>
            {children}
        </UserContext.Provider>
    );
}
