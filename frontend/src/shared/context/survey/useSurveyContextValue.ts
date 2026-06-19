import { useCallback, useState } from "react";

import type {
    SurveyQuestionDto,
    SurveyResultResponseDto,
} from "@/models/survey.models";
import {
    createSurveyResult as createSurveyResultRequest,
    fetchSurveyQuestions as fetchSurveyQuestionsRequest,
} from "@/shared/api/survey.api";
import type {
    SurveyContextValue,
    SurveyDraftState,
} from "@/shared/context/survey/surveyContext";
import { useSessionContext } from "@/shared/context/session/useSessionContext";
import { useApiRequest } from "@/shared/hooks/useApiRequest";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "SurveyContext" });

function createEmptySurveyDraft(): SurveyDraftState {
    return {
        scores: {},
        comment: "",
    };
}

export function useSurveyContextValue(): SurveyContextValue {
    const { ensureSession } = useSessionContext();
    const [isSurveyOpen, setIsSurveyOpen] = useState(false);
    const [surveyDraft, setSurveyDraft] = useState<SurveyDraftState>(createEmptySurveyDraft);
    const [surveyQuestionsData, surveyQuestionsStatus, surveyQuestionsError, triggerFetchSurveyQuestions] =
        useApiRequest<SurveyQuestionDto[]>(fetchSurveyQuestionsRequest, {
            requestName: "surveyQuestions",
        });

    const surveyQuestions = surveyQuestionsData ?? [];
    const allQuestionsAnswered =
        surveyQuestions.length > 0 &&
        surveyQuestions.every((question) => surveyDraft.scores[String(question.id)] != null);

    const setSurveyScore = useCallback((questionId: number, score: number) => {
        setSurveyDraft((prev) => ({
            ...prev,
            scores: {
                ...prev.scores,
                [String(questionId)]: score,
            },
        }));
    }, []);

    const setSurveyComment = useCallback((comment: string) => {
        setSurveyDraft((prev) => ({
            ...prev,
            comment,
        }));
    }, []);

    const clearSurveyDraft = useCallback(() => {
        setSurveyDraft(createEmptySurveyDraft());
    }, []);

    const openSurvey = useCallback(() => {
        setIsSurveyOpen(true);
    }, []);

    const closeSurvey = useCallback(() => {
        setIsSurveyOpen(false);
    }, []);

    const toggleSurvey = useCallback(() => {
        setIsSurveyOpen((prev) => !prev);
    }, []);

    const submitSurveyHandler = useCallback(async (): Promise<SurveyResultResponseDto> => {
        if (surveyQuestions.length === 0) {
            throw new Error("Cannot submit survey before questions are loaded");
        }

        if (!allQuestionsAnswered) {
            throw new Error("Cannot submit survey before all questions are answered");
        }

        const session = await ensureSession();
        const comment = surveyDraft.comment.trim();
        const response = await createSurveyResultRequest({
            user_id: session.user_id,
            session_id: session.session_id,
            scores: surveyDraft.scores,
            comment: comment.length === 0 ? null : comment,
        });

        logger.debug("Submitted survey result", {
            questionCount: surveyQuestions.length,
            surveyResultId: response.id,
        });

        setSurveyDraft(createEmptySurveyDraft());

        return response;
    }, [allQuestionsAnswered, ensureSession, surveyDraft, surveyQuestions]);

    const [submitSurveyData, submitSurveyStatus, submitSurveyError, submitSurvey] = useApiRequest<
        SurveyResultResponseDto
    >(submitSurveyHandler, {
        requestName: "submitSurvey",
    });

    const fetchSurveyQuestions = useCallback(async (): Promise<SurveyQuestionDto[] | null> => {
        return triggerFetchSurveyQuestions();
    }, [triggerFetchSurveyQuestions]);

    return {
        isSurveyOpen,
        openSurvey,
        closeSurvey,
        toggleSurvey,
        surveyQuestions,
        surveyQuestionsStatus,
        surveyQuestionsError,
        fetchSurveyQuestions,
        surveyDraft,
        allQuestionsAnswered,
        setSurveyScore,
        setSurveyComment,
        clearSurveyDraft,
        submitSurveyData,
        submitSurveyStatus,
        submitSurveyError,
        submitSurvey,
    };
}
