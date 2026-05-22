import { createElement, useCallback, useEffect, useMemo, useRef, useState } from "react";

import type { ChatMessage } from "@/components/chat/Chat.interfaces";
import type { ChatMessageDto as RecommendationChatMessageDto } from "@/models/chat-message.models";
import type {
    RecommendationItemDto,
    RecommendationResponseDto,
} from "@/models/recommendation.models";
import { RecommendationResultsMessage } from "@/features/recommendation/chat/components/RecommendationResultsMessage";
import type { RecommendationFeatureContextValue } from "@/features/recommendation/recommendationFeatureContext";
import type {
    SessionHistoryTurnDto,
    SessionDto,
    SessionStateResponseDto,
} from "@/models/session.models";
import { useRecommendationsApi } from "@/shared/hooks/useRecommendationsApi";
import { useSessionContext } from "@/shared/context";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "RecommendationFeatureContext" });
const CHAT_RECOMMENDATION_RESULT_LIMIT = 10;

function createChatMessageId(turnNumber: number, role: "user" | "assistant"): string {
    return `chat-${turnNumber}-${role}`;
}

function createAssistantChatMessageId(turnNumber: number, messageIndex: number): string {
    return `chat-${turnNumber}-assistant-${messageIndex}`;
}

function createRecommendationResultsMessageId(turnNumber: number): string {
    if (turnNumber < 0) {
        return "chat-session-recommendations";
    }

    return `chat-${turnNumber}-recommendations`;
}

function mapRecommendationChatMessageToChatMessage(
    chatHistoryNumber: number,
    message: RecommendationChatMessageDto,
    messageIndex: number,
): ChatMessage {
    return {
        id: createAssistantChatMessageId(chatHistoryNumber, messageIndex),
        role: "assistant",
        content: message.context.text,
    };
}

function createAssistantChatMessages(
    chatHistoryNumber: number,
    messages: RecommendationChatMessageDto[],
): ChatMessage[] {
    return messages.map((message, messageIndex) =>
        mapRecommendationChatMessageToChatMessage(chatHistoryNumber, message, messageIndex),
    );
}

function createChatMessages(history: SessionHistoryTurnDto[]): ChatMessage[] {
    return history.flatMap((turn) => [
        {
            id: createChatMessageId(turn.chat_history_number, "user"),
            role: "user" as const,
            content: turn.user_request,
        },
        ...createAssistantChatMessages(turn.chat_history_number, turn.system_messages),
    ]);
}

function createChatMessage(
    turnNumber: number,
    role: "user" | "assistant",
    content: string,
): ChatMessage {
    return {
        id: createChatMessageId(turnNumber, role),
        role,
        content,
    };
}

function createRecommendationResultsMessage(
    turnNumber: number,
    recommendations: RecommendationItemDto[],
): ChatMessage | null {
    if (recommendations.length === 0) {
        return null;
    }

    return {
        id: createRecommendationResultsMessageId(turnNumber),
        role: "assistant",
        content: createElement(RecommendationResultsMessage, {
            recommendations,
            limit: CHAT_RECOMMENDATION_RESULT_LIMIT,
        }),
    };
}

function appendRecommendationResultsMessage(
    messages: ChatMessage[],
    turnNumber: number,
    recommendations: RecommendationItemDto[],
): ChatMessage[] {
    const recommendationResultsMessage = createRecommendationResultsMessage(
        turnNumber,
        recommendations,
    );

    return recommendationResultsMessage == null
        ? messages
        : [...messages, recommendationResultsMessage];
}

function createSessionKey(session: SessionDto | null | undefined): string | null {
    if (session == null) {
        return null;
    }

    return `${session.user_id}:${session.session_id}`;
}

function createRecommendationResponse(
    sessionState: SessionStateResponseDto,
): RecommendationResponseDto | null {
    if (
        sessionState.history.length === 0 &&
        sessionState.last_recommendation_result.length === 0
    ) {
        return null;
    }

    return {
        messages:
            sessionState.history[sessionState.history.length - 1]?.system_messages ?? [],
        recommendations: sessionState.last_recommendation_result,
    };
}

