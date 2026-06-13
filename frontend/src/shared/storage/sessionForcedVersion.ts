import { browserStorage } from "@/shared/storage/browserStorage";
import { STORAGE_KEYS } from "@/shared/storage/storageKeys";

export const sessionForcedVersionStorage = {
    set: (version: string): void => {
        browserStorage.setItem(STORAGE_KEYS.forceSessionVersion, version.trim());
    },
    get: (): string | null => {
        const value = browserStorage.getItem(STORAGE_KEYS.forceSessionVersion);
        return value ? value.trim() : null;
    },
    clear: (): void => {
        browserStorage.removeItem(STORAGE_KEYS.forceSessionVersion);
    },
};