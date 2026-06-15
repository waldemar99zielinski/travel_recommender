import { createContext } from "react";

import type {
    SurveyQuestionDto,
    SurveyResultResponseDto,
} from "@/models/survey.models";
import type { FetchStatus } from "@/shared/hooks/apiHookTypes";

export interface SurveyDraftState {
    scores: Record<string, number | string>;
    comment: string;
    ageRange: string | null;
}

export interface SurveyContextValue {
    isSurveyOpen: boolean;
    openSurvey: () => void;
    closeSurvey: () => void;
    toggleSurvey: () => void;

    surveyQuestions: SurveyQuestionDto[];
    surveyQuestionsStatus: FetchStatus;
    surveyQuestionsError: string | null;
    fetchSurveyQuestions: () => Promise<SurveyQuestionDto[] | null>;

    surveyDraft: SurveyDraftState;
    allQuestionsAnswered: boolean;
    setSurveyScore: (questionId: number, score: number) => void;
    setSurveyComment: (comment: string) => void;
    setSurveyAgeRange: (ageRange: string | null) => void;
    clearSurveyDraft: () => void;

    submitSurveyData: SurveyResultResponseDto | null;
    submitSurveyStatus: FetchStatus;
    submitSurveyError: string | null;
    submitSurvey: () => Promise<SurveyResultResponseDto | null>;
}

export const SurveyContext = createContext<SurveyContextValue | undefined>(undefined);
