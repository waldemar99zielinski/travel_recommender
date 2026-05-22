function resolveScorePercentage(score: number): number {
    if (!Number.isFinite(score)) {
        return -1;
    }

    if (score >= 0 && score <= 1) {
        return score * 100;
    }

    return score;
}

const SCORE_COLOR_STOPS = [
    { value: 0, color: "#bf1e24" },
    { value: 0.25, color: "#f58e1d" },
    { value: 0.5, color: "#ffcc06" },
    { value: 0.75, color: "#7cba43" },
    { value: 1, color: "#109146" },
] as const;

function clamp(value: number, min: number, max: number): number {
    return Math.min(Math.max(value, min), max);
}

function interpolateColorChannel(start: number, end: number, amount: number): number {
    return Math.round(start + (end - start) * amount);
}

function interpolateHexColor(startColor: string, endColor: string, amount: number): string {
    const normalizedAmount = clamp(amount, 0, 1);
    const start = startColor.slice(1);
    const end = endColor.slice(1);

    const red = interpolateColorChannel(
        Number.parseInt(start.slice(0, 2), 16),
        Number.parseInt(end.slice(0, 2), 16),
        normalizedAmount,
    );
    const green = interpolateColorChannel(
        Number.parseInt(start.slice(2, 4), 16),
        Number.parseInt(end.slice(2, 4), 16),
        normalizedAmount,
    );
    const blue = interpolateColorChannel(
        Number.parseInt(start.slice(4, 6), 16),
        Number.parseInt(end.slice(4, 6), 16),
        normalizedAmount,
    );

    return `#${red.toString(16).padStart(2, "0")}${green
        .toString(16)
        .padStart(2, "0")}${blue.toString(16).padStart(2, "0")}`;
}

export function formatRecommendationScore(score: number): string {
    if (!Number.isFinite(score)) {
        return "0.000";
    }

    return (score * 100).toFixed(3);
}

export function normalizedScoreToColor(score: number): string {
    if (!Number.isFinite(score)) {
        return "#d6dee8";
    }

    const normalizedScore = clamp(score, 0, 1);

    for (let index = 1; index < SCORE_COLOR_STOPS.length; index += 1) {
        const previousStop = SCORE_COLOR_STOPS[index - 1];
        const nextStop = SCORE_COLOR_STOPS[index];

        if (normalizedScore <= nextStop.value) {
            const segmentRange = nextStop.value - previousStop.value;
            const segmentAmount =
                segmentRange === 0
                    ? 0
                    : (normalizedScore - previousStop.value) / segmentRange;

            return interpolateHexColor(
                previousStop.color,
                nextStop.color,
                segmentAmount,
            );
        }
    }

    return SCORE_COLOR_STOPS[SCORE_COLOR_STOPS.length - 1].color;
}

export function createRelativeScoreColorScale(scores: number[]): (score: number) => string {
    const resolvedScores = scores
        .map(resolveScorePercentage)
        .filter((scorePercentage) => scorePercentage >= 0);

    if (resolvedScores.length === 0) {
        return () => "#d6dee8";
    }

    const minScore = Math.min(...resolvedScores);
    const maxScore = Math.max(...resolvedScores);
    const scoreRange = maxScore - minScore;

    return (score: number) => {
        const scorePercentage = resolveScorePercentage(score);

        if (scorePercentage < 0) {
            return "#d6dee8";
        }

        if (scoreRange === 0) {
            return normalizedScoreToColor(1);
        }

        return normalizedScoreToColor((scorePercentage - minScore) / scoreRange);
    };
}

export const SCORE_LEGEND = [
    { labelKey: "map.legend.highest", normalizedScore: 1 },
    { labelKey: "map.legend.high", normalizedScore: 0.75 },
    { labelKey: "map.legend.middle", normalizedScore: 0.5 },
    { labelKey: "map.legend.low", normalizedScore: 0.25 },
    { labelKey: "map.legend.lowest", normalizedScore: 0 },
] as const;
