import { Box, Stack, Typography } from "@mui/material";

import { surveyScoreColors } from "@/components/survey/surveyScoreColors";

const surveyScaleItems = [
    { value: 1, label: "Strongly disagree" },
    { value: 2, label: "Disagree" },
    { value: 3, label: "Neutral" },
    { value: 4, label: "Agree" },
    { value: 5, label: "Strongly agree" },
] as const;

export function SurveyScaleLegend() {
    return (
        <Stack spacing={1.25}>
            <Typography variant="body1" color="text.secondary">
                Rate each statement on a 1 to 5 scale.
            </Typography>

            <Stack direction="row" spacing={0.75} sx={{ alignItems: "stretch" }}>
                {surveyScaleItems.map((item) => (
                    <Box
                        key={item.value}
                        sx={{
                            flex: 1,
                            px: 1,
                            py: 0.9,
                            borderRadius: 1.5,
                            textAlign: "center",
                            bgcolor: surveyScoreColors[item.value].bg,
                            border: "1px solid",
                            borderColor: surveyScoreColors[item.value].border,
                            color: surveyScoreColors[item.value].text,
                        }}
                    >
                        <Typography variant="subtitle2" sx={{ fontWeight: 700, lineHeight: 1.1 }}>
                            {item.value}
                        </Typography>
                        <Typography variant="caption" sx={{ display: "block", lineHeight: 1.2 }}>
                            {item.label}
                        </Typography>
                    </Box>
                ))}
            </Stack>
        </Stack>
    );
}
