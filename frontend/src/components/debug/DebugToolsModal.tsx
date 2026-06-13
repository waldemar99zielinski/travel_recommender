import { useCallback, useEffect, useState } from "react";

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
import { useAppConfigContext, useSessionContext } from "@/shared/context";
import { sessionVersions, type SessionVersion } from "@/models/session.models";

const debugLogger = createLogger({ scope: "DebugToolsModal" });
const LOG_LEVEL_OPTIONS: LogLevel[] = [
    "trace",
    "debug",
    "info",
    "warn",
    "error",
    "silent",
];
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
    } = useAppConfigContext();
    const [open, setOpen] = useState(false);
    const [baseLogLevel, setBaseLogLevelState] = useState<LogLevel>(getBaseLogLevel);
    const {
        forcedSessionVersion,
        setForcedSessionVersion,
    } = useSessionContext();

    useEffect(() => {
        const onKeyDown = (event: KeyboardEvent) => {
            if (!isDebugShortcut(event)) {
                return;
            }

            event.preventDefault();
            event.stopPropagation();
            if (open) {
                setOpen(false);
                return;
            }

            setOpen(true);
        };

        document.addEventListener("keydown", onKeyDown, true);

        return () => {
            document.removeEventListener("keydown", onKeyDown, true);
        };
    }, [open]);

    const handleLogLevelChange = useCallback((level: LogLevel) => {
        setBaseLogLevel(level);
        setBaseLogLevelState(level);
    }, []);

    const handleSessionVersionChange = useCallback(
        (value: string) => {
            const version = value === "" ? null : (value as SessionVersion);
            setForcedSessionVersion(version);
        },
        [setForcedSessionVersion],
    );

    const handleReset = useCallback(() => {
        clearStoredBaseLogLevel();
        setForcedSessionVersion(null);
        const defaultLevel = getBaseLogLevel();
        setBaseLogLevelState(defaultLevel);
        debugLogger.info("Reset base log level", { baseLevel: defaultLevel });
    }, [setForcedSessionVersion]);

    return (
        <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="xs">
            <DialogTitle>Debug Tools</DialogTitle>
            <DialogContent>
                <Stack spacing={2} sx={{ pt: 0.5 }}>
                    <Typography variant="body2" color="text.secondary">
                        Application version {config.version}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Open with Ctrl + Shift + Y. Settings are stored in local storage.
                    </Typography>

                    <FormControl fullWidth>
                        <InputLabel id="debug-log-level-label">Log level</InputLabel>
                        <Select
                            labelId="debug-log-level-label"
                            label="Log level"
                            value={baseLogLevel}
                            onChange={(event) =>
                                handleLogLevelChange(event.target.value as LogLevel)
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
                        <InputLabel id="debug-forced-session-version-label">
                            Forced Session Version
                        </InputLabel>
                        <Select
                            labelId="debug-forced-session-version-label"
                            label="Forced Session Version"
                            value={forcedSessionVersion ?? ""}
                            onChange={(event) =>
                                handleSessionVersionChange(event.target.value)
                            }
                        >
                            <MenuItem key={""} value={""}>
                                {"null"}
                            </MenuItem>
                            {sessionVersions.map((version) => (
                                <MenuItem key={version} value={version}>
                                    {version}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Stack>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleReset}>
                    Reset
                </Button>
                <Button onClick={() => setOpen(false)}>Close</Button>
            </DialogActions>
        </Dialog>
    );
}
