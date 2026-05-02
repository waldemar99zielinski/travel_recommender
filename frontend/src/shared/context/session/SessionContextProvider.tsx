import { useEffect, type ReactNode } from "react";

import { SessionContext } from "@/shared/context/session/sessionContext";
import { useSessionContextValue } from "@/shared/context/session/useSessionContextValue";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "SessionContextProvider" });

type SessionContextProviderProps = {
    children: ReactNode;
};

export function SessionContextProvider({ children }: SessionContextProviderProps) {
    const contextValue = useSessionContextValue();

    useEffect(() => {
        const initializeSession = async () => {
            try {
                logger.trace("Initializing session context provider");

                const activeSession = await contextValue.ensureSession();

                logger.debug("Initialized active session for chat flow", {
                    userId: activeSession.user_id,
                    sessionId: activeSession.session_id,
                });

            } catch (error) {
                logger.error("Failed to initialize session", error);
            }
        };

        void initializeSession();
    }, []);

    return (
        <SessionContext.Provider value={contextValue}>
            {children}
        </SessionContext.Provider>
    );
}
