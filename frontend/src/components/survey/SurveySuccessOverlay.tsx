import { Box, Button, Fade, Paper, SvgIcon, Typography } from "@mui/material";
import { keyframes } from "@mui/system";

interface SurveySuccessOverlayProps {
    open: boolean;
    onClose: () => void;
}

const thankYouCardAnimation = keyframes`
    0% {
        opacity: 0;
        transform: translateY(18px) scale(0.94);
    }
    55% {
        opacity: 1;
        transform: translateY(0) scale(1.02);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
`;

const thankYouGlowAnimation = keyframes`
    0% {
        box-shadow: 0 0 0 0 rgba(46, 125, 50, 0.22);
    }
    70% {
        box-shadow: 0 0 0 16px rgba(46, 125, 50, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(46, 125, 50, 0);
    }
`;

export function SurveySuccessOverlay({ open, onClose }: SurveySuccessOverlayProps) {
    return (
        <Fade in={open} timeout={{ enter: 260, exit: 300 }} unmountOnExit>
            <Box
                sx={{
                    position: "absolute",
                    inset: 0,
                    display: "flex",
                    alignItems: "flex-start",
                    justifyContent: "center",
                    pt: 7,
                    bgcolor: "rgba(250, 252, 250, 0.88)",
                    backdropFilter: "blur(3px)",
                    borderRadius: 2,
                    zIndex: 2,
                    pointerEvents: "auto",
                }}
                onClick={onClose}
            >
                <Paper
                    elevation={10}
                    onClick={(event) => {
                        event.stopPropagation();
                    }}
                    sx={{
                        px: 3,
                        py: 2.5,
                        minWidth: 260,
                        maxWidth: 320,
                        textAlign: "center",
                        borderRadius: 3,
                        border: "1px solid rgba(46, 125, 50, 0.18)",
                        background:
                            "linear-gradient(180deg, rgba(240, 255, 244, 0.98) 0%, rgba(255, 255, 255, 0.98) 100%)",
                        animation: `${thankYouCardAnimation} 320ms ease-out`,
                    }}
                >
                    <Box
                        sx={{
                            width: 60,
                            height: 60,
                            mx: "auto",
                            mb: 1.5,
                            borderRadius: "50%",
                            display: "grid",
                            placeItems: "center",
                            color: "success.dark",
                            bgcolor: "rgba(46, 125, 50, 0.12)",
                            animation: `${thankYouGlowAnimation} 1.5s ease-out`,
                        }}
                    >
                        <SvgIcon sx={{ fontSize: 34 }}>
                            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                        </SvgIcon>
                    </Box>

                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.75 }}>
                        Thank you!
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Your feedback was submitted successfully.
                    </Typography>
                    <Button
                        variant="contained"
                        color="success"
                        onClick={onClose}
                        sx={{ mt: 2, minWidth: 120 }}
                    >
                        Close
                    </Button>
                </Paper>
            </Box>
        </Fade>
    );
}
