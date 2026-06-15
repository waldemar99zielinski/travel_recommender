declare global {
    interface Window {
        __APP_CONFIG__?: {
            environment?: "dev" | "production";
            baseUrl?: string;
            regionsDataUrl?: string;
            surveyEnabled?: boolean | string;
        };
    }
}

export {};
