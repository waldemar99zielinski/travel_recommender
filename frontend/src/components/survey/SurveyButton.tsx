import { Button } from "@mui/material";
import { keyframes } from "@mui/system";

import { appConfiguration } from "@/shared/configuration/appConfiguration";
import { useSurveyContext } from "@/shared/context";

const surveyButtonShine = keyframes`
    0% {
        transform: translateX(-160%) skewX(-24deg);
    }
    100% {
        transform: translateX(220%) skewX(-24deg);
    }
`;

const surveyButtonGlow = keyframes`
    0% {
        box-shadow: 0 0 0 0 rgba(126, 87, 255, 0.18), 0 10px 22px rgba(7, 16, 34, 0.16);
    }
    50% {
        box-shadow: 0 0 0 5px rgba(79, 195, 247, 0.2), 0 14px 30px rgba(7, 16, 34, 0.22);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(126, 87, 255, 0.18), 0 10px 22px rgba(7, 16, 34, 0.16);
    }
`;

export function SurveyButton() {
    const { isSurveyOpen, toggleSurvey } = useSurveyContext();

    if (!appConfiguration.surveyEnabled) {
        return null;
    }

    return (
        <Button
            color="inherit"
            variant={isSurveyOpen ? "outlined" : "text"}
            onClick={toggleSurvey}
            sx={{
                ml: "auto",
                position: "relative",
                overflow: "hidden",
                px: 2.5,
                py: 0.7,
                textTransform: "none",
                borderRadius: 999,
                backdropFilter: "blur(6px)",
                color: "#f7fbff",
                fontWeight: 700,
                letterSpacing: 0.25,
                borderWidth: 1,
                borderColor: isSurveyOpen ? "rgba(255,255,255,0.42)" : "rgba(255,255,255,0.26)",
                bgcolor: isSurveyOpen ? "rgba(255,255,255,0.18)" : "rgba(255,255,255,0.1)",
                background:
                    isSurveyOpen
                        ? "linear-gradient(135deg, rgba(76, 175, 255, 0.42) 0%, rgba(126, 87, 255, 0.38) 52%, rgba(0, 229, 255, 0.26) 100%)"
                        : "linear-gradient(135deg, rgba(0, 229, 255, 0.28) 0%, rgba(126, 87, 255, 0.34) 55%, rgba(255, 64, 129, 0.22) 100%)",
                boxShadow: "0 10px 22px rgba(7, 16, 34, 0.16)",
                animation: `${surveyButtonGlow} 2.4s ease-in-out infinite`,
                transition: "background-color 180ms ease, transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease",
                "&:hover": {
                    bgcolor: "rgba(255,255,255,0.2)",
                    transform: "translateY(-1px) scale(1.015)",
                    boxShadow: "0 14px 30px rgba(7, 16, 34, 0.24)",
                    borderColor: "rgba(255,255,255,0.48)",
                },
                "&::before": {
                    content: '""',
                    position: "absolute",
                    inset: 1,
                    borderRadius: 999,
                    background:
                        "linear-gradient(180deg, rgba(255,255,255,0.34) 0%, rgba(255,255,255,0.08) 38%, rgba(255,255,255,0.02) 100%)",
                    pointerEvents: "none",
                },
                "&::after": {
                    content: '""',
                    position: "absolute",
                    inset: 0,
                    width: "42%",
                    background:
                        "linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.18) 26%, rgba(255,255,255,0.78) 50%, rgba(255,255,255,0.18) 74%, transparent 100%)",
                    animation: `${surveyButtonShine} 2.1s ease-in-out infinite`,
                    pointerEvents: "none",
                },
            }}
        >
            Survey
        </Button>
    );
}
