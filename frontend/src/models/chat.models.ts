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
