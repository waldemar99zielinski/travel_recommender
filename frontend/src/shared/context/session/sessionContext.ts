import { createContext } from "react";

import type {
    SessionDeleteResponseDto,
    SessionDto,
    SessionStateResponseDto,
    SessionVersion,
} from "@/models/session.models";
import type { ChatRecordDto } from "@/models/chat.models";
import type { FetchStatus } from "@/shared/hooks/apiHookTypes";

export interface SessionContextValue {
    session: SessionDto | null;
    createSessionData: SessionDto | null;
    createSessionStatus: FetchStatus;
    createSessionError: string | null;
    createSession: (userId?: string) => Promise<SessionDto | null>;
    ensureSession: (userId?: string) => Promise<SessionDto>;
    getSessionData: SessionStateResponseDto | null;
    getSessionStatus: FetchStatus;
    getSessionError: string | null;
    getSession: (session?: SessionDto | null) => Promise<SessionStateResponseDto | null>;
    removeSessionData: SessionDeleteResponseDto | null;
    removeSessionStatus: FetchStatus;
    removeSessionError: string | null;
    removeSession: (
        session?: SessionDto | null,
    ) => Promise<SessionDeleteResponseDto | null>;

    forcedSessionVersion: SessionVersion | null;
    setForcedSessionVersion: (version: SessionVersion | null) => void;
    sessionChatHistory: ChatRecordDto[];
}

export const SessionContext =
    createContext<SessionContextValue | undefined>(undefined);
