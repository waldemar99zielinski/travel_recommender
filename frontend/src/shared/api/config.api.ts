export interface ApiConfig {
    baseUrl: string;
    regionsDataUrl: string;
}

export const apiConfig: ApiConfig = {
    baseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000",
    regionsDataUrl: import.meta.env.VITE_REGIONS_DATA_URL ?? "/regions.json",
};
