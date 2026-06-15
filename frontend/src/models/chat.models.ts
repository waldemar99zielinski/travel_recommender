import { z } from "zod";

import type { TravelDestinationFilter } from "@/models/recommendation.stream.models";
import {
    recommendationItemDtoSchema,
    recommendationV2TravelDestinationEvaluationDtoSchema,
    type RecommendationItemDto,
    type RecommendationV2TravelDestinationEvaluationDto,
} from "@/models/recommendation.models";

export interface ChatRecordDto {
    user_id: string;
    session_id: string;
    chat_history_number: number;
    user_request: string;
    system_response: string;
    recommendations: RecommendationItemDto[];
    travel_destinations_evaluations: RecommendationV2TravelDestinationEvaluationDto[];
    included_regions_ids: string[];
    excluded_regions_ids: string[];
    travel_destination_filter?: TravelDestinationFilter | null;
}

export type ChatTurnLike = ChatRecordDto | Partial<ChatRecordDto>;

const chatRecordTravelDestinationFilterSchema = z.custom<TravelDestinationFilter | null | undefined>(
    (value) => value == null || typeof value === "object",
);

export const chatRecordDtoSchema = z.object({
    user_id: z.string().trim().min(1),
    session_id: z.string().trim().min(1),
    chat_history_number: z.number().int().nonnegative(),
    user_request: z.string(),
    system_response: z.string(),
    recommendations: z.array(recommendationItemDtoSchema),
    travel_destinations_evaluations: z.array(
        recommendationV2TravelDestinationEvaluationDtoSchema,
    ),
    included_regions_ids: z.array(z.string()),
    excluded_regions_ids: z.array(z.string()),
    travel_destination_filter: chatRecordTravelDestinationFilterSchema.optional(),
}) satisfies z.ZodType<ChatRecordDto>;

export function validateChatRecordDto(payload: unknown): ChatRecordDto {
    return chatRecordDtoSchema.parse(payload);
}

export function hasRecommendations(turn: ChatTurnLike | null | undefined): boolean {
    return (turn?.recommendations?.length ?? 0) > 0;
}

export function getLatestTurnWithRecommendations(
    turns: ReadonlyArray<ChatTurnLike | null | undefined>,
): ChatTurnLike | null {
    for (let index = turns.length - 1; index >= 0; index -= 1) {
        const turn = turns[index];

        if (turn != null && hasRecommendations(turn)) {
            return turn;
        }
    }

    return null;
}
