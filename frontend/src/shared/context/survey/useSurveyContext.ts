import { useContext } from "react";

import { SurveyContext } from "@/shared/context/survey/surveyContext";
import { createLogger } from "@/shared/lib";

const logger = createLogger({ scope: "useSurveyContext" });

export function useSurveyContext() {
    const context = useContext(SurveyContext);

    if (context == null) {
        logger.error("SurveyContext is missing in component tree");
        throw new Error("useSurveyContext must be used within SurveyContextProvider");
    }

    return context;
}
