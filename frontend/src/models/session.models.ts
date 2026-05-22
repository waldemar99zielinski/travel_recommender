import { z } from "zod";

import {
    type ChatMessageDto,
    chatMessageDtoSchema,
} from "@/models/chat-message.models";

export interface SessionDto {
    user_id: string;
    session_id: string;
}

export interface SessionHistoryTurnDto {
    chat_history_number: number;
    user_request: string;
    system_messages: ChatMessageDto[];
}

export interface SessionRecommendationItemDto {
    id: string;
    title: string;
    score: number;
    description: string;
}

export interface SessionCreateRequestDto {
    user_id?: string;
}

export interface SessionCreateResponseDto {
    session: SessionDto;
}

export interface SessionStateResponseDto {
    session: SessionDto;
    history: SessionHistoryTurnDto[];
    last_recommendation_result: SessionRecommendationItemDto[];
}

export interface SessionDeleteResponseDto {
    session: SessionDto;
}

export const sessionRefDtoSchema = z.object({
    user_id: z.string().trim().min(1),
    session_id: z.string().trim().min(1),
}) satisfies z.ZodType<SessionDto>;

export const sessionCreateRequestDtoSchema = z.object({
    user_id: z.string().optional(),
}) satisfies z.ZodType<SessionCreateRequestDto>;

export const sessionCreateResponseDtoSchema = z.object({
    session: sessionRefDtoSchema,
}) satisfies z.ZodType<SessionCreateResponseDto>;

export const sessionHistoryTurnDtoSchema = z.object({
    chat_history_number: z.number().int().nonnegative(),
    user_request: z.string(),
    system_messages: z.array(chatMessageDtoSchema),
}) satisfies z.ZodType<SessionHistoryTurnDto>;

export const sessionRecommendationItemDtoSchema = z.object({
    id: z.string(),
    title: z.string(),
    score: z.number().finite(),
    description: z.string(),
}) satisfies z.ZodType<SessionRecommendationItemDto>;

export const sessionStateResponseDtoSchema = z.object({
    session: sessionRefDtoSchema,
    history: z.array(sessionHistoryTurnDtoSchema),
    last_recommendation_result: z.array(sessionRecommendationItemDtoSchema),
}) satisfies z.ZodType<SessionStateResponseDto>;

export const sessionDeleteResponseDtoSchema = z.object({
    session: sessionRefDtoSchema,
}) satisfies z.ZodType<SessionDeleteResponseDto>;

export function validateSessionRefDto(payload: unknown): SessionDto {
    return sessionRefDtoSchema.parse(payload);
}

export function validateSessionCreateRequestDto(
    payload: unknown,
): SessionCreateRequestDto {
    return sessionCreateRequestDtoSchema.parse(payload);
}

export function validateSessionCreateResponseDto(
    payload: unknown,
): SessionCreateResponseDto {
    return sessionCreateResponseDtoSchema.parse(payload);
}

export function validateSessionStateResponseDto(
    payload: unknown,
): SessionStateResponseDto {
    return sessionStateResponseDtoSchema.parse(payload);
}

export function validateSessionDeleteResponseDto(
    payload: unknown,
): SessionDeleteResponseDto {
    return sessionDeleteResponseDtoSchema.parse(payload);
}
