import {
    Alert,
    Button,
    CircularProgress,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
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
        setSurveyAgeRange,
        setSurveyLlmExperience,
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

            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                About you
            </Typography>

            <FormControl fullWidth>
                <InputLabel id="age-range-label">Age Range</InputLabel>
                <Select
                    labelId="age-range-label"
                    label="Age Range"
                    value={surveyDraft.ageRange ?? ""}
                    onChange={(e) => setSurveyAgeRange(e.target.value || null)}
                    MenuProps={{ sx: { zIndex: 13000 } }}
                >
                    <MenuItem value="under_15">Under 15</MenuItem>
                    <MenuItem value="15-19">15–19</MenuItem>
                    <MenuItem value="20-24">20–24</MenuItem>
                    <MenuItem value="25-29">25–29</MenuItem>
                    <MenuItem value="30-34">30–34</MenuItem>
                    <MenuItem value="35+">35+</MenuItem>
                </Select>
            </FormControl>

            <FormControl fullWidth>
                <InputLabel id="llm-experience-label">LLM Experience</InputLabel>
                <Select
                    labelId="llm-experience-label"
                    label="LLM Experience"
                    value={surveyDraft.llmExperience ?? ""}
                    onChange={(e) => setSurveyLlmExperience(e.target.value || null)}
                    MenuProps={{ sx: { zIndex: 13000 } }}
                >
                    <MenuItem value="beginner">Beginner — Little to no experience</MenuItem>
                    <MenuItem value="intermediate">Intermediate — Regular use</MenuItem>
                    <MenuItem value="advanced">Advanced — Deep technical use</MenuItem>
                </Select>
            </FormControl>

            <Typography variant="body1" sx={{ fontWeight: 700 }}>
                Rate each statement on a 1 to 5 scale.
            </Typography>

            <SurveyScaleLegend />

            {surveyQuestionsError != null && (
                <Alert severity="error">{surveyQuestionsError}</Alert>
            )}

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
                    selectedScore={(surveyDraft.scores[String(question.id)] as number) ?? null}
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

            {submitSurveyError != null && <Alert severity="error">{submitSurveyError}</Alert>}
        </Stack>
    );
}
