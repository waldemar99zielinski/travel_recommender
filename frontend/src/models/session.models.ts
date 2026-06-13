import { z } from "zod";

import { chatRecordDtoSchema, type ChatRecordDto } from "@/models/chat.models";
import { sessionRefDtoSchema, type SessionDto } from "@/models/session-ref.models";

export {
    sessionRefDtoSchema,
    sessionVersions,
    validateSessionRefDto,
    type SessionDto,
    type SessionVersion,
} from "@/models/session-ref.models";

export interface SessionCreateRequestDto {
    user_id?: string;
}

export interface SessionCreateResponseDto {
    session: SessionDto;
}

export interface SessionStateResponseDto {
    session: SessionDto;
    chat_history: ChatRecordDto[];
}

export interface SessionDeleteResponseDto {
    session: SessionDto;
}

export const sessionCreateRequestDtoSchema = z.object({
    user_id: z.string().optional(),
}) satisfies z.ZodType<SessionCreateRequestDto>;

export const sessionCreateResponseDtoSchema = z.object({
    session: sessionRefDtoSchema,
}) satisfies z.ZodType<SessionCreateResponseDto>;

export const sessionStateResponseDtoSchema = z.object({
    session: sessionRefDtoSchema,
    chat_history: z.array(chatRecordDtoSchema),
}) satisfies z.ZodType<SessionStateResponseDto>;

export const sessionDeleteResponseDtoSchema = z.object({
    session: sessionRefDtoSchema,
}) satisfies z.ZodType<SessionDeleteResponseDto>;

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
