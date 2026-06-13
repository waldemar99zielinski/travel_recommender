import { z } from "zod";

export const sessionVersions = ["v0", "v1", "v2"] as const;

export type SessionVersion = typeof sessionVersions[number];

const sessionVersionSchema = z.enum(sessionVersions);

export interface SessionDto {
    user_id: string;
    session_id: string;
    version: SessionVersion;
}

export const sessionRefDtoSchema = z.object({
    user_id: z.string().trim().min(1),
    session_id: z.string().trim().min(1),
    version: sessionVersionSchema,
}) satisfies z.ZodType<SessionDto>;

export function validateSessionRefDto(payload: unknown): SessionDto {
    return sessionRefDtoSchema.parse(payload);
}
