import { useEffect, type ReactNode } from "react";

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

    useEffect(() => {
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
    }, [fetchSurveyQuestions]);

    return <SurveyContext.Provider value={contextValue}>{children}</SurveyContext.Provider>;
}
