import { z } from "zod";

export interface SessionRefDto {
    user_id: string;
    session_id: string;
}

export interface SessionCreateRequestDto {
    user_id?: string;
}

export interface SessionCreateResponseDto {
    session: SessionRefDto;
}

export interface SessionStateResponseDto {
    session: SessionRefDto;
}

export interface SessionDeleteResponseDto {
    session: SessionRefDto;
}

export const sessionRefDtoSchema = z.object({
    user_id: z.string().trim().min(1),
    session_id: z.string().trim().min(1),
}) satisfies z.ZodType<SessionRefDto>;

export const sessionCreateRequestDtoSchema = z.object({
    user_id: z.string().optional(),
}) satisfies z.ZodType<SessionCreateRequestDto>;

export const sessionCreateResponseDtoSchema = z.object({
    session: sessionRefDtoSchema,
}) satisfies z.ZodType<SessionCreateResponseDto>;

export const sessionStateResponseDtoSchema = z.object({
    session: sessionRefDtoSchema,
}) satisfies z.ZodType<SessionStateResponseDto>;

export const sessionDeleteResponseDtoSchema = z.object({
    session: sessionRefDtoSchema,
}) satisfies z.ZodType<SessionDeleteResponseDto>;

export function validateSessionRefDto(payload: unknown): SessionRefDto {
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
