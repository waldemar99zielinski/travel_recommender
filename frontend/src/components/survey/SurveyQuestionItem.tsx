import { Box, ToggleButton, ToggleButtonGroup, Typography } from "@mui/material";

import type { SurveyQuestionDto } from "@/models/survey.models";

import { surveyScoreColors } from "@/components/survey/surveyScoreColors";

interface SurveyQuestionItemProps {
    question: SurveyQuestionDto;
    selectedScore: number | null;
    onSelectScore: (questionId: number, score: number) => void;
}

export function SurveyQuestionItem({
    question,
    selectedScore,
    onSelectScore,
}: SurveyQuestionItemProps) {
    return (
        <Box>
            <Typography variant="body1" sx={{ mb: 0.75, whiteSpace: "pre-line" }}>
                <Box component="span" sx={{ fontWeight: 700, mr: 1 }}>
                    {question.id}.
                </Box>
                {question.question_text.replace(/\\n/g, "\n")}
            </Typography>

            <ToggleButtonGroup
                value={selectedScore}
                exclusive
                onChange={(_event, value) => {
                    if (value != null) {
                        onSelectScore(question.id, value);
                    }
                }}
                size="small"
                sx={{
                    display: "flex",
                    gap: 1,
                    "& .MuiToggleButtonGroup-grouped": {
                        flex: 1,
                        border: 1,
                        borderColor: "divider",
                        borderRadius: 1.5,
                        "&:not(:first-of-type)": {
                            borderRadius: 1.5,
                            borderLeft: 1,
                            borderLeftColor: "divider",
                        },
                        "&:not(:last-of-type)": {
                            borderRadius: 1.5,
                        },
                    },
                }}
            >
                {[1, 2, 3, 4, 5].map((value) => (
                    <ToggleButton
                        key={value}
                        value={value}
                        sx={{
                            bgcolor: surveyScoreColors[value].bg,
                            color: surveyScoreColors[value].text,
                            borderColor: surveyScoreColors[value].border,
                            px: 2,
                            py: 0.75,
                            fontWeight: selectedScore === value ? 700 : 400,
                            "&:hover": {
                                bgcolor: surveyScoreColors[value].bg,
                                filter: "brightness(0.97)",
                            },
                            "&.Mui-selected": {
                                bgcolor: surveyScoreColors[value].border,
                                color: surveyScoreColors[value].text,
                                borderColor: surveyScoreColors[value].text,
                                boxShadow: `0 0 0 2px ${surveyScoreColors[value].text} inset`,
                                transform: "translateY(-1px)",
                            },
                            "&.Mui-selected:hover": {
                                bgcolor: surveyScoreColors[value].border,
                                filter: "brightness(0.97)",
                            },
                        }}
                    >
                        {value}
                    </ToggleButton>
                ))}
            </ToggleButtonGroup>
        </Box>
    );
}
