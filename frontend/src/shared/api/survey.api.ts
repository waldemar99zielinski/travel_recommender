import {
    type SurveyQuestionDto,
    type SurveyResultCreateRequestDto,
    type SurveyResultResponseDto,
    validateSurveyQuestionListResponseDto,
    validateSurveyResultCreateRequestDto,
    validateSurveyResultResponseDto,
} from "@/models/survey.models";
import { surveyApiUrlBuilder } from "@/shared/api/urls.api";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "SurveyApi" });

export async function fetchSurveyQuestions(): Promise<SurveyQuestionDto[]> {
    const startedAt = Date.now();
    const url = surveyApiUrlBuilder.listQuestions();

    logger.trace("Fetching survey questions", {
        url,
    });

    const response = await fetch(url);

    if (!response.ok) {
        logger.error("Survey questions request failed", {
            status: response.status,
            statusText: response.statusText,
            durationMs: Date.now() - startedAt,
        });
        throw new Error(
            `Survey questions request failed with status ${response.status}`,
        );
    }

    const rawResponseData: unknown = await response.json();
    const responseData = validateSurveyQuestionListResponseDto(rawResponseData);

    logger.debug("Survey questions fetched", {
        total: responseData.length,
        durationMs: Date.now() - startedAt,
    });

    return responseData;
}

export async function createSurveyResult(
    payload: SurveyResultCreateRequestDto,
): Promise<SurveyResultResponseDto> {
    const requestPayload = validateSurveyResultCreateRequestDto(payload);
    const startedAt = Date.now();
    const url = surveyApiUrlBuilder.createResult();

    logger.trace("Creating survey result", {
        url,
        userId: requestPayload.user_id,
        sessionId: requestPayload.session_id,
    });

    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(requestPayload),
    });

    if (!response.ok) {
        logger.error("Create survey result request failed", {
            status: response.status,
            statusText: response.statusText,
            durationMs: Date.now() - startedAt,
        });
        throw new Error(
            `Create survey result request failed with status ${response.status}`,
        );
    }

    const rawResponseData: unknown = await response.json();
    const responseData = validateSurveyResultResponseDto(rawResponseData);

    logger.debug("Survey result created", {
        status: response.status,
        durationMs: Date.now() - startedAt,
        responseData,
    });

    return responseData;
}
