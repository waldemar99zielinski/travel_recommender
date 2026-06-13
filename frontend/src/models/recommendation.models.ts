import { z } from "zod";

import {
    type SessionDto,
    sessionRefDtoSchema,
} from "@/models/session-ref.models";

export interface RecommendationRequestDto {
    session: SessionDto;
    message: string;
    included_region_ids: string[];
    excluded_region_ids: string[];
}

export interface RecommendationItemDto {
    region_id: string;
    region_name: string;
}

export interface RecommendationV2RegionResearchDto {
    description: string;
    image_urls: string[];
}

export interface RecommendationV2TravelDestinationEvaluationDto
    extends RecommendationV2RegionResearchDto {
    region_id: string;
}

export const recommendationItemDtoSchema = z.object({
    region_id: z.string().trim().min(1),
    region_name: z.string().trim().min(1),
}) satisfies z.ZodType<RecommendationItemDto>;

export const recommendationV2RegionResearchDtoSchema = z.object({
    description: z.string(),
    image_urls: z.array(z.string()),
}) satisfies z.ZodType<RecommendationV2RegionResearchDto>;

export const recommendationV2TravelDestinationEvaluationDtoSchema = z.object({
    region_id: z.string().trim().min(1),
    description: z.string(),
    image_urls: z.array(z.string()),
}) satisfies z.ZodType<RecommendationV2TravelDestinationEvaluationDto>;

export const recommendationRequestDtoSchema = z.object({
    session: sessionRefDtoSchema,
    message: z.string().trim().min(1),
    included_region_ids: z.array(z.string()),
    excluded_region_ids: z.array(z.string()),
    request_type: z.enum(["user_message", "explore_destination"]),
}) satisfies z.ZodType<RecommendationRequestDto>;

export function validateRecommendationRequestDto(
    payload: unknown,
): RecommendationRequestDto {
    return recommendationRequestDtoSchema.parse(payload);
}
