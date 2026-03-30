export function scoreToColor(score: number): string {
    if (score > 90) {
        return "#109146";
    }
    if (score > 70) {
        return "#7cba43";
    }
    if (score > 60) {
        return "#ffcc06";
    }
    if (score > 50) {
        return "#f58e1d";
    }
    if (score >= 0) {
        return "#bf1e24";
    }
    return "#d6dee8";
}

export const SCORE_LEGEND = [
    { labelKey: "map.legend.excellent", score: 100 },
    { labelKey: "map.legend.good", score: 80 },
    { labelKey: "map.legend.fair", score: 65 },
    { labelKey: "map.legend.uncertain", score: 55 },
    { labelKey: "map.legend.poor", score: 30 },
] as const;
