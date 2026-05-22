import type { SessionDto } from "@/models/session.models";
import { browserStorage } from "@/shared/storage/browserStorage";
import { STORAGE_KEYS } from "@/shared/storage/storageKeys";

function isSessionRefDto(value: unknown): value is SessionDto {
    if (value == null || typeof value !== "object") {
        return false;
    }

    const payload = value as Record<string, unknown>;
    return (
        typeof payload.user_id === "string" &&
        payload.user_id.trim().length > 0 &&
        typeof payload.session_id === "string" &&
        payload.session_id.trim().length > 0
    );
}

export function parseSessionStorageValue(value: string | null): SessionDto | null {
    if (value == null) {
        return null;
    }

    try {
        const parsedValue: unknown = JSON.parse(value);
        if (!isSessionRefDto(parsedValue)) {
            return null;
        }

        return {
            user_id: parsedValue.user_id.trim(),
            session_id: parsedValue.session_id.trim(),
        };
    } catch {
        return null;
    }
}

export const sessionStorage = {
    load: (): SessionDto | null => {
        const rawValue = browserStorage.getItem(STORAGE_KEYS.currentSession);
        return parseSessionStorageValue(rawValue);
    },
    save: (session: SessionDto): void => {
        const normalizedSession: SessionDto = {
            user_id: session.user_id.trim(),
            session_id: session.session_id.trim(),
        };

        browserStorage.setItem(
            STORAGE_KEYS.currentSession,
            JSON.stringify(normalizedSession),
        );
    },
    clear: (): void => {
        browserStorage.removeItem(STORAGE_KEYS.currentSession);
    },
};
