import { apiConfig } from "@/shared/api/config.api";

export interface HealthApiUrlBuilder {
    fetchHealth(): string;
}

export interface RecommendationApiUrlBuilder {
    fetchRecommendations(): string;
}

export interface SessionApiUrlBuilder {
    createSession(): string;
    getSession(userId: string, sessionId: string): string;
    removeSession(userId: string, sessionId: string): string;
}

export function createHealthApiUrlBuilder(baseUrl: string): HealthApiUrlBuilder {
    return {
        fetchHealth: () => `${baseUrl}/health`,
    };
}

export function createRecommendationApiUrlBuilder(
    baseUrl: string,
): RecommendationApiUrlBuilder {
    return {
        fetchRecommendations: () => `${baseUrl}/api/v1/recommendations/chat`,
    };
}

export function createSessionApiUrlBuilder(baseUrl: string): SessionApiUrlBuilder {
    return {
        createSession: () => `${baseUrl}/api/v1/sessions`,
        getSession: (userId: string, sessionId: string) =>
            `${baseUrl}/api/v1/sessions/${encodeURIComponent(userId)}/${encodeURIComponent(sessionId)}`,
        removeSession: (userId: string, sessionId: string) =>
            `${baseUrl}/api/v1/sessions/${encodeURIComponent(userId)}/${encodeURIComponent(sessionId)}`,
    };
}

export const sessionApiUrlBuilder = createSessionApiUrlBuilder(apiConfig.baseUrl);
export const healthApiUrlBuilder = createHealthApiUrlBuilder(apiConfig.baseUrl);
export const recommendationApiUrlBuilder = createRecommendationApiUrlBuilder(
    apiConfig.baseUrl,
);
