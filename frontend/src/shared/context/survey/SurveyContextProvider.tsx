import { useEffect, type ReactNode } from "react";

import { appConfiguration } from "@/shared/configuration/appConfiguration";
import { SurveyContext } from "@/shared/context/survey/surveyContext";
import { useSurveyContextValue } from "@/shared/context/survey/useSurveyContextValue";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "SurveyContextProvider" });

type SurveyContextProviderProps = {
    children: ReactNode;
};

export function SurveyContextProvider({ children }: SurveyContextProviderProps) {
    const contextValue = useSurveyContextValue();
    const { fetchSurveyQuestions } = contextValue;
    const isSurveyEnabled = appConfiguration.surveyEnabled;

    useEffect(() => {
        if (!isSurveyEnabled) {
            logger.debug("Survey feature disabled, skipping question fetch");
            return;
        }

        const loadSurveyQuestions = async () => {
            logger.trace("Fetching survey questions");

            const questions = await fetchSurveyQuestions();
            if (questions == null) {
                logger.error("Failed to load survey questions");
                return;
            }

            logger.debug("Survey questions loaded", {
                count: questions.length,
            });
        };

        void loadSurveyQuestions();
    }, [fetchSurveyQuestions, isSurveyEnabled]);

    return <SurveyContext.Provider value={contextValue}>{children}</SurveyContext.Provider>;
}
