import { useCallback, useState } from "react";

import type {
    SessionDeleteResponseDto,
    SessionDto,
    SessionStateResponseDto,
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

const logger = createLogger({ scope: "SessionContext" });

function isSameSession(
    left: SessionDto | null | undefined,
    right: SessionDto | null | undefined,
): boolean {
    if (left == null || right == null) {
        return left == null && right == null;
    }

    return left.user_id === right.user_id && left.session_id === right.session_id;
}

export function useSessionContextValue(): SessionContextValue {
    const [session, setSession] = useState<SessionDto | null>(() => sessionStorage.load());

    const createSessionHandler = useCallback(async (userId?: string) => {
        const response = await createSessionRequest({
            user_id: userId ?? session?.user_id,
        });

        logger.debug("Created recommendation session", {
            session: response.session,
        });
        if (!isSameSession(session, response.session)) {
            setSession(response.session);
        }
        sessionStorage.save(response.session);
        return response.session;
    }, [session]);

    const [createSessionData, createSessionStatus, createSessionError, createSession] =
        useApiRequest<SessionDto, string>(createSessionHandler, {
            requestName: "createSession",
        });

    const ensureSession = useCallback(
        async (userId?: string): Promise<SessionDto> => {
            if (session != null) {
                logger.trace("Session already active, skipping session creation");
                return session;
            }

            const createdSession = await createSession(userId);
            if (createdSession == null) {
                throw new Error("Failed to create session");
            }

            return createdSession;
        },
        [createSession, session],
    );

    const getSessionHandler = useCallback(
        async (requestedSession?: SessionDto | null) => {
            const targetSession = requestedSession ?? session;
            if (targetSession == null) {
                logger.debug("Get session skipped because no session is active");
                return null;
            }

            const response = await getSessionRequest(targetSession);
            if (response == null) {
                logger.debug("Session state not found", {
                    session: targetSession,
                });

                if (isSameSession(session, targetSession)) {
                    sessionStorage.clear();
                    setSession(null);
                }

                return null;
            }

            if (!isSameSession(session, response.session)) {
                setSession(response.session);
            }

            sessionStorage.save(response.session);

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

    const removeSessionHandler = useCallback(
        async (
            requestedSession?: SessionDto | null,
        ): Promise<SessionDeleteResponseDto | null> => {
            const targetSession = requestedSession ?? session;
            if (targetSession == null) {
                logger.debug("Remove session skipped because no session is active");
                sessionStorage.clear();
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
    };
}
