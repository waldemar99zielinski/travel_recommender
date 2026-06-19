import {
    Alert,
    Button,
    CircularProgress,
    Stack,
    TextField,
    Typography,
} from "@mui/material";

import { SurveyQuestionItem } from "@/components/survey/SurveyQuestionItem";
import { SurveyScaleLegend } from "@/components/survey/SurveyScaleLegend";
import { useSurveyContext } from "@/shared/context";

type SurveyProps = {
    title?: string;
};

export function Survey({ title }: SurveyProps) {
    const {
        surveyQuestions,
        surveyQuestionsStatus,
        surveyQuestionsError,
        surveyDraft,
        allQuestionsAnswered,
        setSurveyScore,
        setSurveyComment,
        submitSurvey,
        submitSurveyStatus,
        submitSurveyError,
    } = useSurveyContext();

    async function handleSubmit() {
        await submitSurvey();
    }

    const orderedQuestions = [...surveyQuestions].sort((left, right) => left.id - right.id);
    const isLoadingQuestions =
        (surveyQuestionsStatus === "idle" || surveyQuestionsStatus === "loading");
    const isSubmitting = submitSurveyStatus === "loading";

    return (
        <Stack spacing={2.25}>
            {title != null && (
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    {title}
                </Typography>
            )}

            <SurveyScaleLegend />

            {surveyQuestionsError != null && (
                <Alert severity="error">{surveyQuestionsError}</Alert>
            )}

            {submitSurveyError != null && <Alert severity="error">{submitSurveyError}</Alert>}

            {isLoadingQuestions && (
                <Stack direction="row" spacing={1.5} sx={{ alignItems: "center" }}>
                    <CircularProgress size={20} />
                    <Typography variant="body2" color="text.secondary">
                        Loading survey questions...
                    </Typography>
                </Stack>
            )}

            {orderedQuestions.map((question) => (
                <SurveyQuestionItem
                    key={question.id}
                    question={question}
                    selectedScore={surveyDraft.scores[String(question.id)] ?? null}
                    onSelectScore={setSurveyScore}
                />
            ))}

            <TextField
                label="Additional feedback"
                value={surveyDraft.comment}
                onChange={(e) => setSurveyComment(e.target.value)}
                multiline
                minRows={3}
                maxRows={6}
                fullWidth
            />

            <Button
                variant="contained"
                disabled={!allQuestionsAnswered || isSubmitting || isLoadingQuestions}
                onClick={handleSubmit}
                sx={{ alignSelf: "flex-start" }}
            >
                {isSubmitting ? "Submitting..." : "Submit"}
            </Button>
        </Stack>
    );
}
