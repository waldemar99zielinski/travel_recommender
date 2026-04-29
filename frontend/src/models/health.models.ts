import { z } from "zod";

export type HealthCheckStatus = "ok" | "error";
export type HealthStatus = "ok" | "degraded";

export interface ApiHealthCheckDto {
    healthy: boolean;
    status: HealthCheckStatus;
    details: string;
}

export interface EmbeddingsHealthCheckDto {
    healthy: boolean;
    status: HealthCheckStatus;
    details: string;
    dimensions: number | null;
}

export interface StorageHealthCheckDto {
    healthy: boolean;
    status: HealthCheckStatus;
    details: string;
    database_reachable: boolean;
    postgresql_18_compatible: boolean;
    pgvector_enabled: boolean;
    pgvector_version_compatible: boolean;
    embedding_dimension_matches: boolean;
    vector_index_present: boolean;
}

export interface HealthChecksDto {
    api: ApiHealthCheckDto;
    embeddings: EmbeddingsHealthCheckDto;
    storage: StorageHealthCheckDto;
}

export interface HealthResponseDto {
    status: HealthStatus;
    env: string;
    log_level: string;
    checks: HealthChecksDto;
}

export const healthCheckStatusSchema = z.enum(["ok", "error"]) satisfies z.ZodType<HealthCheckStatus>;
export const healthStatusSchema = z.enum(["ok", "degraded"]) satisfies z.ZodType<HealthStatus>;

export const apiHealthCheckDtoSchema = z.object({
    healthy: z.boolean(),
    status: healthCheckStatusSchema,
    details: z.string(),
}) satisfies z.ZodType<ApiHealthCheckDto>;

export const embeddingsHealthCheckDtoSchema = apiHealthCheckDtoSchema.extend({
    dimensions: z.number().int().nullable(),
}) satisfies z.ZodType<EmbeddingsHealthCheckDto>;

export const storageHealthCheckDtoSchema = apiHealthCheckDtoSchema.extend({
    database_reachable: z.boolean(),
    postgresql_18_compatible: z.boolean(),
    pgvector_enabled: z.boolean(),
    pgvector_version_compatible: z.boolean(),
    embedding_dimension_matches: z.boolean(),
    vector_index_present: z.boolean(),
}) satisfies z.ZodType<StorageHealthCheckDto>;

export const healthChecksDtoSchema = z.object({
    api: apiHealthCheckDtoSchema,
    embeddings: embeddingsHealthCheckDtoSchema,
    storage: storageHealthCheckDtoSchema,
}) satisfies z.ZodType<HealthChecksDto>;

export const healthResponseDtoSchema = z.object({
    status: healthStatusSchema,
    env: z.string(),
    log_level: z.string(),
    checks: healthChecksDtoSchema,
}) satisfies z.ZodType<HealthResponseDto>;

export function validateHealthResponseDto(payload: unknown): HealthResponseDto {
    return healthResponseDtoSchema.parse(payload);
}
