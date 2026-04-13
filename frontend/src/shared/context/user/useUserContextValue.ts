import { useMemo, useState } from "react";

import type { UserContextValue } from "@/shared/context/user/userContext";

function createUuidV4(): string {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
        return crypto.randomUUID();
    }

    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (char) => {
        const random = Math.floor(Math.random() * 16);
        const value = char === "x" ? random : (random & 0x3) | 0x8;

        return value.toString(16);
    });
}

export function useUserContextValue(): UserContextValue {
    const [userId, setUserId] = useState(() => createUuidV4());
    const [sessionId] = useState(() => {
        let id = createUuidV4();

        while (id === userId) {
            id = createUuidV4();
        }

        return id;
    });

    return useMemo(
        () => ({
            userId,
            session: {
                user_id: userId,
                session_id: sessionId,
            },
            setUserId,
        }),
        [userId, sessionId],
    );
}
