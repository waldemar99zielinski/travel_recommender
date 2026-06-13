import { useEffect, useRef, useState } from "react";

import { LinearProgress, Stack } from "@mui/material";

import { LoaderShell } from "@/components/loader/LoaderShell";

type TimedProgressLoaderProps = {
    durationMs: number;
    initialElapsedMs?: number;
    loaded?: boolean;
    label?: string;
    updateIntervalMs?: number;
};

function clamp(value: number, min: number, max: number): number {
    return Math.min(Math.max(value, min), max);
}

function resolveBaseProgress(elapsedMs: number, durationMs: number): number {
    if (durationMs <= 0) {
        return 90;
    }

    if (elapsedMs <= durationMs) {
        return (elapsedMs / durationMs) * 90;
    }

    if (elapsedMs >= durationMs * 2) {
        return 99;
    }

    return 90 + ((elapsedMs - durationMs) / durationMs) * 9;
}

export function TimedProgressLoader({
    durationMs,
    initialElapsedMs = 0,
    loaded = false,
    label,
    updateIntervalMs = 100,
}: TimedProgressLoaderProps) {
    const clampedDurationMs = Math.max(durationMs, 0);
    const clampedInitialElapsedMs = Math.max(initialElapsedMs, 0);
    const [progressValue, setProgressValue] = useState(() =>
        resolveBaseProgress(clampedInitialElapsedMs, clampedDurationMs),
    );
    const timelineRef = useRef({
        durationMs: clampedDurationMs,
        initialElapsedMs: clampedInitialElapsedMs,
        startedAt: 0,
    });
    const progressRef = useRef(progressValue);
    const loadedTransitionRef = useRef<{
        startedAt: number;
        startingProgress: number;
    } | null>(null);

    useEffect(() => {
        progressRef.current = progressValue;
    }, [progressValue]);

    useEffect(() => {
        timelineRef.current = {
            durationMs: clampedDurationMs,
            initialElapsedMs: clampedInitialElapsedMs,
            startedAt: Date.now() - clampedInitialElapsedMs,
        };
        loadedTransitionRef.current = null;

        const timeoutId = window.setTimeout(() => {
            const nextProgress = resolveBaseProgress(
                clampedInitialElapsedMs,
                clampedDurationMs,
            );
            progressRef.current = nextProgress;
            setProgressValue(nextProgress);
        }, 0);

        return () => {
            window.clearTimeout(timeoutId);
        };
    }, [clampedDurationMs, clampedInitialElapsedMs]);

    useEffect(() => {
        const completeDurationMs = 800;

        const updateProgress = () => {
            const now = Date.now();
            const elapsedMs = now - timelineRef.current.startedAt;
            const baseProgress = resolveBaseProgress(
                elapsedMs,
                timelineRef.current.durationMs,
            );

            if (!loaded) {
                loadedTransitionRef.current = null;
                progressRef.current = baseProgress;
                setProgressValue(baseProgress);
                return;
            }

            if (loadedTransitionRef.current == null) {
                loadedTransitionRef.current = {
                    startedAt: now,
                    startingProgress: progressRef.current,
                };
            }

            const completionElapsedMs =
                now - loadedTransitionRef.current.startedAt;
            const completionRatio = clamp(
                completionElapsedMs / completeDurationMs,
                0,
                1,
            );
            const nextProgress =
                loadedTransitionRef.current.startingProgress +
                (100 - loadedTransitionRef.current.startingProgress) * completionRatio;

            progressRef.current = nextProgress;
            setProgressValue(nextProgress);
        };

        const timeoutId = window.setTimeout(updateProgress, 0);
        const intervalId = window.setInterval(updateProgress, updateIntervalMs);

        return () => {
            window.clearTimeout(timeoutId);
            window.clearInterval(intervalId);
        };
    }, [loaded, updateIntervalMs]);

    return (
        <LoaderShell label={label}>
            <Stack sx={{ minWidth: 220 }}>
                <LinearProgress
                    variant="determinate"
                    value={progressValue}
                    sx={{
                        height: 8,
                        borderRadius: 999,
                        bgcolor: "rgba(15, 23, 42, 0.08)",
                    }}
                />
            </Stack>
        </LoaderShell>
    );
}
