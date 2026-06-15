import { Button } from "@mui/material";
import { keyframes } from "@mui/system";

import { useSurveyContext } from "@/shared/context";

const surveyButtonShine = keyframes`
    0% {
        transform: translateX(-160%) skewX(-24deg);
    }
    100% {
        transform: translateX(220%) skewX(-24deg);
    }
`;

export function SurveyButton() {
    const { isSurveyOpen, toggleSurvey } = useSurveyContext();

    return (
        <Button
            color="inherit"
            variant={isSurveyOpen ? "outlined" : "text"}
            onClick={toggleSurvey}
            sx={{
                ml: "auto",
                borderColor: isSurveyOpen ? "currentColor" : undefined,
                position: "relative",
                overflow: "hidden",
                px: 2.5,
                textTransform: "none",
                borderRadius: 999,
                backdropFilter: "blur(6px)",
                bgcolor: isSurveyOpen ? "rgba(255,255,255,0.12)" : "rgba(255,255,255,0.06)",
                transition: "background-color 180ms ease, transform 180ms ease",
                "&:hover": {
                    bgcolor: "rgba(255,255,255,0.16)",
                    transform: "translateY(-1px)",
                },
                "&::after": {
                    content: '\"\"',
                    position: "absolute",
                    inset: 0,
                    width: "38%",
                    background:
                        "linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.08) 35%, rgba(255,255,255,0.45) 50%, rgba(255,255,255,0.08) 65%, transparent 100%)",
                    animation: `${surveyButtonShine} 2.8s ease-in-out infinite`,
                    pointerEvents: "none",
                },
            }}
        >
            Survey
        </Button>
    );
}
