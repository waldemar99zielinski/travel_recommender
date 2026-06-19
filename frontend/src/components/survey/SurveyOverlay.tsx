import { useEffect, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";

import {
    Box,
    IconButton,
    Paper,
    Stack,
    SvgIcon,
    Typography,
} from "@mui/material";

import { Survey } from "@/components/survey/Survey";
import { SurveySuccessOverlay } from "@/components/survey/SurveySuccessOverlay";
import { useSurveyContext } from "@/shared/context";

export interface SurveyOverlayProps {
    open: boolean;
    onClose: () => void;
}

type OverlayPosition = {
    left: number;
    top: number;
};

const VIEWPORT_MARGIN = 12;
const DEFAULT_TOP = 88;
const DEFAULT_WIDTH = 420;
const DEFAULT_HEIGHT = 560;

function clamp(value: number, min: number, max: number): number {
    return Math.min(Math.max(value, min), max);
}

function getDefaultPosition(): OverlayPosition {
    if (typeof window === "undefined") {
        return {
            left: VIEWPORT_MARGIN,
            top: DEFAULT_TOP,
        };
    }

    return {
        left: Math.max(VIEWPORT_MARGIN, (window.innerWidth - DEFAULT_WIDTH) / 2),
        top: Math.max(VIEWPORT_MARGIN, (window.innerHeight - DEFAULT_HEIGHT) / 2),
    };
}

export function SurveyOverlay({ open, onClose }: SurveyOverlayProps) {
    const { submitSurveyData, submitSurveyStatus } = useSurveyContext();
    const panelRef = useRef<HTMLDivElement | null>(null);
    const dragOffsetRef = useRef({ x: 0, y: 0 });
    const [position, setPosition] = useState<OverlayPosition>(getDefaultPosition);
    const [isSuccessVisible, setIsSuccessVisible] = useState(false);
    const lastSubmittedSurveyIdRef = useRef<number | null>(null);

    useEffect(() => {
        if (submitSurveyStatus !== "success" || submitSurveyData == null) {
            return;
        }

        if (lastSubmittedSurveyIdRef.current === submitSurveyData.id) {
            return;
        }

        lastSubmittedSurveyIdRef.current = submitSurveyData.id;
        setIsSuccessVisible(true);

        const timeoutId = window.setTimeout(() => {
            setIsSuccessVisible(false);
        }, 2400);

        return () => {
            window.clearTimeout(timeoutId);
        };
    }, [submitSurveyData, submitSurveyStatus]);

    useEffect(() => {
        const handleResize = () => {
            const panel = panelRef.current;
            if (panel == null) {
                return;
            }

            const rect = panel.getBoundingClientRect();
            const maxLeft = Math.max(VIEWPORT_MARGIN, window.innerWidth - rect.width - VIEWPORT_MARGIN);
            const maxTop = Math.max(VIEWPORT_MARGIN, window.innerHeight - rect.height - VIEWPORT_MARGIN);

            setPosition((prev) => ({
                left: clamp(prev.left, VIEWPORT_MARGIN, maxLeft),
                top: clamp(prev.top, VIEWPORT_MARGIN, maxTop),
            }));
        };

        window.addEventListener("resize", handleResize);
        return () => {
            window.removeEventListener("resize", handleResize);
        };
    }, []);

    const handleDragStart = (event: ReactPointerEvent<HTMLDivElement>) => {
        if (event.button !== 0) {
            return;
        }

        if ((event.target as HTMLElement).closest("button") != null) {
            return;
        }

        const panel = panelRef.current;
        if (panel == null) {
            return;
        }

        const rect = panel.getBoundingClientRect();
        dragOffsetRef.current = {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top,
        };

        const handlePointerMove = (moveEvent: PointerEvent) => {
            const maxLeft = Math.max(VIEWPORT_MARGIN, window.innerWidth - rect.width - VIEWPORT_MARGIN);
            const maxTop = Math.max(VIEWPORT_MARGIN, window.innerHeight - rect.height - VIEWPORT_MARGIN);

            setPosition({
                left: clamp(
                    moveEvent.clientX - dragOffsetRef.current.x,
                    VIEWPORT_MARGIN,
                    maxLeft,
                ),
                top: clamp(
                    moveEvent.clientY - dragOffsetRef.current.y,
                    VIEWPORT_MARGIN,
                    maxTop,
                ),
            });
        };

        const handlePointerUp = () => {
            window.removeEventListener("pointermove", handlePointerMove);
            window.removeEventListener("pointerup", handlePointerUp);
        };

        window.addEventListener("pointermove", handlePointerMove);
        window.addEventListener("pointerup", handlePointerUp);
    };

    if (!open) {
        return null;
    }

    return (
        <Box
            sx={{
                position: "fixed",
                inset: 0,
                zIndex: 11000,
                pointerEvents: "none",
            }}
        >
            <Paper
                ref={panelRef}
                elevation={12}
                sx={{
                    position: "fixed",
                    left: position.left,
                    top: position.top,
                    width: `min(${DEFAULT_WIDTH}px, calc(100vw - ${VIEWPORT_MARGIN * 2}px))`,
                    height: `min(${DEFAULT_HEIGHT}px, calc(100vh - ${VIEWPORT_MARGIN * 2}px))`,
                    display: "flex",
                    flexDirection: "column",
                    overflow: "hidden",
                    pointerEvents: "auto",
                    borderRadius: 2,
                }}
            >
                <Stack
                    direction="row"
                    spacing={1}
                    onPointerDown={handleDragStart}
                    sx={{
                        px: 2,
                        py: 1.25,
                        alignItems: "center",
                        justifyContent: "space-between",
                        borderBottom: "1px solid",
                        borderColor: "divider",
                        cursor: "move",
                        userSelect: "none",
                        touchAction: "none",
                        bgcolor: "background.default",
                    }}
                >
                    <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                        Survey
                    </Typography>

                    <IconButton size="small" onClick={onClose} aria-label="Close survey">
                        <SvgIcon fontSize="small">
                            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                        </SvgIcon>
                    </IconButton>
                </Stack>

                <Box sx={{ flex: 1, overflow: "auto", p: 2 }}>
                    <Survey />
                </Box>

                <SurveySuccessOverlay
                    open={isSuccessVisible}
                    onClose={() => setIsSuccessVisible(false)}
                />
            </Paper>
        </Box>
    );
}
