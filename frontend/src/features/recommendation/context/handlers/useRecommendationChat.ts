import { useEffect, useEffectEvent, useState } from "react";

import type { ChatRecordDto } from "@/models/chat.models";
import type {
    RecommendationItemDto,
    RecommendationV2TravelDestinationEvaluationDto,
} from "@/models/recommendation.models";
import type {
    ProgressStage,
    RecommendationDestinationResearchEventData,
    TravelDestinationFilter,
} from "@/models/recommendation.stream.models";
import { streamRecommendations } from "@/shared/api/recommendation.api";
import { useSessionContext } from "@/shared/context";
import { useDestinationContext } from "@/shared/context/destination/useDestinationContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "useChat" });

function buildDestinationResearchStateByRegion(
    evaluations: RecommendationV2TravelDestinationEvaluationDto[] | undefined,
) {
    if (evaluations == null || evaluations.length === 0) {
        return {};
    }

    return Object.fromEntries(
        evaluations.map((evaluation) => [
            evaluation.region_id,
            {
                state: "done" as const,
                data: {
                    description: evaluation.description,
                    image_urls: evaluation.image_urls,
                },
            },
        ]),
    );
}

function buildDestinationResearchEvaluations(
    state: ReturnType<typeof buildDestinationResearchStateByRegion>,
): RecommendationV2TravelDestinationEvaluationDto[] {
    return Object.entries(state)
        .filter(([, entry]) => entry.data != null)
        .map(([regionId, entry]) => ({
            region_id: regionId,
            description: entry.data!.description,
            image_urls: entry.data!.image_urls,
        }));
}

export interface UseRecommendationChat {
    chatRecords: ChatRecordDto[];
    setChatRecords: React.Dispatch<React.SetStateAction<ChatRecordDto[]>>;

    step: ProgressStage;
    onGoingChatTurn: Partial<ChatRecordDto> | null;
    destinationResearchStarted: boolean;

    submitRecommendationMessage: (message: string) => Promise<void>;
}

interface UseRecommendationChatOptions {
    setIncludedRegionIds: (ids: string[]) => void;
    setExcludedRegionIds: (ids: string[]) => void;
}

export const STEP_LABELS: Record<string, string> = {
    initializing: "Starting…",
    validating_request: "Validating request…",
    gathering_filter: "Analyzing travel preferences…",
    recommendation_generation: "Generating recommendations…",
    desination_research_generation: "Researching recommended regions…",
    destination_research: "Researching recommended regions…",
    response_generation: "Preparing response…",
};

