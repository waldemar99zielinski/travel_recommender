import { z } from "zod";

import {
    type ChatMessageDto,
    chatMessageDtoSchema,
} from "@/models/chat-message.models";
import {
    type SessionDto,
    sessionRefDtoSchema,
} from "@/models/session.models";

export interface RecommendationItemDto {
    id: string;
    title: string;
    score: number;
    description: string;
}

export interface RecommendationResponseDto {
    messages: ChatMessageDto[];
    recommendations: RecommendationItemDto[];
}

export interface RecommendationRequestDto extends SessionDto {
    message: string;
}

export const recommendationItemDtoSchema = z.object({
    id: z.string(),
    title: z.string(),
    score: z.number().finite(),
    description: z.string(),
}) satisfies z.ZodType<RecommendationItemDto>;

export const recommendationResponseDtoSchema = z.object({
    messages: z.array(chatMessageDtoSchema),
    recommendations: z.array(recommendationItemDtoSchema),
}) satisfies z.ZodType<RecommendationResponseDto>;

export const recommendationRequestDtoSchema = sessionRefDtoSchema.extend({
    message: z.string().trim().min(1),
}) satisfies z.ZodType<RecommendationRequestDto>;

export function validateRecommendationRequestDto(
    payload: unknown,
): RecommendationRequestDto {
    return recommendationRequestDtoSchema.parse(payload);
}

export function validateRecommendationResponseDto(
    payload: unknown,
): RecommendationResponseDto {
    return recommendationResponseDtoSchema.parse(payload);
}
