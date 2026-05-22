import { useEffect, useState } from "react";

import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
    Stack,
    Typography,
} from "@mui/material";

import {
    clearStoredBaseLogLevel,
    createLogger,
    getBaseLogLevel,
    setBaseLogLevel,
    type LogLevel,
} from "@/shared/lib";
import {
    appConfiguration,
    type RecommendationApiVersion,
} from "@/shared/configuration";
import { useAppConfigContext } from "@/shared/context";

const debugLogger = createLogger({ scope: "DebugToolsModal" });
const LOG_LEVEL_OPTIONS: LogLevel[] = [
    "trace",
    "debug",
    "info",
    "warn",
    "error",
    "silent",
];
const RECOMMENDATION_API_VERSION_OPTIONS: RecommendationApiVersion[] = ["v1", "v2", "v3"];

function isDebugShortcut(event: KeyboardEvent): boolean {
    return (
        event.ctrlKey &&
        event.shiftKey &&
        !event.altKey &&
        !event.metaKey &&
        event.code === "KeyY"
    );
}

export function DebugToolsModal() {
    const {
        config,
        resetRecommendationApiVersion,
        setRecommendationApiVersion,
    } = useAppConfigContext();
    const [open, setOpen] = useState(false);
    const [selectedLogLevel, setSelectedLogLevel] = useState<LogLevel>(() =>
        getBaseLogLevel(),
    );
    const [selectedRecommendationApiVersion, setSelectedRecommendationApiVersion] =
        useState<RecommendationApiVersion>(config.recommendationApiVersion);

    useEffect(() => {
        const onKeyDown = (event: KeyboardEvent) => {
            if (!isDebugShortcut(event)) {
                return;
            }

            event.preventDefault();
            event.stopPropagation();
            setOpen((previous) => !previous);
        };

        document.addEventListener("keydown", onKeyDown, true);

        return () => {
            document.removeEventListener("keydown", onKeyDown, true);
        };
    }, []);

    useEffect(() => {
        if (!open) {
            return;
        }

        setSelectedLogLevel(getBaseLogLevel());
        setSelectedRecommendationApiVersion(config.recommendationApiVersion);
    }, [config.recommendationApiVersion, open]);

    return (
        <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="xs">
            <DialogTitle>Debug Tools</DialogTitle>
            <DialogContent>
                <Stack spacing={2} sx={{ pt: 0.5 }}>
                    <Typography variant="body2" color="text.secondary">
                        Open with Ctrl + Shift + Y. Settings are stored in local storage.
                    </Typography>

                    <FormControl fullWidth>
                        <InputLabel id="debug-log-level-label">Log level</InputLabel>
                        <Select
                            labelId="debug-log-level-label"
                            label="Log level"
                            value={selectedLogLevel}
                            onChange={(event) =>
                                setSelectedLogLevel(event.target.value as LogLevel)
                            }
                        >
                            {LOG_LEVEL_OPTIONS.map((level) => (
                                <MenuItem key={level} value={level}>
                                    {level}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <FormControl fullWidth>
                        <InputLabel id="debug-recommendation-api-version-label">
                            Recommendation API version
                        </InputLabel>
                        <Select
                            labelId="debug-recommendation-api-version-label"
                            label="Recommendation API version"
                            value={selectedRecommendationApiVersion}
                            onChange={(event) =>
                                setSelectedRecommendationApiVersion(
                                    event.target.value as RecommendationApiVersion,
                                )
                            }
                        >
                            {RECOMMENDATION_API_VERSION_OPTIONS.map((version) => (
                                <MenuItem key={version} value={version}>
                                    {version}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Stack>
            </DialogContent>
            <DialogActions>
                <Button
                    onClick={() => {
                        clearStoredBaseLogLevel();
                        resetRecommendationApiVersion();
                        const baseLevel = getBaseLogLevel();
                        setSelectedLogLevel(baseLevel);
                        setSelectedRecommendationApiVersion(
                            appConfiguration.recommendationApiVersion,
                        );
                        debugLogger.info("Reset base log level", { baseLevel });
                    }}
                >
                    Reset
                </Button>
                <Button onClick={() => setOpen(false)}>Close</Button>
                <Button
                    variant="contained"
                    onClick={() => {
                        setBaseLogLevel(selectedLogLevel);
                        setRecommendationApiVersion(selectedRecommendationApiVersion);
                        debugLogger.info("Updated base log level", {
                            level: selectedLogLevel,
                        });
                        debugLogger.info("Updated recommendation API version", {
                            version: selectedRecommendationApiVersion,
                        });
                        setOpen(false);
                    }}
                >
                    Apply
                </Button>
            </DialogActions>
        </Dialog>
    );
}
