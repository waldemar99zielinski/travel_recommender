import { useCallback, useState } from "react";

import type {
    SessionDeleteResponseDto,
    SessionDto,
    SessionStateResponseDto,
    SessionVersion,
} from "@/models/session.models";
import {
    createSession as createSessionRequest,
    getSession as getSessionRequest,
    removeSession as removeSessionRequest,
} from "@/shared/api/session.api";
import type { SessionContextValue } from "@/shared/context/session/sessionContext";
import { useApiRequest } from "@/shared/hooks/useApiRequest";
import { createLogger } from "@/shared/lib";
import { sessionStorage } from "@/shared/storage";
import { sessionForcedVersionStorage } from "@/shared/storage/sessionForcedVersion";
import type { ChatRecordDto } from "@/models/chat.models";

const logger = createLogger({ scope: "SessionContext" });

export function useSessionContextValue(): SessionContextValue {
    const [session, setSession] = useState<SessionDto | null>(() => sessionStorage.load());
    const [sessionChatHistory, setSessionChatHistory] = useState<ChatRecordDto[]>([]);
    const [forcedSessionVersion, _setForceSessionVersion] = useState<SessionVersion | null>(() => sessionForcedVersionStorage.get() as SessionVersion | null);

    const createSessionHandler = useCallback(async (userId?: string) => {
        const response = await createSessionRequest({
            user_id: userId ?? session?.user_id,
        });

        logger.debug("Created recommendation session", {
            session: response.session,
        });

        setSessionChatHistory([]); 

        if (forcedSessionVersion != null) {
            logger.warn("Forcing session version with value", {
                version: forcedSessionVersion,
            })
            response.session.version = forcedSessionVersion;
        }

        sessionStorage.save(response.session);
        setSession(response.session);
        return response.session;
    }, [session, forcedSessionVersion]);

    const [createSessionData, createSessionStatus, createSessionError, createSession] =
        useApiRequest<SessionDto, string>(createSessionHandler, {
            requestName: "createSession",
        });

    const getSessionHandler = useCallback(
        async (requestedSession?: SessionDto | null) => {
            const targetSession = requestedSession ?? session;
            if (targetSession == null) {
               throw new Error("getSession called without active session");
            }

            const response = await getSessionRequest(targetSession);
            if (response == null) {
                logger.debug("Session state not found", {
                    session: targetSession,
                });

                setSession(targetSession);
                setSessionChatHistory([]);

                return {
                    session: targetSession,
                    chat_history: [],
                };
            }

            sessionStorage.save(response.session);
            setSession(response.session);
            setSessionChatHistory(response.chat_history);

            return response;
        },
        [session],
    );

    const [getSessionData, getSessionStatus, getSessionError, getSession] = useApiRequest<
        SessionStateResponseDto | null,
        SessionDto | null
    >(getSessionHandler, {
        requestName: "getSession",
    });

    const ensureSession = useCallback(
        async (userId?: string): Promise<SessionDto> => {
            if (session != null) {
                logger.trace("Session already active");
                
                if (getSessionStatus === "idle") {
                    logger.trace("Ensuring session by fetching session state");
                    await getSession(session);
                }

                return session;
            }

            const createdSession = await createSession(userId);
            if (createdSession == null) {
                throw new Error("Failed to create session");
            }

            return createdSession;
        },
        [createSession, session, getSession, getSessionStatus],
    );

    const removeSessionHandler = useCallback(
        async (
            requestedSession?: SessionDto | null,
        ): Promise<SessionDeleteResponseDto | null> => {
            const targetSession = requestedSession ?? session;
            if (targetSession == null) {
                logger.debug("Remove session skipped because no session is active");
                sessionStorage.clear();
                setSessionChatHistory([]);
                setSession(null);
                return null;
            }

            try {
                const response = await removeSessionRequest(targetSession);
                logger.debug("Removed recommendation session", {
                    session: response.session,
                });
                return response;
            } finally {
                sessionStorage.clear();
                setSessionChatHistory([]);
                setSession(null);
            }
        },
        [session],
    );

    const [removeSessionData, removeSessionStatus, removeSessionError, removeSession] =
        useApiRequest<SessionDeleteResponseDto | null, SessionDto | null>(
            removeSessionHandler,
            {
                requestName: "removeSession",
            },
        );

    const setForcedSessionVersion = useCallback((version: SessionVersion | null) => {
        if (version == null) {
            sessionForcedVersionStorage.clear();
            _setForceSessionVersion(null);
            logger.info("Cleared forced session version");
        } else {
            sessionForcedVersionStorage.set(version);
            _setForceSessionVersion(version);
            logger.info("Set forced session version", { version });
        }
    }, [_setForceSessionVersion]);

    return {
        session,
        createSessionData,
        createSessionStatus,
        createSessionError,
        createSession,
        ensureSession,
        getSessionData,
        getSessionStatus,
        getSessionError,
        getSession,
        removeSessionData,
        removeSessionStatus,
        removeSessionError,
        removeSession,
        forcedSessionVersion,
        setForcedSessionVersion,
        sessionChatHistory: sessionChatHistory,
    };
}
