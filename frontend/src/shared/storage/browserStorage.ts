export interface BrowserStorage {
    getItem: (key: string) => string | null;
    setItem: (key: string, value: string) => void;
    removeItem: (key: string) => void;
}

function getLocalStorage(): Storage | null {
    if (typeof window === "undefined") {
        return null;
    }

    try {
        return window.localStorage;
    } catch {
        return null;
    }
}

export const browserStorage: BrowserStorage = {
    getItem: (key: string) => {
        const storage = getLocalStorage();
        if (storage == null) {
            return null;
        }

        try {
            return storage.getItem(key);
        } catch {
            return null;
        }
    },
    setItem: (key: string, value: string) => {
        const storage = getLocalStorage();
        if (storage == null) {
            return;
        }

        try {
            storage.setItem(key, value);
        } catch {
            return;
        }
    },
    removeItem: (key: string) => {
        const storage = getLocalStorage();
        if (storage == null) {
            return;
        }

        try {
            storage.removeItem(key);
        } catch {
            return;
        }
    },
};
