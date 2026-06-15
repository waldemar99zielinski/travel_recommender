import {
    apiConfig,
} from "@/shared/api/config.api";
import type { RecommendationApiVersion } from "@/shared/configuration";

export interface DestinationApiUrlBuilder {
    listDestinations(): string;
}

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

export interface SurveyApiUrlBuilder {
    listQuestions(): string;
    createResult(): string;
}

export function createDestinationApiUrlBuilder(baseUrl: string): DestinationApiUrlBuilder {
    return {
        listDestinations: () => `${baseUrl}/api/v1/destinations`,
    };
}

export function createHealthApiUrlBuilder(baseUrl: string): HealthApiUrlBuilder {
    return {
        fetchHealth: () => `${baseUrl}/health`,
    };
}

export function createRecommendationApiUrlBuilder(
    baseUrl: string,
    recommendationApiVersion: RecommendationApiVersion,
): RecommendationApiUrlBuilder {
    return {
        fetchRecommendations: () =>
            `${baseUrl}/api/${recommendationApiVersion}/recommendations/chat`,
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

export function createSurveyApiUrlBuilder(baseUrl: string): SurveyApiUrlBuilder {
    return {
        listQuestions: () => `${baseUrl}/api/v1/survey/questions`,
        createResult: () => `${baseUrl}/api/v1/survey/results`,
    };
}

export const destinationApiUrlBuilder = createDestinationApiUrlBuilder(apiConfig.baseUrl);
export const sessionApiUrlBuilder = createSessionApiUrlBuilder(apiConfig.baseUrl);
export const healthApiUrlBuilder = createHealthApiUrlBuilder(apiConfig.baseUrl);
export const surveyApiUrlBuilder = createSurveyApiUrlBuilder(apiConfig.baseUrl);
