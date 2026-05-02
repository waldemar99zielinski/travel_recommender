import { z } from "zod";

export interface SessionDto {
    user_id: string;
    session_id: string;
}

export interface SessionCreateRequestDto {
    user_id?: string;
}

export interface SessionCreateResponseDto {
    session: SessionDto;
}

export interface SessionStateResponseDto {
    session: SessionDto;
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

export const sessionStateResponseDtoSchema = z.object({
    session: sessionRefDtoSchema,
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
