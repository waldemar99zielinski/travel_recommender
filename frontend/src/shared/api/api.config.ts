export interface ApiConfig {
    baseUrl: string;
    regionsDataUrl: string;
}

export const apiConfig: ApiConfig = {
    baseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080",
    regionsDataUrl: import.meta.env.VITE_REGIONS_DATA_URL ?? "/regions.json",
};
