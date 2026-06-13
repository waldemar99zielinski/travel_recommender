import { useCallback } from "react";

import { useSessionContext } from "@/shared/context";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "useRecommendationSession" });

export interface UseRecommendationSessionReturn {
    startNewSession: () => Promise<void>;
    createSessionStatus: "idle" | "loading" | "success" | "error";
    createSessionError: string | null;
    getSessionStatus: "idle" | "loading" | "success" | "error";
    getSessionError: string | null;
}

export function useRecommendationSession(): UseRecommendationSessionReturn {
    const {
        createSession,
        createSessionStatus,
        createSessionError,
        getSession,
        getSessionStatus,
        getSessionError,
    } = useSessionContext();

    const startNewSession = useCallback(async () => {
        logger.debug("Starting new recommendation session");

        const session = await createSession();
        if (session == null) {
            logger.error("Failed to create new session");
            return;
        }

    }, [createSession, getSession]);

    return {
        startNewSession,
        createSessionStatus,
        createSessionError,
        getSessionStatus,
        getSessionError,
    };
}