export function useRecommendationFeatureContextValue(): RecommendationFeatureContextValue {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [lastChatHistoryNumber, setLastChatHistoryNumber] = useState(-1);
    const [recommendationResponse, setRecommendationResponse] =
        useState<RecommendationResponseDto | null>(null);
    const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);
    const [focusedRegionId, setFocusedRegionId] = useState<string | null>(null);
    const [, recommendationsStatus, recommendationsError, fetchRecommendationsData] =
        useRecommendationsApi();
    const {
        session,
        createSession,
        ensureSession,
        createSessionStatus,
        createSessionError,
        getSession,
        getSessionStatus,
        getSessionError,
    } = useSessionContext();
    const initialSessionKeyRef = useRef<string | null>(createSessionKey(session));
    const hydratedSessionKeyRef = useRef<string | null>(null);

    const         resetRecommendationState = useCallback(() => {
        setMessages([]);
        setLastChatHistoryNumber(-1);
        setRecommendationResponse(null);
        setSelectedRegionId(null);
        setFocusedRegionId(null);
    }, []);

    useEffect(() => {
        let isCancelled = false;
        const initialSessionKey = initialSessionKeyRef.current;
        const activeSessionKey = createSessionKey(session);

        const hydrateRecommendationState = async () => {
            if (session == null) {
                resetRecommendationState();
                return;
            }

            if (
                initialSessionKey == null ||
                activeSessionKey !== initialSessionKey ||
                hydratedSessionKeyRef.current === activeSessionKey
            ) {
                return;
            }

            logger.trace("Hydrating recommendation session state", {
                session,
            });

            const response = await getSession(session);
            if (isCancelled) {
                return;
            }

            hydratedSessionKeyRef.current = activeSessionKey;

            if (response == null) {
                resetRecommendationState();

                logger.debug("Recommendation session state not available", {
                    session,
                });

                return;
            }

            const nextLastChatHistoryNumber =
                response.history[response.history.length - 1]?.chat_history_number ?? -1;
            setMessages(
                appendRecommendationResultsMessage(
                    createChatMessages(response.history),
                    nextLastChatHistoryNumber,
                    response.last_recommendation_result,
                ),
            );
            setLastChatHistoryNumber(nextLastChatHistoryNumber);
            setRecommendationResponse(createRecommendationResponse(response));

            logger.debug("Hydrated recommendation session state", {
                session: response.session,
                historyLength: response.history.length,
                lastRecommendationCount: response.last_recommendation_result.length,
            });
        };

        void hydrateRecommendationState();

        return () => {
            isCancelled = true;
        };
    }, [getSession, resetRecommendationState, session]);

    useEffect(() => {
        setSelectedRegionId(recommendationResponse?.recommendations[0]?.id ?? null);
    }, [recommendationResponse]);

    const startNewSession = useCallback(async (): Promise<void> => {
        logger.trace("Starting new recommendation session", {
            currentSession: session,
        });

        const nextSession = await createSession();
        if (nextSession == null) {
            throw new Error("Failed to create a new session");
        }

        resetRecommendationState();

        logger.debug("Started new recommendation session", {
            session: nextSession,
        });
    }, [createSession, resetRecommendationState, session]);

    const submitRecommendationMessage = useCallback(
        async (message: string): Promise<RecommendationResponseDto | null> => {
            const userMessage = message.trim();
            if (userMessage.length === 0) {
                logger.debug("Ignored empty recommendation message submit");
                return null;
            }

            const activeSession = session ?? (await ensureSession());

            logger.trace("Submitting recommendation message", {
                userId: activeSession.user_id,
                sessionId: activeSession.session_id,
                messageLength: userMessage.length,
            });

            const nextChatHistoryNumber = lastChatHistoryNumber + 1;
            setMessages((previous) => [
                ...previous,
                createChatMessage(nextChatHistoryNumber, "user", userMessage),
            ]);
            setLastChatHistoryNumber(nextChatHistoryNumber);

            const response = await fetchRecommendationsData({
                ...activeSession,
                message: userMessage,
            });

            if (response == null) {
                logger.warn("Recommendation response missing after submit");
                return null;
            }

            setMessages((previous) => [
                ...previous,
                ...appendRecommendationResultsMessage(
                    createAssistantChatMessages(nextChatHistoryNumber, response.messages),
                    nextChatHistoryNumber,
                    response.recommendations,
                ),
            ]);
            setRecommendationResponse(response);

            logger.debug("Stored recommendation response", {
                response,
                chatHistoryNumber: nextChatHistoryNumber,
                selectedRecommendationId: response.recommendations[0]?.id ?? null,
            });

            return response;
        },
        [ensureSession, fetchRecommendationsData, lastChatHistoryNumber, session],
    );

    const isLoading =
        recommendationsStatus === "loading" ||
        createSessionStatus === "loading" ||
        getSessionStatus === "loading";
    const errorMessage =
        recommendationsError ?? createSessionError ?? getSessionError;

    return useMemo(
        () => ({
            messages,
            recommendationResponse,
            selectedRegionId,
            setSelectedRegionId,
            focusedRegionId,
            setFocusedRegionId,
            startNewSession,
            submitRecommendationMessage,
            recommendationsStatus,
            recommendationsError,
            isLoading,
            errorMessage,
        }),
        [
            messages,
            recommendationResponse,
            selectedRegionId,
            focusedRegionId,
            startNewSession,
            submitRecommendationMessage,
            recommendationsStatus,
            recommendationsError,
            isLoading,
            errorMessage,
        ],
    );
}