export function useRecommendationChat({
    setIncludedRegionIds,
    setExcludedRegionIds,
}: UseRecommendationChatOptions): UseRecommendationChat {
    const { ensureSession, session, sessionChatHistory } = useSessionContext();
    const [chatRecords, setChatRecords] = useState<ChatRecordDto[]>(sessionChatHistory);
    const [onGoingChatTurn, setOnGoingChatTurn] = useState<Partial<ChatRecordDto> | null>(null);
    const [step, setStep] = useState<ProgressStage>("idle");
    const [destinationResearchStarted, setDestinationResearchStarted] =
        useState(false);
    const destinationContext = useDestinationContext();
    const applyResolvedRegionFilters = useEffectEvent(
        (includedRegionIds: string[], excludedRegionIds: string[]) => {
            if (includedRegionIds.length > 0) {
                setIncludedRegionIds(includedRegionIds);
            }

            if (excludedRegionIds.length > 0) {
                setExcludedRegionIds(excludedRegionIds);
            }
        },
    );

    useEffect(() => {
        setChatRecords(sessionChatHistory);
        setOnGoingChatTurn(null);
        setStep("idle");
        setDestinationResearchStarted(false);
    }, [session?.session_id, sessionChatHistory]);

    useEffect(() => {
        if (
            !onGoingChatTurn?.travel_destination_filter &&
            !chatRecords.at(-1)?.travel_destination_filter
        ) {
            return;
        }

        const filterToProcess =
            onGoingChatTurn?.travel_destination_filter ??
            chatRecords.at(-1)?.travel_destination_filter;

        if (filterToProcess == null) {
            applyResolvedRegionFilters([], []); 
            return;
        }

        const includedParentRegionIds =
            filterToProcess.parent_region_filters
                ?.filter((filter) => filter.type === "include")
                .map((filter) => filter.region_name) ?? [];
        const excludedParentRegionIds =
            filterToProcess.parent_region_filters
                ?.filter((filter) => filter.type === "exclude")
                .map((filter) => filter.region_name) ?? [];

        const includedRegionIds: string[] = [];
        const excludedRegionIds: string[] = [];

        includedParentRegionIds.forEach((parentRegionId) => {
            const destinations =
                destinationContext.getDestinationsByParentRegion(parentRegionId);
            includedRegionIds.push(...destinations.map((destination) => destination.id));
        });

        excludedParentRegionIds.forEach((parentRegionId) => {
            const destinations =
                destinationContext.getDestinationsByParentRegion(parentRegionId);
            excludedRegionIds.push(...destinations.map((destination) => destination.id));
        });

        applyResolvedRegionFilters(includedRegionIds, excludedRegionIds);
    }, [onGoingChatTurn?.travel_destination_filter, chatRecords, destinationContext]);

    const submitRecommendationMessage = async (message: string): Promise<void> => {
        const userMessage = message.trim();
        if (userMessage.length === 0) {
            throw new Error("Message cannot be empty");
        }

        const activeSession = await ensureSession();
        let streamedChatTurn: ChatRecordDto | null = null;
        let accumulatedRecommendations: RecommendationItemDto[] = [];
        let accumulatedResponse = "";

        logger.trace("Submitting recommendation message via SSE", {
            messageLength: userMessage.length,
            version: activeSession.version,
        });

        try {
            const stream = streamRecommendations({
                session: activeSession,
                message: userMessage,
                included_region_ids: [],
                excluded_region_ids: [],
            });

            setOnGoingChatTurn({
                user_id: activeSession.user_id,
                session_id: activeSession.session_id,
                chat_history_number: chatRecords.length,
                user_request: userMessage,
                recommendations: [],
                travel_destinations_evaluations: [],
                included_regions_ids: [],
                excluded_regions_ids: [],
            });
            setDestinationResearchStarted(false);

            for await (const sseEvent of stream) {
                switch (sseEvent.event) {
                    case "initializing":
                    case "validating_request":
                    case "gathering_filter":
                    case "recommendation_generation":
                    case "response_generation": {
                        setStep(sseEvent.event as ProgressStage);
                        break;
                    }

                    case "filter": {
                        const filterData = sseEvent.data as TravelDestinationFilter;
                        logger.trace("Received travel destination filter", filterData);
                        setOnGoingChatTurn((prev) => ({
                            ...prev,
                            travel_destination_filter: filterData,
                        }));
                        break;
                    }

                    case "recommendation": {
                        setStep("recommendation");
                        const data = sseEvent.data as {
                            recommendations: RecommendationItemDto[];
                        };
                        accumulatedRecommendations = data.recommendations ?? [];
                        setOnGoingChatTurn((prev) => ({
                            ...prev,
                            recommendations: accumulatedRecommendations,
                        }));
                        break;
                    }

                    case "desination_research_generation": {
                        setStep("desination_research_generation");
                        setDestinationResearchStarted(true);
                        break;
                    }

                    case "destination_research": {
                        setStep("destination_research");
                        const data =
                            sseEvent.data as RecommendationDestinationResearchEventData;

                        setOnGoingChatTurn((prev) => {
                            const nextEvaluations = buildDestinationResearchEvaluations({
                                ...buildDestinationResearchStateByRegion(
                                    prev?.travel_destinations_evaluations,
                                ),
                                [data.region_id]: {
                                    state: "done",
                                    data: data.destination_research,
                                },
                            });

                            return {
                                ...prev,
                                travel_destinations_evaluations: nextEvaluations,
                            };
                        });
                        break;
                    }

                    case "response": {
                        setStep("response");
                        const data = sseEvent.data as { message: string };
                        accumulatedResponse = data.message ?? "";
                        setOnGoingChatTurn((prev) => ({
                            ...prev,
                            system_response: accumulatedResponse,
                        }));
                        break;
                    }

                    case "done": {
                        setStep("done");
                        streamedChatTurn = sseEvent.data as ChatRecordDto;
                        if (streamedChatTurn != null) {
                            const completedChatTurn = streamedChatTurn;

                            setChatRecords((prev) => [...prev, completedChatTurn]);
                        }
                        setOnGoingChatTurn(null);
                        setDestinationResearchStarted(false);
                        break;
                    }

                    case "error": {
                        setStep("error");
                        logger.error("Error event received in recommendation stream", {
                            data: sseEvent.data,
                        });
                        throw new Error("Error received from recommendation stream");
                    }

                    default: {
                        logger.debug("Ignoring unknown recommendation stream event", {
                            event: sseEvent.event,
                        });
                    }
                }
            }
        } catch (error) {
            setOnGoingChatTurn(null);
            setStep("idle");
            setDestinationResearchStarted(false);
            logger.error("Recommendation streaming failed", error);
            throw Error("Failed to submit recommendation message");
        }
    };

    return {
        chatRecords,
        setChatRecords,
        step,
        onGoingChatTurn,
        destinationResearchStarted,
        submitRecommendationMessage,
    };
}
