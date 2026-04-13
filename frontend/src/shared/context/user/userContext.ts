import { createContext } from "react";

import type { SessionRefDto } from "@/models/session.models";

export interface UserContextValue {
    userId: string;
    session: SessionRefDto;
    setUserId: (userId: string) => void;
}

export const UserContext = createContext<UserContextValue | undefined>(
    undefined,
);
