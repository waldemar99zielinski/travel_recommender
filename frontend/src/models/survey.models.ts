import { z } from "zod";

export interface SurveyQuestionDto {
    id: number;
    question_text: string;
}

export interface SurveyResultCreateRequestDto {
    user_id: string;
    session_id: string;
    scores: Record<string, number | string>;
    comment?: string | null;
}

export interface SurveyResultResponseDto {
    id: number;
    user_id: string;
    session_id: string;
    scores: Record<string, number | string>;
    comment: string | null;
}

export const surveyQuestionDtoSchema = z.object({
    id: z.number().int(),
    question_text: z.string(),
}) satisfies z.ZodType<SurveyQuestionDto>;

export const surveyQuestionListResponseDtoSchema = z.array(surveyQuestionDtoSchema);

const surveyResultScoresValueSchema = z.union([z.number(), z.string()]);

export const surveyResultCreateRequestDtoSchema = z.object({
    user_id: z.string().uuid(),
    session_id: z.string().uuid(),
    scores: z.record(z.string(), surveyResultScoresValueSchema),
    comment: z.string().nullable().optional(),
}) satisfies z.ZodType<SurveyResultCreateRequestDto>;

export const surveyResultResponseDtoSchema = z.object({
    id: z.number().int(),
    user_id: z.string().uuid(),
    session_id: z.string().uuid(),
    scores: z.record(z.string(), surveyResultScoresValueSchema),
    comment: z.string().nullable(),
}) satisfies z.ZodType<SurveyResultResponseDto>;

export function validateSurveyQuestionListResponseDto(
    payload: unknown,
): SurveyQuestionDto[] {
    return surveyQuestionListResponseDtoSchema.parse(payload);
}

export function validateSurveyResultCreateRequestDto(
    payload: unknown,
): SurveyResultCreateRequestDto {
    return surveyResultCreateRequestDtoSchema.parse(payload);
}

export function validateSurveyResultResponseDto(
    payload: unknown,
): SurveyResultResponseDto {
    return surveyResultResponseDtoSchema.parse(payload);
}
